import csv
import logging
import os
import shutil
import sqlite3
import time
from sqlite3 import Connection
import schedule

from config import Config
from dao import Dao
from models import Transaction, TransactionCategory

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def save_transaction(transaction: Transaction, db_connection: Connection) -> int:
    """Saves a Transaction to the database.  Returns the number of records created in the database; so 1 if a record was
    created in the database.  Otherwise 0."""
    # Check if the transaction already exists in the database.
    transaction_exists: bool = Dao.transaction_exists(transaction.internal_id, db_connection)

    # If not, then save the transaction and one transaction category associated with it.
    if not transaction_exists:
        generated_id: int = Dao.save_transaction(transaction, db_connection)

        transaction_category: TransactionCategory = TransactionCategory(
            **{
                'category_id': 1,
                'transaction_id': generated_id,
                'amount': transaction.amount
            }
        )

        Dao.save_transaction_category(transaction_category, db_connection)
        return 1
    else:
        return 0


def import_csv_files() -> None:
    logger.info('Inside import_csv_files')

    config: Config = Config()
    db_connection: Connection = sqlite3.connect(config.DB_FILE_PATH)

    try:
        for csv_import in config.csv_imports:
            # Get the directory for this CsvImport (ex:  transactions, investments, home value, etc).
            data_type_dir: str = config.get_data_type_dir(csv_import.data_type)
            csv_dir: str = f'{data_type_dir}/{csv_import.directory}'

            for file_name in os.listdir(csv_dir):
                if file_name.endswith('.csv'):

                    num_of_transactions_inserted: int = 0
                    logger.info(f'Importing {csv_dir}/{file_name}')

                    with open(f'{csv_dir}/{file_name}') as file_contents:
                        if csv_import.headers:
                            reader = csv.DictReader(
                                file_contents,
                                fieldnames=csv_import.headers
                            )
                        else:
                            reader = csv.DictReader(
                                file_contents
                            )

                        # Create a transaction for each row in the csv file.
                        for row in reader:
                            transaction: Transaction = Transaction.from_dict(
                                **{
                                    'payee': csv_import.map_payee(row),
                                    'type': None,
                                    'date': csv_import.map_date(row),
                                    'amount': csv_import.map_amount(row),
                                    'institution_id': csv_import.directory,
                                    'memo': None,
                                    'sic': None,
                                    'mcc': None,
                                    'checknum': None,
                                    'category_id': 1  # Default to the Uncategorized category.
                                }
                            )

                            records_inserted = save_transaction(transaction, db_connection)
                            num_of_transactions_inserted = num_of_transactions_inserted + records_inserted

                    logger.info(f'Inserted {num_of_transactions_inserted} transactions')

                    archive_dir: str = f'{csv_dir}/archived/{file_name}'
                    shutil.move(
                        src=f'{csv_dir}/{file_name}',
                        dst=archive_dir
                    )
                    logger.info(f'Moved file to {archive_dir}')

        db_connection.close()
        logger.info('Finished import_csv_files')
    except Exception as e:
        logger.error(e)
        db_connection.rollback()
        db_connection.close()


# Schedule the csv import task to run every minute.
schedule.every(1).minutes.do(import_csv_files)

while True:
    logger.info('Looking for csv files to import')
    schedule.run_pending()

    logger.info('Finished running csv import')
    time.sleep(1)
