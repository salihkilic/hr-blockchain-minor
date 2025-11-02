from decimal import Decimal
from typing import Optional

from models import Transaction, User
from faker import Faker

from models.enum import TransactionType
from repositories.transaction import AbstractTransactionRepository


class MockTransactionRepository(AbstractTransactionRepository):

    def find_by_block_id(self, block_id: int) -> list[Transaction]:
        txs = list()

        for _ in range(10):
            txs.append(self._fake_transaction(kind=TransactionType.MINING_REWARD if _ == 0 else TransactionType.TRANSFER))

        return txs

    def find_in_transaction_pool(self) -> list[Transaction]:
        txs = list()

        for _ in range(5):
            txs.append(self._fake_transaction(kind=TransactionType.SIGNUP_REWARD if _ == 0 or _ == 3 else TransactionType.TRANSFER))

        return txs

    def find_by_user(self, user: User) -> list[Transaction]:
        txs = list()

        for _ in range(10):
            txs.append(self._fake_transaction(kind=TransactionType.TRANSFER))

        return txs

    def _fake_transaction(self, kind: TransactionType) -> Transaction:
        return Transaction(
                kind=kind,
                receiver_address=Faker().sha256(),
                sender_address=Faker().sha256(),
                fee=Decimal(Faker().pyfloat(1, 2, positive=True)),
                amount=Decimal(Faker().pyfloat(2, 2, positive=True)),
                sender_signature="SIGNATURE",
                sender_public_key="KEY"
            )

    def write_transaction_to_pool(self, transaction: Transaction) -> None:
        pass



