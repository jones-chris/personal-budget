from datetime import date
from decimal import Decimal

import ofxclient
from ofxparse import ofxparse


class Transaction:
    """
    A Transaction object (not to be confused with an ofxclient.Transaction).
    """
    def __init__(self, transaction: ofxparse.Transaction = None, account: ofxclient.Account = None) -> None:
        if transaction and account:
            self.id: int = None
            self.payee: str = transaction.payee
            self.type: str = transaction.type
            self.date: date = transaction.date
            self.amount: int = 0
            self.institution_id: str = account.institution.number
            self.memo: str = transaction.memo
            self.sic: str = transaction.sic
            self.mcc: str = transaction.mcc
            self.checknum: str = transaction.checknum
            self.category_id: int = None
            self.transaction_amount: Decimal = transaction.amount
            self.internal_id = self.payee + str(self.date) + str(self.amount)

    @staticmethod
    def from_dict(**kwargs):
        transaction = Transaction()

        transaction.id = kwargs.get('id', None)
        transaction.payee = kwargs['payee']
        transaction.type = kwargs['type']
        transaction.date = kwargs['date']
        transaction.amount = kwargs['amount']
        transaction.institution_id = kwargs['institution_id']
        transaction.memo = kwargs['memo']
        transaction.sic = kwargs['sic']
        transaction.mcc = kwargs['mcc']
        transaction.checknum = kwargs['checknum']
        transaction.category_id = kwargs.get('category_id', None)
        transaction.transaction_category_id = kwargs.get('transaction_category_id', None)
        transaction.transaction_amount = kwargs.get('transaction_amount', None)
        transaction.internal_id = transaction.payee + str(transaction.date) + str(transaction.amount)

        return transaction

    def to_tuple(self):
        return (
            self.id,
            self.payee,
            self.type,
            self.date.strftime('%Y-%m-%d'),
            self.amount,
            self.institution_id,
            self.memo,
            self.sic,
            self.mcc,
            self.checknum,
        )


class TransactionCategory:

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        self.category_id = kwargs['category_id']
        self.transaction_id = kwargs['transaction_id']
        self.amount = kwargs['amount']

    def to_tuple(self):
        return (
            self.category_id,
            self.transaction_id,
            self.amount,
            self.id
        )


class Category:

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.name = kwargs['name']

    def to_tuple(self):
        return (
            self.id,
            self.name,
        )
