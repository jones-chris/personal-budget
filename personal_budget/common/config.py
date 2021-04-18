import json
import logging
import os
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def get_config() -> dict:
    # Get configuration file.
    config_file_path = sys.argv[1]
    if not os.path.exists(config_file_path):
        logger.error('{config_file_path} does not exist')
        exit(1)

    # Check that the config file is a json file.
    root, extension = os.path.splitext(config_file_path)
    if extension.lower() != '.json':
        logger.error('{config_file_path} must be have a .json extension.  For example, /path/to/my_config.json')

    config: dict = {}
    with open(config_file_path) as config_file:
        config = json.load(config_file)

    # Various checks to make sure the config file contents are valid...
    # Check that the transaction directory exists.
    transaction_directory: str = config['transaction_directory']
    if not os.path.exists(transaction_directory):
        logger.error(f'{transaction_directory} does not exist')
        exit(1)

    sqlite_db_file_path: str = config['sqlite_db_file_path']
    if not os.path.exists(sqlite_db_file_path):
        logger.error(f'{sqlite_db_file_path} does not exist')
        exit(1)

    return config
