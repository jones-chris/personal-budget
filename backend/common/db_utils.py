import sqlite3

from common.config import DB_FILE_PATH


def manage_database_connection(target_func) -> ():
    def wrapper():
        db_connection = sqlite3.connect(DB_FILE_PATH)

        try:
            response = target_func(db_connection)

            if db_connection.in_transaction:
                db_connection.commit()

            return response
        except Exception as e:
            print(e)

            if db_connection.in_transaction:
                db_connection.rollback()

            return {
                'message': f'{e}'
            }, 500

    return wrapper
