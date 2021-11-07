import enum
import json
import logging
import os
import distutils.dir_util
import sys
import typing
from typing import List, Union, Dict, OrderedDict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Report:

    name: str
    import_transactions: bool
    import_categories: bool

    @staticmethod
    def from_dict(**kwargs):
        report: Report = Report()
        for key, value in kwargs.items():
            setattr(report, key, value)

        return report


class DataType(enum.Enum):
    """The type of data, such as transaction, investment, etc"""
    # todo: add other types here as we pull in more data, such as investments, home value, etc.
    TRANSACTION = 'transaction'


class CsvImport:

    directory: str
    headers: List[str]
    mappings: Dict[str, List[str]]
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


class Rule:

    class MatchingOperator(enum.Enum):
        IS = 'is',
        IS_NOT = 'is not'
        CONTAINS = 'contains',
        STARTS_WITH = 'starts with',
        ENDS_WITH = 'ends with'

    # payee: str
    matching_operator: MatchingOperator
    matching_text: str
    category_id: int

    @staticmethod
    def from_dict(**kwargs):
        rule: Rule = Rule()
        type_hints: Dict = typing.get_type_hints(Rule)
        for key, value in kwargs.items():
            logger.info(f'key={key} value={value}')
            field_type = type_hints[key]
            logger.info(f'field_type is {str(field_type)}')

            if issubclass(field_type, enum.Enum):  # In the case the field is an enum, like the matching_operator, get the enum value matching the value.
                logger.info('field_type is a subclass of enum.Enum')
                setattr(rule, key, field_type[value.upper()])
            else:
                logger.info('field_type is not a subclass of enum.Enum')
                setattr(rule, key, value)

        return rule


class Config:

    CONFIG_DIR_FILE_PATH: str = sys.argv[1]
    DB_FILE_PATH: str = f'{CONFIG_DIR_FILE_PATH}/budget'
    CONFIG_JSON_FILE_PATH: str = f'{CONFIG_DIR_FILE_PATH}/config.json'
    TRANSACTIONS_DIR_FILE_PATH: str = f'{CONFIG_DIR_FILE_PATH}/transactions'
    REPORTS_DIR_FILE_PATH: str = f'{CONFIG_DIR_FILE_PATH}/reports'
    SAMPLE_CONFIG_DIR_FILE_PATH: str = './sample_budget_dir/budget'

    def __init__(self) -> None:
        # Check that the budget directory exists.
        if not os.path.exists(self.CONFIG_DIR_FILE_PATH):
            logger.error(f'{self.CONFIG_DIR_FILE_PATH} does not exist')
            exit(1)

        # Check that the directory is not empty.  If so, create a new one.
        if len(os.listdir(self.CONFIG_DIR_FILE_PATH)) == 0:
            distutils.dir_util.copy_tree(self.SAMPLE_CONFIG_DIR_FILE_PATH, self.CONFIG_DIR_FILE_PATH)

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
            self._build_reports(config)
            self._build_rules(config)

    def get_data_type_dir(self, data_type: DataType) -> str:
        """Given a DataType, return the directory path that contains files for that DataType."""
        if DataType.TRANSACTION.name == data_type:
            return self.TRANSACTIONS_DIR_FILE_PATH
        # todo:  add more DataType enum values and their directory mappings here.
        else:
            raise ValueError(f'No dir mapping found for data type, {data_type}')

    def get_report(self, report_name: str) -> Report:
        reports_with_name = [report for report in self.reports if report.name == report_name]
        if len(reports_with_name) == 0:
            raise ValueError(f'Could not find report with name, {report_name}')
        elif len(reports_with_name) > 1:
            raise ValueError(f'Found more than 1 report with name, {report_name}')
        else:
            return reports_with_name[0]

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

    def _build_reports(self, config: dict) -> None:
        report_dicts: List[dict] = config['reports']

        reports: List[Report] = []
        for report_dict in report_dicts:
            report: Report = Report.from_dict(**report_dict)
            reports.append(report)

        self.reports = reports

    def _build_rules(self, config: dict) -> None:
        rule_dicts: List[dict] = config['rules']

        rules: List[Rule] = []
        for rule_dict in rule_dicts:
            rule: Rule = Rule.from_dict(**rule_dict)
            rules.append(rule)

        self.rules = rules
