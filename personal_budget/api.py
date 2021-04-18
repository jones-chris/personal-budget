import datetime
import logging
from decimal import Decimal
from typing import List
from flask import Flask, request
from common.config import get_config
from common.dao import Dao
from personal_budget.common.models import Transaction, TransactionCategory, Category
from itertools import groupby

app = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

config: dict = get_config()
DB_FILE_PATH: str = config['sqlite_db_file_path']


@app.route('/transactions', methods=['GET'])
def get_transactions():
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')

    if start_date:
        start_date = datetime.datetime.strptime(start_date, '%m/%d/%Y').date()
    else:
        return {
            'message': 'startDate query parameter is null'
        }, 400

    if end_date:
        end_date = datetime.datetime.strptime(end_date, '%m/%d/%Y').date()
    else:
        end_date = datetime.date.today()

    transactions: List[Transaction] = Dao.get_transactions(start_date, end_date, DB_FILE_PATH)

    return {
        'transactions': [transaction.__dict__ for transaction in transactions]
    }, 200


@app.route('/transactions/category', methods=['POST'])
def update_transaction_category():
    request_body: List[dict] = request.get_json()
    transaction_categories: List[TransactionCategory] = [TransactionCategory(**transaction_category) for transaction_category in request_body]

    transaction_categories_grouped_by_internal_id = groupby(
        transaction_categories,
        lambda transaction: transaction.internal_id
    )

    for internal_id, transaction_categories in transaction_categories_grouped_by_internal_id:
        # Check that the total amount matches the transaction amount.
        transaction: Transaction = Dao.get_transaction(internal_id, DB_FILE_PATH)
        transaction_category_amount_total: Decimal = sum([transaction_category.amount for transaction_category in transaction_categories])
        if transaction.amount != transaction_category_amount_total:
            return {
                'message': 'The sum of the transaction categories must equal the transaction amount'
            }, 400

        for transaction_category in transaction_categories:
            Dao.save_transaction_category(transaction_category, DB_FILE_PATH)

    return 201


@app.route('/category', methods=['POST', 'PUT'])
def update_category():
    request_body: dict = request.get_json()
    try:
        category: Category = Category(**request_body)
    except KeyError:
        return 400

    Dao.save_category(category, DB_FILE_PATH)

    return 201


if __name__ == '__main__':
    app.run(
        host='localhost',
        port=5000,
        debug=True
    )
