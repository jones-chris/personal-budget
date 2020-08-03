import json
import logging
import os
from typing import List

import ofxclient
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
        self.internal_id = f'{account.institution.org}.{account.number}.{transaction.id}'
        self.payee = transaction.payee
        self.type = transaction.type
        self.date = transaction.date
        self.amount = transaction.amount
        self.institution_id = transaction.id
        self.memo = transaction.memo
        self.sic = transaction.sic
        self.mcc = transaction.mcc
        self.checknum = transaction.checknum


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


def lambda_handler(event, context) -> int:
    logger.info('In lambda_handler')

    region_name = os.environ['REGION_NAME']
    institution_name = os.environ['INSTITUTION_NAME']
    usaa_creds_secret_name = os.environ.get('USAA_CREDS_SECRET_NAME')
    dynamo_table_name = os.environ.get('TRANSACTIONS_DYNAMO_TABLE_NAME')

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
        exit(1)

    for account in accounts:
        transactions = account.transactions(days=10)
        logger.info(f'Retrieved {len(transactions)} transactions for account {account.number}')

        for transaction in transactions:
            dynamo_transaction = Transaction(**transaction.__dict__)
            socks.dynamodb.add_item(
                table_name=dynamo_table_name,
                item=dynamo_transaction,
                region_name=region_name
            )

        logger.info(f'Finished saving transactions for account {account.number}')

    exit(0)
