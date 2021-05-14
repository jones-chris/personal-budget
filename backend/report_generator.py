import datetime
import logging
from sqlite3 import Connection
from typing import List, AnyStr
from openpyxl import load_workbook, Workbook
from config import Config, Report
from dao import Dao
from models import Transaction, Category
from tempfile import NamedTemporaryFile


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class ReportGenerator:

    def __init__(self, db_connection: Connection):
        self.config: Config = Config()
        self.db_connection: Connection = db_connection
        self.last_row_number = 10000
        self.transactions_data_range_address = f'$A$2:$K${self.last_row_number}'
        self.categories_data_range_address = f'$A$2:$B${self.last_row_number}'

    # def to_file(self) -> None:
    #     # Default to the current month.
    #     end_date: datetime.date = datetime.date.today()
    #     start_date: datetime.date = end_date.replace(day=1)
    #
    #     budget_report: Workbook = self._create_budget_report(start_date, end_date)
    #
    #     budget_template_output_file_path = self.config['budget_template_output_file_path']
    #     budget_report.save(f'{budget_template_output_file_path}/{datetime.datetime.now()}.xlsx')

    def to_stream(self, start_date: datetime.date, end_date: datetime.date, report_name: str) -> AnyStr:
        budget_report: Workbook = self._create_budget_report(start_date, end_date, report_name)

        with NamedTemporaryFile() as temp:
            budget_report.save(temp.name)
            temp.seek(0)
            return temp.read()

    def _create_budget_report(self, start_date: datetime.date, end_date: datetime.date, report_name: str) -> Workbook:
        report_file_path = f'{self.config.REPORTS_DIR_FILE_PATH}/{report_name}'

        logger.info(f'Loading report from {report_file_path}')
        workbook = load_workbook(report_file_path)

        report: Report = self.config.get_report(report_name)
        if report.import_transactions:
            self._import_transactions(workbook, start_date, end_date)
        if report.import_categories:
            self._import_categories(workbook)

        return workbook

    def _import_transactions(self, workbook: Workbook, start_date: datetime.date, end_date: datetime.date) -> None:
        transactions_worksheet = [worksheet for worksheet in workbook.worksheets if worksheet.title == 'Transactions'][0]
        transactions_data_range = transactions_worksheet[self.transactions_data_range_address]

        transactions: List[Transaction] = Dao.get_transactions(start_date, end_date, self.db_connection)

        if len(transactions) >= self.last_row_number:
            raise ValueError(
                f'{len(transactions)} transactions retrieved, but there are only {self.last_row_number} rows to insert '
                f'into in the spreadsheet'
            )

        for i, transaction in enumerate(transactions):
            row = transactions_data_range[i]
            row[0].value = transaction.id
            row[1].value = transaction.payee
            row[2].value = transaction.type
            row[3].value = transaction.amount
            row[4].value = transaction.institution_id
            row[5].value = transaction.memo
            row[6].value = transaction.sic
            row[7].value = transaction.mcc
            row[8].value = transaction.checknum
            row[9].value = transaction.date
            row[10].value = transaction.category_id

    def _import_categories(self, workbook: Workbook) -> None:
        categories_worksheet = [worksheet for worksheet in workbook.worksheets if worksheet.title == 'Categories'][0]
        categories_data_range = categories_worksheet[self.categories_data_range_address]

        categories: List[Category] = Dao.get_categories(self.db_connection)

        if len(categories) >= self.last_row_number:
            raise ValueError(
                f'{len(categories)} categories retrieved, but there are only {self.last_row_number} rows to insert '
                f'into in the spreadsheet'
            )

        for i, category in enumerate(categories):
            row = categories_data_range[i]
            row[0].value = category.id
            row[1].value = category.name

# # If this script is run directly from the terminal, then create a budget report file.
# if __name__ == '__main__':
#     ReportGenerator().to_file()
