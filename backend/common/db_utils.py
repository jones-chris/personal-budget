import functools
import sqlite3
from common.config import get_config


def manage_database_connection(target_func) -> ():

    config: dict = get_config()
    db_file_path: str = config['sqlite_db_file_path']

    @functools.wraps(target_func)
    def wrapper(*args, **kwargs):
        db_connection = sqlite3.connect(db_file_path)

        try:
            response = target_func(db_connection, **kwargs)

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
