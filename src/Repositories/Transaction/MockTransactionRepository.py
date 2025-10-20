from Models import Transaction
from Models.Enum import TransactionType
from Repositories.Transaction.ITransactionRepository import ITransactionRepository
from faker import Faker

class MockTransactionRepository(ITransactionRepository):

    def find_by_block_id(self, block_id: int) -> list[Transaction]:
        txs = list()

        for _ in range(15):
            txs.append(Transaction(
                tx_id=Faker().uuid4(),
                sender=Faker().name(),
                receiver=Faker().name(),
                amount=Faker().random_number(digits=2),
                tx_type=TransactionType.REWARD if _ == 0 else TransactionType.NORMAL
            ))

        return txs