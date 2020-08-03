import os

if __name__ == '__main__':
    os.environ['REGION_NAME'] = 'us-east-1'
    os.environ['INSTITUTION_NAME'] = 'USAA'
    os.environ['USAA_CREDS_SECRET_NAME'] = 'usaa/creds'
    os.environ['TRANSACTIONS_DYNAMO_TABLE_NAME'] = 'prod-persona-budget-transactions'

    from personal_budget import main
    main.lambda_handler({}, [])
