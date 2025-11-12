from __future__ import annotations

from typing import List

from exceptions.mining import InvalidBlockException
from models import User, Transaction, Block
from blockchain import Pool, Ledger


class MiningHelper:
    """
    Backend helper to encapsulate a typical mining flow:
      - Validates pool state and selects transactions
      - Builds a block (including reward), performs PoW
      - Submits the block to the ledger for consensus
    """

    @classmethod
    def mine_and_submit(cls, miner: User, transactions: List[Transaction]) -> Block:
        # Ensure there are enough transactions in the pool
        pool = Pool.get_instance()
        if len(pool.get_transactions()) < 5:
            raise InvalidBlockException("Not enough transactions in pool to start mining (need >= 5 transfers).")

        # Validate fairness: these are the required txs that must be included
        required = pool.get_required_transactions()
        if required is None:
            raise InvalidBlockException("Pool cannot determine required transactions for fairness.")

        # Ensure the provided transactions include the required ones
        for r in required:
            if r not in transactions:
                raise InvalidBlockException("Provided transactions do not include all required fairness transactions.")

        # Mine the block (includes reward)
        block = Block.mine_with_transactions(miner, transactions)

        # Submit to the ledger (enforces spacing, fairness, and validations again)
        Ledger.get_instance().submit_block(block)
        return block

