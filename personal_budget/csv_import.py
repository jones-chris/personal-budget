import csv
import logging
import os
from common.config import get_config
from personal_budget.common.dao import Dao
from personal_budget.common.models import Transaction

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def main() -> None:
    # # Get configuration file.
    # config_file_path = sys.argv[1]
    # if not os.path.exists(config_file_path):
    #     logger.error('{config_file_path} does not exist')
    #     exit(1)
    #
    # root, extension = os.path.splitext(config_file_path)
    # if extension.lower() != '.json':
    #     logger.error('{config_file_path} must be have a .json extension.  For example, /path/to/my_config.json')
    #
    # config = {}
    # with open(config_file_path) as config_file:
    #     config = json.load(config_file)
    #
    # # Get number of days of transactions to retrieve.
    # transaction_directory: str = config['transaction_directory']
    # sqlite_db_file_path: str = config['sqlite_db_file_path']
    #
    # if not os.path.exists(transaction_directory):
    #     logger.error(f'{transaction_directory} does not exist')
    #     exit(1)

    config: dict = get_config()
    DB_FILE_PATH: str = config['sqlite_db_file_path']

    # Get number of days of transactions to retrieve.
    transaction_directory: str = config['transaction_directory']

    for file_name in os.listdir(transaction_directory):
        if file_name.endswith('.csv'):
            with open(f'{transaction_directory}/{file_name}') as file_contents:
                reader = csv.DictReader(
                    file_contents,
                    fieldnames=[
                        'posted', 'blank1', 'date', 'blank2', 'description', 'category', 'amount'
                    ])

                for row in reader:
                    internal_id: str = f"{row['date']}-{row['description']}-{row['amount']}"
                    date: date = row['date']

                    transaction: Transaction = Transaction.from_dict(
                        **{
                            'internal_id': internal_id,
                            'payee': row['description'],
                            'type': None,
                            'date': row['date'],
                            'amount': row['amount'].replace('--', ''),
                            'institution_id': 'USAA',
                            'memo': None,
                            'sic': None,
                            'mcc': None,
                            'checknum': None
                        }
                    )

                    Dao.save_transaction(transaction, DB_FILE_PATH)

            #         # Query the database to find out if a record with this internal_id exists already.
            #         cursor.execute('SELECT count(*) FROM transactions WHERE internal_id = ?',
            #                        (internal_id,))
            #
            #         # If a record with the internal_id already exists, UPDATE it.  Otherwise, INSERT a new record.
            #         results_record = cursor.fetchone()
            #         if results_record[0] == 0:
            #             cursor.execute(
            #                 'INSERT INTO transactions (internal_id, payee, type, date, amount, institution_id, memo, sic, mcc, checknum)'
            #                 ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            #                 (internal_id, description, None, date, amount, 'USAA', None, None, None, None,)
            #             )
            #         else:
            #             cursor.execute(
            #                 'UPDATE transactions '
            #                 '    SET payee = ?, type = ?, date =?, amount = ?, institution_id = ?, memo = ?, sic = ?, mcc = ?, checknum = ? '
            #                 '    WHERE internal_id = ?',
            #                 (description, None, date, amount, 'USAA', None, None, None, None, internal_id,)
            #             )
            #
            # db_connection.commit()


if __name__ == '__main__':
    main()
