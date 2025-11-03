from typing import Optional

from blockchain.abstract_pickable_singleton import AbstractPickableSingleton
from models import Transaction


class Pool(AbstractPickableSingleton):
    _transactions: list[Transaction] = []

    def add_transaction(self, transaction: Transaction) -> None:
        self._transactions.append(transaction)
        self._save()

    def get_transactions(self) -> list[Transaction]:
        return self._transactions

    @classmethod
    def get_instance(cls) -> "Pool":
        # Only override for type hinting purposes
        """ Get the singleton instance of the Pool."""
        return super().get_instance()

