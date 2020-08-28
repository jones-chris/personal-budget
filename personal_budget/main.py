import json
import logging
import os
from datetime import date
from decimal import Decimal
from typing import List

import personal_budget.ofxclient as ofxclient
import ofxparse
import socks

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
        self.institution_id: str = account.institution.org  # The partition key in dynamo.
        self.memo: str = transaction.memo
        self.sic: str = transaction.sic
        self.mcc: str = transaction.mcc
        self.checknum: str = transaction.checknum

    def to_dict(self):
        return {
            'internal_id': self.internal_id,
            'payee': self.payee,
            'type': self.type,
            'date': self.date.strftime('%Y-%m-%d'),
            'amount': self.amount,
            'institution_id': self.institution_id,
            'memo': self.memo,
            'sic': self.sic,
            'mcc': self.mcc,
            'checknum': self.checknum
        }


def create_institution(institution_name: str, username: str, password: str) -> ofxclient.Institution:
    if institution_name not in INSTITUTION_CONFIG.keys():
        raise ValueError(f'{institution_name} not found in INSTITUTION_CONFIG')

    institution_config = INSTITUTION_CONFIG[institution_name]

    return ofxclient.Institution(
        id=institution_config['id'],
        org=institution_config['org'],
        url=institution_config['ofx_url'],
        username=username,
        password=password,
        use_in_mem_string_buffer=False
    )


def lambda_handler(event, context) -> bool:
    logger.info('In lambda_handler')

    region_name = os.environ['REGION_NAME']
    institution_name = os.environ['INSTITUTION_NAME']
    usaa_creds_secret_name = os.environ['USAA_CREDS_SECRET_NAME']
    dynamo_table_name = os.environ['TRANSACTIONS_DYNAMO_TABLE_NAME']
    num_of_transaction_days = os.environ['NUM_OF_TRANSACTION_DAYS']

    # Get institution member id and password from Secrets Manager.
    logger.info('Retrieving secret')
    secret: str = socks.secretsmanager.get_secret(
        secret_name=usaa_creds_secret_name,
        region_name=region_name
    )
    secret: dict = json.loads(secret)
    institution_member_id = secret['member_id']
    password = secret['password']

    institution = create_institution(
        institution_name=institution_name,
        username=institution_member_id,
        password=password
    )

    # Get accounts, get transactions for those accounts, and save the transactions to the dynamo table.
    logger.info(F'Calling {institution.org} OFX API endpoint')
    accounts: List[ofxclient.account] = institution.accounts()

    logger.info(f'Retrieved {len(accounts)} accounts')

    if len(accounts) == 0:
        return False

    for account in accounts:
        transactions = account.transactions(
            days=int(num_of_transaction_days)
        )

        logger.info(f'Retrieved {len(transactions)} transactions for account {account.number}')

        for transaction in transactions:
            dynamo_transaction = Transaction(
                transaction=transaction,
                account=account
            )
            socks.dynamodb.add_item(
                table_name=dynamo_table_name,
                item=dynamo_transaction.to_dict(),
                region_name=region_name
            )

        logger.info(f'Finished saving transactions for account {account.number}')

    return True
