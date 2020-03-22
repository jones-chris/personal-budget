import base64
from datetime import datetime
import json
import logging
import os
from typing import Tuple
from dateutil.relativedelta import relativedelta

import boto3
import mintapi


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def get_secret(secret_name) -> Tuple[str, str]:
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager"
        # region_name=region_name,
        # config=Config(signature_version='s3v4')
    )

    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )

    # Decrypts secret using the associated KMS CMK.
    # Depending on whether the secret is a string or binary, one of these fields will be populated.
    if 'SecretString' in get_secret_value_response:
        secret_string = get_secret_value_response['SecretString']
    else:
        secret_string = base64.b64decode(get_secret_value_response['SecretBinary'])

    secret_dict = json.loads(secret_string)

    return secret_dict['email'], secret_dict['password']


def lambda_handler(event, context):
    logger.info('In lambda_handler')

    secret_name = os.environ['MINT_SECRET_NAME']

    logger.info('Retrieving secret')
    email, password = get_secret(secret_name)

    logger.info('Logging into Mint')
    mint = mintapi.Mint(
        email=email,
        password=password,
        mfa_method='sms',
        headless=True,  # Whether the chromedriver should work without opening a visible window (useful for server-side deployments)
    )
    logger.info('Successfully logged into Mint')

    tmp_dir = '/tmp'
    today = datetime.today()
    current_month_start_date = today.replace(day=1)
    current_month_file_name = f'{current_month_start_date.month}_{current_month_start_date.year}.csv'
    logger.info(f'today is {str(today)} '
                f'current_month_start_date is {str(current_month_start_date)} '
                f'current_month_file_name is {current_month_file_name} ')

    # Get current month transactions.
    logger.info('Retrieving current month transactions')
    current_month_transactions = mint.get_detailed_transactions(
        include_investment=False,
        skip_duplicates=True,
        remove_pending=True,
        start_date=current_month_start_date.strftime('%m/%d/%y')
    )

    logger.info(f'Successfully retrieved current month transactions.  Writing data to {current_month_file_name}')
    current_month_transactions.to_csv(path_or_buf=f'{tmp_dir}/{current_month_file_name}')

    # Get last month's transactions.
    last_month_start_date = current_month_start_date - relativedelta(months=1)
    last_month_end_date = current_month_start_date - relativedelta(days=1)
    last_month_file_name = f'{last_month_start_date.month}_{last_month_start_date.year}.csv'
    logger.info(f'last_month_start_date is {str(last_month_start_date)} '
                f'last_month_end_date is {str(last_month_end_date)} '
                f'last_month_file_name is {last_month_file_name} ')

    logger.info('Retrieving last month transactions')
    last_month_transactions = mint.get_detailed_transactions(
        include_investment=False,
        skip_duplicates=True,
        remove_pending=True,
        start_date=last_month_start_date.strftime('%m/%d/%y')
    )

    # Filter out all transactions that are outside lsat_month_end_date.
    is_before_end_date = last_month_transactions['odate'] <= last_month_end_date.strftime('%m/%d/%y')
    last_month_transactions = last_month_transactions[is_before_end_date]

    logger.info(f'Successfully retrieved last month transactions and filtered the transactions.  Writing data to {last_month_file_name}.')
    last_month_transactions.to_csv(path_or_buf=f'{tmp_dir}/{last_month_file_name}')

    # Send transaction files to S3.
    logger.info('Uploading files to S3')
    s3_transactions_bucket = os.environ['TRANSACTIONS_BUCKET']
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(
        Filename=f'{tmp_dir}/{current_month_file_name}',
        Bucket=s3_transactions_bucket,
        Key=current_month_file_name
    )
    logger.info('Successfully uploaded current month''s file')
    s3.meta.client.upload_file(
        Filename=f'{tmp_dir}/{last_month_file_name}',
        Bucket=s3_transactions_bucket,
        Key=last_month_file_name
    )
    logger.info('Successfully uploaded last month''s file')
