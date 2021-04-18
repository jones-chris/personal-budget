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
            'SELECT internal_id, payee, type, amount, institution_id, memo, sic, mcc, checknum, date '
            'FROM transactions '
            'WHERE date BETWEEN ? and ? '
            'ORDER BY date DESC',
            (start_date.strftime('%m/%d/%Y'), end_date.strftime('%m/%d/%Y'),)
        ).fetchall()

        transactions: List[Transaction] = []
        for row in db_results:
            transactions.append(
                Transaction.from_dict(**{
                    'internal_id': row[0],
                    'payee': row[1],
                    'type': row[2],
                    'amount': row[3],
                    'institution_id': row[4],
                    'memo': row[5],
                    'sic': row[6],
                    'mcc': row[7],
                    'checknum': row[8],
                    'date': row[9]
                })
            )

        return transactions

    @staticmethod
    def get_transaction(internal_id: str, db_file_path: str) -> Transaction:
        db_connection = sqlite3.connect(db_file_path)
        cursor = db_connection.cursor()

        return cursor.execute(
            'SELECT internal_id, payee, type, amount, institution_id, memo, sic, mcc, checknum, date '
            'FROM transactions '
            'WHERE date internal_id = ?',
            (internal_id,)
        ).fetchone()

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
                (transaction.internal_id, transaction.payee, None, transaction.date, transaction.amount, 'USAA', None, None, None, None,)
            )
        else:
            cursor.execute(
                'UPDATE transactions '
                '    SET payee = ?, type = ?, date =?, amount = ?, institution_id = ?, memo = ?, sic = ?, mcc = ?, checknum = ? '
                '    WHERE internal_id = ?',
                (transaction.payee, None, transaction.date, transaction.amount, 'USAA', None, None, None, None, transaction.internal_id,)
            )

        db_connection.commit()

    @staticmethod
    def save_transaction_category(transaction_category: TransactionCategory, db_file_path: str) -> None:
        db_connection = sqlite3.connect(db_file_path)
        cursor = db_connection.cursor()

        cursor.execute(
            'SELECT count(*) FROM transaction_categories WHERE transaction_internal_id = ?',
            (transaction_category.transaction_internal_id,)
        )

        # Turn foreign keys on in SQLite database.
        cursor.execute('PRAGMA foreign_keys = ON')
        db_result = cursor.fetchone()
        if db_result[0] == 0:
            cursor.execute(
                'INSERT INTO transaction_categories (transaction_internal_id, category_id, amount) VALUES (?, ?, ?)',
                transaction_category.to_tuple()
            )
        else:
            cursor.execute(
                'UPDATE transaction_categories '
                'SET category_id = ?, '
                '    amount = ? '
                'WHERE id = ?',
                (transaction_category.category_id, transaction_category.amount, transaction_category.id,)
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
