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
                tx_id=Faker().sha256(),
                sender=Faker().name(),
                receiver=Faker().name(),
                amount=Faker().random_number(digits=2),
                tx_type=TransactionType.REWARD if _ == 3 else TransactionType.NORMAL
            ))

        return txs