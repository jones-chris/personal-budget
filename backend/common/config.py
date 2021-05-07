import json
import logging
import os
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def get_config() -> dict:
    # Get configuration file.
    CONFIG_DIR_FILE_PATH: str = sys.argv[1]
    DB_FILE_PATH: str = f'{CONFIG_DIR_FILE_PATH}/budget'
    CONFIG_JSON_FILE_PATH: str = f'{CONFIG_DIR_FILE_PATH}/config.json'
    TRANSACTIONS_DIR_FILE_PATH: str = f'{CONFIG_DIR_FILE_PATH}/transactions'
    REPORTS_DIR_FILE_PATH: str = f'{CONFIG_DIR_FILE_PATH}/report_templates'

    if not os.path.exists(CONFIG_DIR_FILE_PATH):
        logger.error(f'{CONFIG_DIR_FILE_PATH} does not exist')
        exit(1)

    # Check that the config file is a json file.
    root, extension = os.path.splitext(CONFIG_JSON_FILE_PATH)
    if extension.lower() != '.json':
        logger.error(f'{CONFIG_JSON_FILE_PATH} must be have a .json extension.  For example, config.json')

    # Check that the transaction directory exists.
    if not os.path.exists(TRANSACTIONS_DIR_FILE_PATH):
        logger.error(f'{TRANSACTIONS_DIR_FILE_PATH} does not exist')
        exit(1)

    if not os.path.exists(DB_FILE_PATH):
        logger.error(f'{DB_FILE_PATH} does not exist')
        exit(1)

    config: dict = {}
    with open(CONFIG_JSON_FILE_PATH) as config_file:
        config = json.load(config_file)
        config['sqlite_db_file_path'] = DB_FILE_PATH
        config['transaction_directory'] = TRANSACTIONS_DIR_FILE_PATH
        config['report_template_directory'] = REPORTS_DIR_FILE_PATH
        config['config_json_file_path'] = CONFIG_JSON_FILE_PATH

    return config  # todo:  consider making this a class rather than a dictionary.

    # todo:  the below code is for getting the config when running locally, not in a docker container.  Figure out how to
    # todo:  ...not have 2 different code blocks for running a docker container and running locally.
    # Get configuration file.
    # config_file_path = sys.argv[1]
    # if not os.path.exists(config_file_path):
    #     logger.error(f'{config_file_path} does not exist')
    #     exit(1)
    #
    # # Check that the config file is a json file.
    # root, extension = os.path.splitext(config_file_path)
    # if extension.lower() != '.json':
    #     logger.error(f'{config_file_path} must be have a .json extension.  For example, /path/to/my_config.json')
    #
    # config: dict = {}
    # with open(config_file_path) as config_file:
    #     config = json.load(config_file)
    #
    # # Various checks to make sure the config file contents are valid...
    # # Check that the transaction directory exists.
    # transaction_directory: str = config['transaction_directory']
    # if not os.path.exists(transaction_directory):
    #     logger.error(f'{transaction_directory} does not exist')
    #     exit(1)
    #
    # sqlite_db_file_path: str = config['sqlite_db_file_path']
    # if not os.path.exists(sqlite_db_file_path):
    #     logger.error(f'{sqlite_db_file_path} does not exist')
    #     exit(1)
    #
    # return config
