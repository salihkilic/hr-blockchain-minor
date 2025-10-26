from decimal import Decimal

from models import Transaction
from faker import Faker

from repositories.transaction import AbstractTransactionRepository


class MockTransactionRepository(AbstractTransactionRepository):

    def find_by_block_id(self, block_id: int) -> list[Transaction]:
        txs = list()

        for _ in range(10):
            txs.append(self._fake_transaction(kind='reward' if _ == 0 else 'transfer'))

        return txs

    def find_in_transaction_pool(self) -> list[Transaction]:
        txs = list()

        for _ in range(5):
            txs.append(self._fake_transaction(kind='reward' if _ == 0 else 'transfer'))

        return txs

    def _fake_transaction(self, kind) -> Transaction:
        return Transaction(
                kind=kind,
                txid=Faker().sha256(),
                receiver_address=Faker().uuid4(),
                sender_address=Faker().uuid4(),
                fee=Decimal(Faker().pyfloat(1, 2, positive=True)),
                amount=Decimal(Faker().pyfloat(2, 2, positive=True)),
                version=1,
                timestamp=Faker().iso8601(),
                signature="SIGNATURE",
                sender_public_key="KEY"

            )

