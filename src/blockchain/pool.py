import os
from typing import Optional

from blockchain.abstract_pickable_singleton import AbstractPickableSingleton
from models import Transaction
from services import FileSystemService


class Pool(AbstractPickableSingleton):
    _transactions: list[Transaction]

    def __init__(self, file_path: Optional[str] = None):
        self._transactions = []
        if file_path is None:
            filesystem_service = FileSystemService()
            file_path = os.path.join(filesystem_service.get_data_root(), FileSystemService.POOL_FILE_NAME)
        super().__init__(file_path)

    def add_transaction(self, transaction: Transaction) -> None:
        self.get_instance()._transactions.append(transaction)
        self._save()

    def get_transactions(self) -> list[Transaction]:
        return self.get_instance()._transactions

    @classmethod
    def load(cls, file_path) -> Optional["AbstractPickableSingleton"]:
        if file_path is None:
            filesystem_service = FileSystemService()
            file_path = os.path.join(filesystem_service.get_data_root(), FileSystemService.POOL_FILE_NAME)
        return super().load(file_path)

    @classmethod
    def get_instance(cls) -> "Pool":
        # Only override for type hinting purposes
        """ Get the singleton instance of the Pool."""
        return super().get_instance()

