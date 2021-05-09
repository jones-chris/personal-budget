import csv
import enum
import json
import logging
import os
import sys
from typing import List, Union, Dict, OrderedDict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Report:

    def __init__(
            self,
            name: str,
            include_transactions: bool
    ):
        self.name: str = name
        self.include_transactions: bool = include_transactions


class DataType(enum.Enum):
    """The type of data, such as transaction, investment, etc"""
    # todo: add other types here as we pull in more data, such as investments, home value, etc.
    TRANSACTION = 'transaction'


class CsvImport:

    directory: str
    headers: List[str]
    mappings: Dict[str, List[str]]
    unique_composite_fields: List[str]
    data_type: DataType

    @staticmethod
    def from_dict(**kwargs):
        csv_import: CsvImport = CsvImport()
        for key, value in kwargs.items():
            setattr(csv_import, key, value)

        return csv_import

    def map_payee(self, row: Union[Dict[str, str], OrderedDict[str, str]]) -> str:
        """Returns the value that results from applying the CsvImport's mapping to the csv.DictReader row"""
        value: str = ''

        payee_mapping: List[str] = self.mappings['payee']
        for field in payee_mapping:
            field_value = row[field]
            value = value + field_value

        return value

    def map_date(self, row: Union[Dict[str, str], OrderedDict[str, str]]) -> str:
        value: str = ''

        date_mapping: List[str] = self.mappings['date']
        for field in date_mapping:
            field_value = row[field]
            value = value + field_value

        return value

    def map_amount(self, row: Union[Dict[str, str], OrderedDict[str, str]]) -> str:
        value: str = ''

        amount_mapping: List[str] = self.mappings['amount']
        for field in amount_mapping:
            field_value = row[field]

            if field_value:
                field_value = field_value.replace('--', '')

            value = value + field_value

        return value


class OfxImport:

    member_id: str
    password: str
    institution_id: int
    url: str
    organization_name: str
    data_type: DataType

    @staticmethod
    def from_dict(**kwargs):
        ofx_import: OfxImport = OfxImport()
        for key, value in kwargs.items():
            setattr(ofx_import, key, value)

        return ofx_import


class Config:

    CONFIG_DIR_FILE_PATH: str = sys.argv[1]
    DB_FILE_PATH: str = f'{CONFIG_DIR_FILE_PATH}/budget'
    CONFIG_JSON_FILE_PATH: str = f'{CONFIG_DIR_FILE_PATH}/config.json'
    TRANSACTIONS_DIR_FILE_PATH: str = f'{CONFIG_DIR_FILE_PATH}/transactions'
    REPORTS_DIR_FILE_PATH: str = f'{CONFIG_DIR_FILE_PATH}/reports'

    # def __init__(
    #         self,
    #         reports: List[Report],
    #         csv_imports: List[CsvImport],
    #         ofx_imports: List[OfxImport],
    #         db_file_path: str
    # ):
    #     self.reports: List[Report] = reports
    #     self.csv_imports: List[CsvImport] = csv_imports
    #     self.ofx_imports: List[OfxImport] = ofx_imports
    #     self.db_file_path: str = db_file_path

    def __init__(self) -> None:
        # Get configuration file.
        if not os.path.exists(self.CONFIG_DIR_FILE_PATH):
            logger.error(f'{self.CONFIG_DIR_FILE_PATH} does not exist')
            exit(1)

        # Check that the config file is a json file.
        root, extension = os.path.splitext(self.CONFIG_JSON_FILE_PATH)
        if extension.lower() != '.json':
            logger.error(f'{self.CONFIG_JSON_FILE_PATH} must be have a .json extension.  For example, config.json')

        # Check that the transaction directory exists.
        if not os.path.exists(self.TRANSACTIONS_DIR_FILE_PATH):
            logger.error(f'{self.TRANSACTIONS_DIR_FILE_PATH} does not exist')
            exit(1)

        if not os.path.exists(self.DB_FILE_PATH):
            logger.error(f'{self.DB_FILE_PATH} does not exist')
            exit(1)

        with open(self.CONFIG_JSON_FILE_PATH) as config_file:
            config = json.load(config_file)
            self._build_ofx_imports(config)
            self._build_csv_imports(config)

    def _build_ofx_imports(self, config: dict) -> None:
        ofx_dicts: List[dict] = config['imports']['ofx']

        ofx_imports: List[OfxImport] = []
        for ofx_dict in ofx_dicts:
            ofx_import: OfxImport = OfxImport.from_dict(**ofx_dict)
            ofx_imports.append(ofx_import)

        self.ofx_imports = ofx_imports

    def _build_csv_imports(self, config: dict) -> None:
        csv_dicts: List[dict] = config['imports']['csv']

        csv_imports: List[CsvImport] = []
        for csv_dict in csv_dicts:
            csv_import: CsvImport = CsvImport.from_dict(**csv_dict)
            csv_imports.append(csv_import)

        self.csv_imports = csv_imports
