from abc import ABC, abstractmethod

from models import Transaction


class AbstractTransactionRepository(ABC):

    @abstractmethod
    def find_by_block_id(self, block_id: int) -> list[Transaction]:
        ...

    @abstractmethod
    def find_in_transaction_pool(self) -> list[Transaction]:
        ...