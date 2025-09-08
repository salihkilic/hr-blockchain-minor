from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import List

from .block import Block
from .transaction import Transaction


@dataclass
class Blockchain:
    """
    Minimal  blockchain model.
    """
    difficulty_prefix: str = "00"
    chain: List[Block] = field(default_factory=list)
    pending_transactions: List[Transaction] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.chain:
            self._create_genesis_block()

    # ------------------------------------------------------------------
    # Genesis
    # ------------------------------------------------------------------
    def _create_genesis_block(self) -> None:
        genesis = Block(index=0, timestamp=time(), transactions=[], previous_hash="0" * 64)
        self.chain.append(genesis)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    # ------------------------------------------------------------------
    # Transactions / Mining
    # ------------------------------------------------------------------
    def add_transaction(self, tx: Transaction) -> None:
        self.pending_transactions.append(tx)

    def mine_pending_transactions(self) -> Block:
        new_block = Block(
            index=len(self.chain),
            timestamp=time(),
            transactions=list(self.pending_transactions),
            previous_hash=self.last_block.hash
        )
        new_block.mine(self.difficulty_prefix)
        self.chain.append(new_block)
        self.pending_transactions.clear()
        return new_block

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def is_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]
            # Recompute hash
            recomputed = Block(
                index=current.index,
                timestamp=current.timestamp,
                transactions=current.transactions,
                previous_hash=current.previous_hash,
                nonce=current.nonce
            ).hash
            if recomputed != current.hash or current.previous_hash != prev.hash:
                return False
        return True

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------
    def to_list(self) -> List[dict]:
        return [b.to_dict() for b in self.chain]
