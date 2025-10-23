from decimal import Decimal

from Models import Transaction
from Models.Enum import TransactionType
from Repositories.Transaction.ITransactionRepository import ITransactionRepository
from faker import Faker

class MockTransactionRepository(ITransactionRepository):

    def find_by_block_id(self, block_id: int) -> list[Transaction]:
        txs = list()

        random_length = Faker().random_int(min=10, max=25)

        for _ in range(random_length):
            txs.append(Transaction(
                txid=Faker().sha256(),
                receiver_address=Faker().uuid4(),
                sender_address=Faker().uuid4(),
                fee=Decimal(Faker().pyfloat(1, 2, positive=True)),
                amount=Decimal(Faker().pyfloat(2, 2, positive=True)),
                version=1
            ))

        return txs

    def find_in_transaction_pool(self) -> list[Transaction]:
        txs = list()

        random_length = Faker().random_int(min=10, max=25)

        for _ in range(random_length):
            txs.append(Transaction(
                txid=Faker().sha256(),
                receiver_address=Faker().uuid4(),
                sender_address=Faker().uuid4(),
                fee=Decimal(Faker().pyfloat(1, 2, positive=True)),
                amount=Decimal(Faker().pyfloat(2, 2, positive=True)),
                version=1
            ))

        return txs

