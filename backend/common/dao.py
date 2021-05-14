import sqlite3
from datetime import date
from sqlite3 import Connection
from typing import List
from .models import Transaction, TransactionCategory, Category


class Dao:

    @staticmethod
    def get_transactions(start_date: date, end_date: date, db_connection: Connection) -> List[Transaction]:
        # db_connection = sqlite3.connect(db_file_path)
        cursor = db_connection.cursor()

        db_results = cursor.execute(
            '''
            SELECT t.id, 
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
              ON t.id = tc.transaction_id 
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
                        'id': row[0],
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
    def get_transaction(id: str, db_connection: Connection) -> Transaction:
        cursor = db_connection.cursor()

        db_result = cursor.execute(
            '''
            SELECT t.id, 
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
              ON t.id = tc.transaction_id 
            LEFT JOIN category c 
              ON tc.category_id = c.id 
            WHERE t.id = ?
            ORDER BY t.date DESC
            ''',
            (id,)
        ).fetchone()

        return Transaction.from_dict(
            **{
                'id': db_result[0],
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
    def transaction_exists(internal_id: str, db_connection: Connection) -> bool:
        cursor = db_connection.cursor()

        # Query the database to find out if a record with this internal_id exists already.
        db_result = cursor.execute(
            'SELECT count(*) FROM transactions WHERE internal_id = ?',
            (internal_id,)
        ).fetchone()

        return db_result[0] != 0

    @staticmethod
    def save_transaction(transaction: Transaction, db_connection: Connection) -> int:
        cursor = db_connection.cursor()

        # Query the database to find out if a record with this id exists already.
        cursor.execute(
            'SELECT count(*) FROM transactions WHERE id = ?',
            (transaction.id,)
        )

        # If a record with the id already exists, UPDATE it.  Otherwise, INSERT a new record.
        db_result = cursor.fetchone()
        if db_result[0] == 0:
            cursor.execute(
                'INSERT INTO transactions (id, payee, type, date, amount, institution_id, memo, sic, mcc, checknum, internal_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (transaction.id, transaction.payee, None, transaction.date, transaction.amount, 'USAA', None,
                 None, None, None, transaction.internal_id,)
            )
        else:
            cursor.execute(
                'UPDATE transactions '
                '    SET payee = ?, type = ?, date =?, amount = ?, institution_id = ?, memo = ?, sic = ?, mcc = ?, checknum = ?, internal_id = ? '
                '    WHERE id = ?',
                (transaction.payee, None, transaction.date, transaction.amount, 'USAA', None, None, None, None, transaction.internal_id,
                 transaction.id,)
            )

        db_connection.commit()

        last_rowid: int = cursor.execute(
            'SELECT last_insert_rowid()'
        ).fetchone()

        return last_rowid[0]

    @staticmethod
    def save_transaction_category(transaction_category: TransactionCategory, db_connection: Connection) -> None:
        cursor = db_connection.cursor()

        # Turn foreign keys on in SQLite database.
        cursor.execute('PRAGMA foreign_keys = ON')

        cursor.execute(
            'INSERT INTO transaction_categories (category_id, transaction_id, amount) VALUES (?, ?, ?)',
            (transaction_category.category_id, transaction_category.transaction_id,
             transaction_category.amount,)
        )

        db_connection.commit()

    # @staticmethod
    # def update_transaction_category(transaction_category: TransactionCategory, db_file_path: str) -> None:
    #     db_connection = sqlite3.connect(db_file_path)
    #     cursor = db_connection.cursor()
    #
    #     # Turn foreign keys on in SQLite database.
    #     cursor.execute('PRAGMA foreign_keys = ON')
    #
    #     cursor.execute(
    #         'UPDATE transaction_categories '
    #         'SET category_id = ?, '
    #         '    amount = ? '
    #         'WHERE id = ?',
    #         (transaction_category.category_id, transaction_category.amount, transaction_category.id,)
    #     )
    #
    #     db_connection.commit()

    @staticmethod
    def delete_transaction_category(id: int, db_connection: Connection) -> None:
        cursor = db_connection.cursor()

        # Turn foreign keys on in SQLite database.
        cursor.execute('PRAGMA foreign_keys = ON')

        cursor.execute(
            '''
            DELETE 
            FROM transaction_categories
            WHERE id = ?
            ''',
            (id,)
        )

        db_connection.commit()

    @staticmethod
    def get_transaction_category_amount(transaction_category_id: int, db_connection: Connection) -> int:
        cursor = db_connection.cursor()

        db_result = cursor.execute(
            '''
            SELECT SUM(amount)
            FROM transaction_categories
            WHERE id = ?
            ''',
            (transaction_category_id,)
        ).fetchone()

        return db_result[0]

    @staticmethod
    def save_category(category: Category, db_connection: Connection) -> None:
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
    def delete_category(category_id: int, db_connection: Connection) -> None:
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
    def get_categories(db_connection: Connection) -> List[Category]:
        cursor = db_connection.cursor()

        db_results = cursor.execute(
            '''
            SELECT id, name
            FROM category
            ORDER BY name ASC
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
