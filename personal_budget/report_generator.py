import datetime
from typing import List, AnyStr
from openpyxl import load_workbook, Workbook
from common.config import get_config
from common.dao import Dao
from personal_budget.common.models import Transaction
from tempfile import NamedTemporaryFile


class ReportGenerator:

    def __init__(self):
        self.config: dict = get_config()
        self.db_file_path = self.config['sqlite_db_file_path']
        self.last_row_number = 10000
        self.transactions_data_range_address = f'$A$2:$J${self.last_row_number}'

    def to_file(self) -> None:
        # Default to the current month.
        end_date: datetime.date = datetime.date.today()
        start_date: datetime.date = end_date.replace(day=1)

        budget_report: Workbook = self._create_budget_report(start_date, end_date)

        budget_template_output_file_path = self.config['budget_template_output_file_path']
        budget_report.save(f'{budget_template_output_file_path}/{datetime.datetime.now()}.xlsx')

    def to_stream(self, start_date: datetime.date, end_date: datetime.date) -> AnyStr:
        budget_report: Workbook = self._create_budget_report(start_date, end_date)

        with NamedTemporaryFile() as temp:
            budget_report.save(temp.name)
            temp.seek(0)
            return temp.read()

    def _create_budget_report(self, start_date: datetime.date, end_date: datetime.date) -> Workbook:
        budget_template_file_path = self.config['budget_template_file_path']
        workbook = load_workbook(budget_template_file_path)

        transactions_worksheet = [worksheet for worksheet in workbook.worksheets if worksheet.title == 'Transactions'][0]
        transactions_data_range = transactions_worksheet[self.transactions_data_range_address]

        transactions: List[Transaction] = Dao.get_transactions(start_date, end_date, self.db_file_path)

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

        return workbook


# If this script is run directly from the terminal, then create a budget report file.
if __name__ == '__main__':
    ReportGenerator().to_file()
