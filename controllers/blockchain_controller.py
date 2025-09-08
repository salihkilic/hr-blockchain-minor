from __future__ import annotations

from typing import List

from models.blockchain import Blockchain
from models.transaction import Transaction


class BlockchainController:
    """
    Facade around the Blockchain model for the UI layer.
    """

    def __init__(self, difficulty_prefix: str = "0000") -> None:
        self.blockchain = Blockchain(difficulty_prefix=difficulty_prefix)

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def get_chain(self) -> List[dict]:
        return self.blockchain.to_list()

    def is_valid(self) -> bool:
        return self.blockchain.is_valid()

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------
    def add_transaction(self, sender: str, recipient: str, amount: float) -> Transaction:
        tx = Transaction.create(sender=sender, recipient=recipient, amount=amount)
        self.blockchain.add_transaction(tx)
        return tx

    def mine(self):
        return self.blockchain.mine_pending_transactions()

