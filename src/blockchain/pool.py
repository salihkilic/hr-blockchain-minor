from typing import Optional
from datetime import datetime

from textual import log

from base.subscribable import Subscribable
from blockchain.abstract_pickable_singleton import AbstractPickableSingleton
from exceptions.mining import InvalidBlockException
from models import Transaction, Block
from models.enum.transaction_type import TransactionType
from services import NetworkingService
import logging

class Pool(AbstractPickableSingleton, Subscribable):
    _transactions: list[Transaction]
    _transactions_marked_for_block: list[Transaction]

    def __init__(self):
        self._transactions = []
        self._transactions_marked_for_block = []
        super().__init__()

    @classmethod
    def _save(cls) -> None:
        # Notify subscribers about the updated transactions change before saving
        super()._save()
        cls._call_subscribers(None)

    def mark_transaction_for_block(self, transaction: Transaction) -> None:
        self.get_instance()._transactions_marked_for_block.append(transaction)
        self._save()

    def unmark_transaction_for_block(self, transaction: Transaction) -> None:
        self.get_instance()._transactions_marked_for_block.remove(transaction)
        self._save()

    def get_transactions_marked_for_block(self) -> list[Transaction]:
        return self.get_instance()._transactions_marked_for_block

    def unmark_all_transaction(self):
        self.get_instance()._transactions_marked_for_block = []
        self._save()

    def add_transaction(self, transaction: Transaction, raise_exception: bool = True, broadcast_to_network: bool = True) -> None:
        transaction.validate(raise_exception)
        self.get_instance()._transactions.append(transaction)
        self._save()

        if broadcast_to_network:
            NetworkingService.get_instance().broadcast_new_transaction(
                transaction_payload=transaction.to_dict()
            )

    def remove_transaction(self, transaction: Transaction) -> None:
        self.get_instance()._transactions.remove(transaction)
        self._save()

    def remove_transactions(self, transactions: list[Transaction]) -> None:
        self.get_instance()._transactions = [tx for tx in self.get_instance()._transactions if tx not in transactions]
        self._save()

    def get_transactions(self) -> list[Transaction]:
        return self.get_instance()._transactions

    def get_transaction_without_marked_for_block(self) -> list[Transaction]:
        return [tx for tx in self.get_instance()._transactions if tx not in self.get_instance()._transactions_marked_for_block]

    def get_required_transactions(self, max_timestamp: Optional[str] = None) -> Optional[list[Transaction]]:
        """
        Get all transactions from pool that need to be included as part of the fairness protocol.
        """

        if len(self.get_instance()._transactions) < 5:
            return None

        # Only consider normal transfer transactions for fairness selection
        all_transactions = [
            tx for tx in self.get_instance()._transactions
            if tx.kind != TransactionType.MINING_REWARD and tx.validate(raise_exception=False)
        ]

        if max_timestamp is not None:
            dt_max = datetime.fromisoformat(max_timestamp)
            all_transactions = [
                tx for tx in all_transactions
                if datetime.fromisoformat(tx.timestamp) < dt_max
            ]

        if len(all_transactions) < 4:
            return None

        oldest_tx = sorted(all_transactions, key=lambda t: t.timestamp)[:2]
        remaining = [tx for tx in all_transactions if tx not in oldest_tx]
        lowest_fee_tx = sorted(remaining, key=lambda t: (t.fee, t.timestamp))[:2]

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
            raise InvalidBlockException("Not enough transactions in pool to validate fairness.")

        for req_tx in required_transactions:
            if req_tx not in block.transactions:
                raise InvalidBlockException("Not all required transactions are included in the block for fairness.")

        non_miner_txs = [tx for tx in block.transactions if tx.sender_address != block.miner_address or tx.kind != TransactionType.TRANSFER]
        if len(non_miner_txs) == 0:
            pool_non_miner_txs = [tx for tx in self.get_instance()._transactions if tx.sender_address != block.miner_address]
            if len(pool_non_miner_txs) > 0:
                raise InvalidBlockException("Block must include at least one transaction not created by the miner.")

    def remove_marked_transaction_from_pool(self):
        """ Removed the transactions marked for block from the pool and unmark them. """
        marked_txs = self.get_instance()._transactions_marked_for_block
        self.remove_transactions(marked_txs)
        self.unmark_all_transaction()

    def get_invalid_transactions_for_sender_address(self, sender_address: str) -> list[Transaction]:
        """ Get all transactions from pool for the given sender address that are invalid. """
        invalid_txs = []
        for tx in self.get_instance()._transactions:
            if tx.sender_address == sender_address and tx.is_invalid:
                invalid_txs.append(tx)
        return invalid_txs

    def mark_transaction_as_invalid(self, transaction: Transaction) -> None:
        """ Mark a transaction in the pool as invalid. """
        for tx in self.get_instance()._transactions:
            if tx == transaction:
                tx.is_invalid = True
        self._save()

    def cancel_transaction(self, transaction: Transaction) -> None:
        """ Cancel a transaction in the pool. """
        self.remove_transaction(transaction)
        self._save()

    def handle_network_transaction(self, request_data: dict) -> None:
        """ Handle a new transaction received from the network. """
        # Keep UI-visible log and also emit structured debug logs
        transaction_data = request_data['transaction']
        log(f"Received new transaction from network: {request_data}")
        logging.debug("Received network transaction payload: %s", {k: transaction_data.get(k) for k in (list(transaction_data.keys())[:10])} if isinstance(transaction_data, dict) else transaction_data)
        transaction = Transaction.from_dict(transaction_data)
        try:
            self.add_transaction(transaction, raise_exception=True, broadcast_to_network=False)
        except Exception as e:
            # Log invalid transactions from the network for observability but don't re-raise
            logging.exception("Failed to add transaction received from network: %s", e)
            return
        self._call_subscribers(None)

    @classmethod
    def load(cls) -> Optional["AbstractPickableSingleton"]:
        loaded = super().load()
        if loaded is not None:
            # Reset marked for block list on load
            loaded._transactions_marked_for_block = []
        return loaded

    @classmethod
    def get_instance(cls) -> "Pool":
        # Only override for type hinting purposes
        """ Get the singleton instance of the Pool."""
        return super().get_instance()

    def get_transactions_for_address(self, address: str) -> list["Transaction"]:
        """ Get all transactions from pool for the given address (as sender or receiver). """
        return [tx for tx in self.get_instance()._transactions if tx.sender_address == address or tx.receiver_address == address]
