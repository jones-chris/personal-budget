import datetime
import logging
import sqlite3
from decimal import Decimal
from sqlite3 import Connection
from typing import List, Union, Dict, AnyStr, Tuple

from flask import Flask, request, jsonify, Response, g, render_template
from flask_cors import CORS

import report_generator as report_generator
import config as config
import dao as dao
import models as models

app = Flask(__name__, static_url_path='/', static_folder='../ui/build', template_folder='../ui/build')
CORS(app)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

app_context: config.Config = config.Config()
DB_FILE_PATH: str = app_context.DB_FILE_PATH

# Note:
# The @app.route `endpoint` parameter is needed in order to prevent a Flask AssertionError.  See Solution #3 in this link:
# https://izziswift.com/assertionerror-view-function-mapping-is-overwriting-an-existing-endpoint-function-main/


@app.route('/', methods=['GET'], endpoint='serve_ui')
def serve_ui():
    return render_template('index.html')


@app.route('/transactions', methods=['GET'], endpoint='get_transactions')
def get_transactions() -> tuple:
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')

    if start_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        return {
            'message': 'startDate query parameter is null'
        }, 400

    if end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = datetime.date.today()

    db_connection: Connection = get_database_connection()
    transactions: List[models.Transaction] = dao.Dao.get_transactions(start_date, end_date, db_connection)

    return {
        'transactions': [transaction.__dict__ for transaction in transactions]
    }, 200


@app.route('/transaction/category', methods=['POST'], endpoint='create_transaction_categories')
def create_transaction_categories() -> Union[int, tuple]:
    request_body: List[dict] = request.get_json()
    transaction_categories: List[models.TransactionCategory] = [models.TransactionCategory(**transaction_category) for transaction_category in request_body]

    transaction_categories_grouped_by_id: Dict[str, List[
        models.TransactionCategory]] = _group_transaction_categories_by_id(transaction_categories)

    db_connection: Connection = get_database_connection()
    for transaction_id in transaction_categories_grouped_by_id.keys():
        # Check that the total amount matches the transaction amount.
        transaction: models.Transaction = dao.Dao.get_transaction(transaction_id, db_connection)
        transaction_categories: List[models.TransactionCategory] = transaction_categories_grouped_by_id[transaction_id]
        transaction_category_amount_total: Decimal = sum([transaction_category.amount for transaction_category in transaction_categories])
        if transaction.amount != transaction_category_amount_total:
            return {
                'message': f'The sum of the transaction categories, {transaction_category_amount_total}, must equal the transaction amount, {transaction.amount}'
            }, 400

        for transaction_category in transaction_categories:
            dao.Dao.save_transaction_category(transaction_category, db_connection)

    return {}, 200


@app.route('/transaction/category/<transaction_category_id>', methods=['PUT'], endpoint='update_category_transaction')
def update_category_transaction(transaction_category_id: int) -> tuple:
    request_body: dict = request.get_json()

    transaction_categories: List[models.TransactionCategory] = []
    for dictionary in request_body:
        transaction_categories.append(
            models.TransactionCategory(**dictionary)
        )

    db_connection: Connection = get_database_connection()
    transaction_category_amount: int = dao.Dao.get_transaction_category_amount(transaction_category_id, db_connection)
    transaction_category_amount_total: Decimal = round(sum([transaction_category.amount for transaction_category in transaction_categories]), 2)
    if transaction_category_amount != transaction_category_amount_total:
        return {
                   'message': f'The sum of the transaction categories, {transaction_category_amount_total}, must equal the '
                              f'transaction category amount, {transaction_category_amount}'
               }, 400

    dao.Dao.delete_transaction_category(transaction_category_id, db_connection)
    for transaction_category in transaction_categories:
        dao.Dao.save_transaction_category(transaction_category, db_connection)

    return {}, 200


@app.route('/category', methods=['POST', 'PUT'], endpoint='update_category')
def update_category() -> tuple:
    request_body: dict = request.get_json()
    try:
        category: models.Category = models.Category(**request_body)
    except KeyError:
        return {}, 400

    db_connection: Connection = get_database_connection()
    dao.Dao.save_category(category, db_connection)

    return {}, 201


@app.route('/categories', methods=['GET'], endpoint='get_categories')
def get_categories() -> tuple:
    db_connection: Connection = get_database_connection()
    categories: List[models.Category] = dao.Dao.get_categories(db_connection)

    return jsonify([category.__dict__ for category in categories])


@app.route('/category', methods=['DELETE'], endpoint='delete_category')
def delete_category() -> tuple:
    request_body: dict = request.get_json()
    category_id = request_body['id']

    db_connection: Connection = get_database_connection()
    dao.Dao.delete_category(category_id, db_connection)

    return {}, 200


@app.route('/report/<report_name>', methods=['GET'], endpoint='get_report')
def get_report(report_name: str) -> Union[Tuple[AnyStr, int], Tuple[Dict[str, str], int]]:
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')

    if start_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        return {
            'message': 'startDate query parameter is null'
        }, 400

    if end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = datetime.date.today()

    db_connection: Connection = get_database_connection()
    report_temp_file: AnyStr = report_generator.ReportGenerator(db_connection).to_stream(start_date, end_date, report_name)
    return Response(
        report_temp_file,
        headers={
            'Content-Disposition': 'attachment; filename=sheet.xlsx',
            'Content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
    )


@app.route('/reports', methods=['GET'], endpoint='get_reports')
def get_reports() -> tuple:
    return jsonify([report.__dict__ for report in app_context.reports])


@app.teardown_request
def close_db_transaction_and_connection(error):
    """Closes the database again at the end of the request."""
    if error:
        logger.error(error)

        if hasattr(g, 'database_connection'):
            g.database_connection.rollback()
            g.database_connection.close()
    else:
        if hasattr(g, 'database_connection'):
            g.database_connection.commit()
            g.database_connection.close()


def get_database_connection():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'database_connection'):
        db_file_path: str = app_context.DB_FILE_PATH
        g.database_connection = sqlite3.connect(db_file_path)

    return g.database_connection


def _group_transaction_categories_by_id(transaction_categories: List[models.TransactionCategory]) -> Dict[str, List[
    models.TransactionCategory]]:
    grouped_transaction_categories: Dict[str, List[models.TransactionCategory]] = {}
    for transaction_category in transaction_categories:
        if transaction_category.transaction_id in grouped_transaction_categories.keys():
            grouped_transaction_categories[transaction_category.transaction_id].append(transaction_category)
        else:
            grouped_transaction_categories[transaction_category.transaction_id] = [transaction_category]

    return grouped_transaction_categories


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
else:
    app
