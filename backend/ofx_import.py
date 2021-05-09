import json
import logging
import os
import sqlite3
import sys
from datetime import date
from decimal import Decimal
from typing import List

import ofxclient
import ofxparse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


INSTITUTION_CONFIG = {
    'USAA': {
        'id': '24591',
        'org': 'USAA',
        'ofx_url': 'https://service2.usaa.com/ofx/OFXServlet'
    }
}


class Transaction:
    """
    A Transaction object (not to be confused with an ofxclient.Transaction).
    """
    def __init__(self, transaction: ofxparse.Transaction, account: ofxclient.Account) -> None:
        self.internal_id: str = f'{account.institution.org}.{account.number}.{transaction.id}'
        self.payee: str = transaction.payee
        self.type: str = transaction.type
        self.date: date = transaction.date  # The sort key in dynamo.
        self.amount: Decimal = transaction.amount
        self.institution_id: str = account.institution.number  # The partition key in dynamo.
        self.memo: str = transaction.memo
        self.sic: str = transaction.sic
        self.mcc: str = transaction.mcc
        self.checknum: str = transaction.checknum

    def to_tuple(self):
        return (
            self.internal_id,
            self.payee,
            self.type,
            self.date.strftime('%Y-%m-%d'),
            self.amount,
            self.institution_id,
            self.memo,
            self.sic,
            self.mcc,
            self.checknum
        )


def create_institution(institution_name: str, username: str, password: str) -> ofxclient.Institution:
    if institution_name not in INSTITUTION_CONFIG.keys():
        raise ValueError(f'{institution_name} not found in INSTITUTION_CONFIG')

    institution_config = INSTITUTION_CONFIG[institution_name]

    return ofxclient.Institution(
        id=institution_config['id'],
        org=institution_config['org'],
        url=institution_config['ofx_url'],
        username=username,
        password=password
    )


def main() -> None:
    logger.info('In main')

    # Get configuration file.
    config_file_path = sys.argv[1]
    if not os.path.exists(config_file_path):
        logger.error('{config_file_path} does not exist')
        exit(1)

    root, extension = os.path.splitext(config_file_path)
    if extension.lower() != '.json':
        logger.error('{config_file_path} must be have a .json extension.  For example, /path/to/my_config.json')

    config = {}
    with open(config_file_path) as config_file:
        config = json.load(config_file)

    # Get number of days of transactions to retrieve.
    institution_name = config['institution_name']   
    member_id = config['member_id']
    password = config['password'] 
    num_of_transaction_days = config['number_of_transaction_days']
    sqlite_db_file_path = config['sqlite_db_file_path']

    institution = create_institution(
        institution_name=institution_name,
        username=member_id,
        password=password
    )

    # Get accounts, get transactions for those accounts, and save the transactions to the SQLite database.
    logger.info(F'Calling {institution.org} OFX API endpoint')
    accounts: List[ofxclient.account] = institution.accounts()

    logger.info(f'Retrieved {len(accounts)} accounts')

    if len(accounts) == 0:
        exit(0)

    # Create the database connection and cursor if there are accounts to iterate through, so we're not instantiating
    # them for each account.
    db_connection = sqlite3.connect(sqlite_db_file_path)
    cursor = db_connection.cursor()
    for account in accounts:
        transactions = account.transactions(days=int(num_of_transaction_days))
        logger.info(f'Retrieved {len(transactions)} transactions for account {account.number}')

        for transaction in transactions:
            cursor.execute('SELECT count(*) FROM transactions WHERE internal_id = ?', (transaction.internal_id,))
            
            # If a record with the internal_id already exists, UPDATE it.  Otherwise, INSERT a new record.
            row = cursor.fetchone()
            if row[0] == 0:
                cursor.execute(
                    'INSERT INTO transactions (internal_id, payee, type, date, amount, institution_id, memo, sic, mcc, checknum) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    transaction.to_tuple()
                )
            else:
                cursor.execute(
                    'UPDATE transactions '
                    '    SET payee = ?, type = ?, date =?, amount = ?, institution_id = ?, memo = ?, sic = ?, mcc = ?, checknum = ? '
                    '    WHERE internal_id = ?',
                    (transaction.payee, transaction.type, transaction.date, transaction.amount, transaction.institution_id, transaction.memo, transaction.sic, transaction.mcc, transaction.checknum, transaction.internal_id, )
                )

        logger.info(f'Finished saving transactions for account {account.number}')

    exit(0)


# Beginning of script
if __name__ == '__main__':
    main()
