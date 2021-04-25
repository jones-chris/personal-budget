import sqlite3
from datetime import date
from typing import List
from common.models import Transaction, TransactionCategory, Category


class Dao:

    @staticmethod
    def get_transactions(start_date: date, end_date: date, db_file_path: str) -> List[Transaction]:
        db_connection = sqlite3.connect(db_file_path)
        cursor = db_connection.cursor()

        db_results = cursor.execute(
            '''
            SELECT t.internal_id, 
                   t.payee, 
                   t.type, 
                   tc.amount,
                   t.institution_id, 
                   t.memo, 
                   t.sic, 
                   t.mcc, 
                   t.checknum, 
                   t.date, 
                   c.id AS category,
                   tc.id AS transaction_category_id,
                   t.amount AS total_amount
            FROM transactions t 
            LEFT JOIN transaction_categories tc 
              ON t.internal_id = tc.transaction_internal_id 
            LEFT JOIN category c 
              ON tc.category_id = c.id 
            WHERE t.date BETWEEN ? and ? 
            ORDER BY t.date DESC
            ''',
            (start_date.strftime('%m/%d/%Y'), end_date.strftime('%m/%d/%Y'),)
        ).fetchall()

        transactions: List[Transaction] = []
        for row in db_results:
            transactions.append(
                Transaction.from_dict(
                    **{
                        'internal_id': row[0],
                        'payee': row[1],
                        'type': row[2],
                        'amount': row[3],
                        'institution_id': row[4],
                        'memo': row[5],
                        'sic': row[6],
                        'mcc': row[7],
                        'checknum': row[8],
                        'date': row[9],
                        'category_id': row[10],
                        'transaction_category_id': row[11],
                        'transaction_amount': row[12]
                    }
                )
            )

        return transactions

    @staticmethod
    def get_transaction(internal_id: str, db_file_path: str) -> Transaction:
        db_connection = sqlite3.connect(db_file_path)
        cursor = db_connection.cursor()

        db_result = cursor.execute(
            '''
            SELECT t.internal_id, 
                   t.payee, 
                   t.type, 
                   tc.amount,
                   t.institution_id, 
                   t.memo, 
                   t.sic, 
                   t.mcc, 
                   t.checknum, 
                   t.date, 
                   c.id AS category,
                   tc.id AS transaction_category_id,
                   t.amount AS total_amount
            FROM transactions t 
            LEFT JOIN transaction_categories tc 
              ON t.internal_id = tc.transaction_internal_id 
            LEFT JOIN category c 
              ON tc.category_id = c.id 
            WHERE t.internal_id = ?
            ORDER BY t.date DESC
            ''',
            (internal_id,)
        ).fetchone()

        return Transaction.from_dict(
            **{
                'internal_id': db_result[0],
                'payee': db_result[1],
                'type': db_result[2],
                'amount': db_result[3],
                'institution_id': db_result[4],
                'memo': db_result[5],
                'sic': db_result[6],
                'mcc': db_result[7],
                'checknum': db_result[8],
                'date': db_result[9],
                'category_id': db_result[10],
                'transaction_category_id': db_result[11]
            }
        )

    @staticmethod
    def save_transaction(transaction: Transaction, db_file_path: str) -> None:
        db_connection = sqlite3.connect(db_file_path)
        cursor = db_connection.cursor()

        # Query the database to find out if a record with this internal_id exists already.
        cursor.execute(
            'SELECT count(*) FROM transactions WHERE internal_id = ?',
            (transaction.internal_id,)
        )

        # If a record with the internal_id already exists, UPDATE it.  Otherwise, INSERT a new record.
        db_result = cursor.fetchone()
        if db_result[0] == 0:
            cursor.execute(
                'INSERT INTO transactions (internal_id, payee, type, date, amount, institution_id, memo, sic, mcc, checknum)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (transaction.internal_id, transaction.payee, None, transaction.date, transaction.amount, 'USAA', None,
                 None, None, None,)
            )
        else:
            cursor.execute(
                'UPDATE transactions '
                '    SET payee = ?, type = ?, date =?, amount = ?, institution_id = ?, memo = ?, sic = ?, mcc = ?, checknum = ? '
                '    WHERE internal_id = ?',
                (transaction.payee, None, transaction.date, transaction.amount, 'USAA', None, None, None, None,
                 transaction.internal_id,)
            )

        db_connection.commit()

    @staticmethod
    def save_transaction_category(transaction_category: TransactionCategory, db_file_path: str) -> None:
        db_connection = sqlite3.connect(db_file_path)
        cursor = db_connection.cursor()

        # cursor.execute(
        #     'SELECT count(*) FROM transaction_categories WHERE transaction_internal_id = ?',
        #     (transaction_category.transaction_internal_id,)
        # )
        # db_result = cursor.fetchone()
        #
        # # Turn foreign keys on in SQLite database.
        cursor.execute('PRAGMA foreign_keys = ON')

        # If the transaction category already exists, then update it.  Otherwise, insert a new record.
        if transaction_category.id:
            cursor.execute(
                'UPDATE transaction_categories '
                'SET category_id = ?, '
                '    amount = ? '
                'WHERE id = ?',
                (transaction_category.category_id, transaction_category.amount, transaction_category.id,)
            )
        else:
            cursor.execute(
                'INSERT INTO transaction_categories (category_id, transaction_internal_id, amount) VALUES (?, ?, ?)',
                (transaction_category.category_id, transaction_category.transaction_internal_id,
                 transaction_category.amount,)
            )

        db_connection.commit()

    @staticmethod
    def save_category(category: Category, db_file_path: str) -> None:
        db_connection = sqlite3.connect(db_file_path)
        cursor = db_connection.cursor()

        # If the category has an id, then perform an UPDATE.
        if category.id:
            cursor.execute(
                'UPDATE category '
                'SET name = ? '
                'WHERE id = ?',
                (category.name, category.id,)
            )
        else:
            cursor.execute(
                'INSERT INTO category (name) VALUES (?)',
                (category.name,)
            )

        db_connection.commit()

    @staticmethod
    def delete_category(category_id: int, db_file_path: str) -> None:
        db_connection = sqlite3.connect(db_file_path)
        cursor = db_connection.cursor()

        cursor.execute(
            '''
            DELETE
            FROM category
            WHERE id = ?
            ''',
            (category_id,)
        )

        db_connection.commit()

    @staticmethod
    def get_categories(db_file_path: str) -> List[Category]:
        db_connection = sqlite3.connect(db_file_path)
        cursor = db_connection.cursor()

        db_results = cursor.execute(
            '''
            SELECT id, name
            FROM category
            '''
        ).fetchall()

        categories: List[Category] = []
        for row in db_results:
            categories.append(
                Category(
                    **{
                        'id': row[0],
                        'name': row[1]
                    }
                )
            )

        return categories
