import os
from typing import Optional

from blockchain.abstract_pickable_singleton import AbstractPickableSingleton
from exceptions.mining import InvalidBlockException
from models import Transaction, Block
from models.constants import FilesAndDirectories
from services import FileSystemService


class Pool(AbstractPickableSingleton):
    _transactions: list[Transaction]

    def __init__(self, file_path: Optional[str] = None):
        self._transactions = []
        if file_path is None:
            filesystem_service = FileSystemService()
            file_path = os.path.join(filesystem_service.get_data_root(), FilesAndDirectories.POOL_FILE_NAME)
        super().__init__(file_path)

    def add_transaction(self, transaction: Transaction) -> None:
        self.get_instance()._transactions.append(transaction)
        self._save()

    def get_transactions(self) -> list[Transaction]:
        return self.get_instance()._transactions

    def get_required_transactions(self, max_timestamp: Optional[str] = None) -> Optional[list[Transaction]]:
        """
        Get all transactions from pool that need to be included as part of the fairness protocol.
        """

        if len(self.get_instance()._transactions) < 5:
            return None

        # TODO
        #  Filter out invalid transactions


        all_transactions = self.get_instance()._transactions

        if max_timestamp is not None:
            all_transactions = [tx for tx in all_transactions if tx.timestamp <= max_timestamp]

        oldest_tx = sorted(all_transactions, key=lambda t: t.timestamp)[:2]
        remaining = [tx for tx in all_transactions if tx not in oldest_tx]
        lowest_fee_tx = sorted(remaining, key=lambda t: t.fee)[:2]

        return oldest_tx + lowest_fee_tx

    def validate_transaction_in_block_for_fairness(self, block: Block) -> None:
        """
        Validate that the block contains the required transactions as per the fairness protocol.

        At least two oldest transactions must be included — ensures temporal fairness.
        At least two lowest-fee transactions must be included — prevents starvation of low-fee transactions.
        At least one transaction not created by the miner must be included — prevents self-bias in block composition.
            (This rule is omitted if there are no transactions from other users available in the pool.)
        """
        required_transactions = self.get_required_transactions(max_timestamp=block.timestamp)
        if required_transactions is None:
            raise Exception("Not enough transactions in pool to validate fairness.")

        for req_tx in required_transactions:
            if req_tx not in block.transactions:
                raise InvalidBlockException(f"Not all required transactions are included in the block for fairness.")

        non_miner_txs = [tx for tx in block.transactions if tx.sender_address != block.miner_address]
        if len(non_miner_txs) == 0:
            pool_non_miner_txs = [tx for tx in self.get_instance()._transactions if tx.sender_address != block.miner_address]
            if len(pool_non_miner_txs) > 0:
                raise InvalidBlockException("Block must include at least one transaction not created by the miner.")

    @classmethod
    def load(cls, file_path) -> Optional["AbstractPickableSingleton"]:
        if file_path is None:
            filesystem_service = FileSystemService()
            file_path = os.path.join(filesystem_service.get_data_root(), FilesAndDirectories.POOL_FILE_NAME)
        return super().load(file_path)

    @classmethod
    def get_instance(cls) -> "Pool":
        # Only override for type hinting purposes
        """ Get the singleton instance of the Pool."""
        return super().get_instance()

