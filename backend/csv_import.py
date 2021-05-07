import csv
import logging
import os
from typing import List

from common.config import get_config
from common.dao import Dao
from common.models import Transaction, TransactionCategory

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def main() -> None:
    config: dict = get_config()
    DB_FILE_PATH: str = config['sqlite_db_file_path']

    # Get number of days of transactions to retrieve.
    transaction_directory: str = config['transaction_directory']

    for file_name in os.listdir(transaction_directory):
        if file_name.endswith('.csv'):
            with open(f'{transaction_directory}/{file_name}') as file_contents:
                # Get transactions csv file field names from config.
                fieldnames: List[str] = config['import']['csv']['transactions']['headers']

                reader = csv.DictReader(
                    file_contents,
                    fieldnames=fieldnames
                )

                # Create a transaction for each row in the csv file.
                for row in reader:
                    transaction: Transaction = Transaction.from_dict(
                        **{
                            'payee': row['description'],
                            'type': None,
                            'date': row['date'],
                            'amount': row['amount'].replace('--', ''),
                            'institution_id': 'USAA',
                            'memo': None,
                            'sic': None,
                            'mcc': None,
                            'checknum': None,
                            'category_id': 1  # Default to the Uncategorized category.
                        }
                    )

                    # Check if the transaction already exists in the database.
                    transaction_exists: bool = Dao.transaction_exists(transaction.internal_id, DB_FILE_PATH)

                    # If not, then save the transaction and one transaction category associated with it.
                    if not transaction_exists:
                        generated_id: int = Dao.save_transaction(transaction, DB_FILE_PATH)

                        transaction_category: TransactionCategory = TransactionCategory(
                            **{
                                'category_id': 1,
                                'transaction_id': generated_id,
                                'amount': transaction.amount
                            }
                        )

                        Dao.save_transaction_category(transaction_category, DB_FILE_PATH)


if __name__ == '__main__':
    main()
