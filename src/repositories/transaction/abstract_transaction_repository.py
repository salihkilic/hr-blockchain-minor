from abc import ABC, abstractmethod

from models import Transaction, User


class AbstractTransactionRepository(ABC):

    @abstractmethod
    def find_by_block_id(self, block_id: int) -> list[Transaction]:
        ...

    @abstractmethod
    def find_in_transaction_pool(self) -> list[Transaction]:
        ...

    @abstractmethod
    def find_by_user(self, user: User) -> list[Transaction]:
        ...

    @abstractmethod
    def write_transaction_to_pool(self, transaction: Transaction) -> None:
        ...