from typing import Optional

from textual import log

from base.subscribable import Subscribable
from blockchain.abstract_pickable_singleton import AbstractPickableSingleton
from models import Block
from models.block import BlockStatus, ValidationFlag
from exceptions.mining import InvalidBlockException
from models.enum import TransactionType


class Ledger(AbstractPickableSingleton, Subscribable):
    # Hash - Block pairs
    _blocks: dict[str, "Block"]
    _latest_block: Optional[Block]
    _pending_blocks: dict[str, Block]

    def __init__(self):
        self._blocks = {}
        self._latest_block = None
        self._pending_blocks = {}
        super().__init__()
        self._initialize()

    def _initialize(self) -> None:
        """ Initialize the ledger with the genesis block if empty."""
        if not self._blocks:
            genesis_block = Block.create_genesis_block()
            self._blocks[genesis_block.calculated_hash] = genesis_block
            self._latest_block = genesis_block
            self._save()

    # -----------------
    # Basic getters
    # -----------------
    def get_latest_block(self, include_pending: bool = False) -> Optional[Block]:
        if include_pending and self.has_pending_blocks():
            return self.get_pending_block()
        return self._latest_block

    def get_block(self, hash: str) -> Optional[Block]:
        return self._blocks.get(hash, None)

    def get_block_by_number(self, number: int, include_pending: bool = False) -> Optional[Block]:
        blocks = self._blocks.values()

        if include_pending:
            blocks = list(blocks) + list(self._pending_blocks.values())

        for block in blocks:
            if block.number == number:
                return block
        return None

    def get_n_blocks(self, n: int) -> list[Block]:
        if n <= 0:
            return []
        current_block = self._latest_block
        blocks = []
        for _ in range(n):
            if current_block is None:
                break
            blocks.append(current_block)
            if current_block.previous_hash is None:
                break
            current_block = self._blocks[current_block.previous_hash]
        return blocks

    def get_all_blocks(self) -> list[Block]:
        return list(self._blocks.values())

    # Helper to get the chain in order (genesis -> latest)
    def _get_chain_ordered(self) -> list[Block]:
        return list(reversed(self.get_n_blocks(self.block_count)))

    # -----------------
    # Chain integrity validation
    # -----------------
    def validate_chain(self) -> tuple[bool, list[str]]:
        """
        Validate the entire chain from genesis to latest.
        Checks:
          - Linkage and numbering
          - Non-genesis blocks are ACCEPTED
          - 3-minute spacing between consecutive blocks
          - Merkle root, hash, difficulty and tx validity via Block.validate
        Returns (is_valid, errors)
        """
        errors: list[str] = []
        chain = self._get_chain_ordered()
        if not chain:
            errors.append("Ledger is empty.")
            return (False, errors)

        from datetime import datetime
        previous: Optional[Block] = None
        for idx, block in enumerate(chain):
            # Status rules
            if block.number == 0:
                if block.status not in (BlockStatus.GENESIS,):
                    errors.append(f"Genesis block has invalid status: {block.status}.")
            else:
                if block.status != BlockStatus.ACCEPTED:
                    errors.append(f"Block #{block.number} is not ACCEPTED.")

            # Timing rules (non-genesis)
            if previous is not None:
                prev_ts = datetime.fromisoformat(previous.timestamp)
                this_ts = datetime.fromisoformat(block.timestamp)
                delta = (this_ts - prev_ts).total_seconds()
                if delta < 180:
                    errors.append(f"Blocks #{previous.number} -> #{block.number} are less than 3 minutes apart.")

            # Structural + transaction validation
            validation = block.validate(previous)
            if not validation.valid:
                joined = "; ".join(validation.reasons)
                errors.append(f"Block #{block.number} failed validation: {joined}")

            previous = block

        return (len(errors) == 0, errors)

    # -----------------
    # Pending blocks & consensus
    # -----------------
    def has_pending_blocks(self) -> bool:
        return len(self._pending_blocks) > 0

    def submit_block(self, block: Block) -> None:
        # Do not allow submitting a new block while another is pending validation
        if self.has_pending_blocks():
            raise InvalidBlockException("Cannot submit new block: a previous block is still pending validation.")

        previous = self.get_latest_block()

        # Require building on an accepted (or genesis) block
        if previous is None:
            raise InvalidBlockException("Previous block missing.")
        if previous.number != 0 and previous.status != BlockStatus.ACCEPTED:
            raise InvalidBlockException("Previous block is not accepted.")

        # Enforce 3-minute spacing between blocks (non-genesis)
        if block.number != 0:
            from datetime import datetime
            prev_ts = datetime.fromisoformat(previous.timestamp)
            this_ts = datetime.fromisoformat(block.timestamp)
            delta = (this_ts - prev_ts).total_seconds()
            if delta < 180:
                raise InvalidBlockException("At least 3 minutes must pass between consecutive blocks.")

        # Structural + transaction validation
        validation = block.validate(previous)
        if not validation.valid:
            raise InvalidBlockException(f"Block structural/transaction validation failed: {validation.reasons}")

        # Fairness validation against pool
        from blockchain import Pool
        Pool.get_instance().validate_transaction_in_block_for_fairness(block)

        block.status = BlockStatus.PENDING
        self._pending_blocks[block.calculated_hash] = block
        self._save()

    def get_pending_block(self) -> Optional[Block]:
        if not self.has_pending_blocks():
            return None

        return next(iter(self._pending_blocks.values()))

    def add_validation_flag(self, block_hash: str, validator_address: str, valid: bool,
                            reason: Optional[str] = None) -> dict:
        block = self._pending_blocks.get(block_hash)
        if block is None:
            raise InvalidBlockException("Pending block not found.")
        if block.status != BlockStatus.PENDING:
            raise InvalidBlockException("Block is not pending.")
        if validator_address == block.miner_address:
            raise InvalidBlockException("Miner cannot validate own block.")
        # Prevent duplicate validation by same validator
        if any(vf.validator == validator_address for vf in block.validators):
            raise InvalidBlockException("Validator has already validated this block.")

        block.validators.append(ValidationFlag(validator=validator_address, valid=valid, reason=reason))
        valid_count = sum(1 for vf in block.validators if vf.valid)
        invalid_count = sum(1 for vf in block.validators if not vf.valid)

        # Consensus thresholds
        if valid_count >= 3 and invalid_count < 3:
            self._finalize_accept(block)
        elif invalid_count >= 3 and valid_count < 3:
            self._finalize_reject(block)
        self._save()
        return {
            "status": block.status.value if block.status else None,
            "valid_flags": valid_count,
            "invalid_flags": invalid_count
        }

    def _finalize_accept(self, block: Block) -> None:
        block.status = BlockStatus.ACCEPTED
        # Move block into chain
        self._blocks[block.calculated_hash] = block
        self._latest_block = block
        # Remove from pending
        self._pending_blocks.pop(block.calculated_hash, None)
        # Remove included transactions from pool
        from blockchain import Pool
        Pool.get_instance().remove_transactions(block.transactions)

    def _finalize_reject(self, block: Block) -> None:
        block.status = BlockStatus.REJECTED
        from blockchain import Pool
        pool = Pool.get_instance()
        # Return valid transactions to pool; flag invalid ones
        for tx in block.transactions:

            if tx.kind == TransactionType.MINING_REWARD:
                continue # Do not return mining rewards to pool

            if not tx.validate(raise_exception=False):
                # Mark as invalid (attribute added later if needed)
                if not hasattr(tx, 'is_invalid'):
                    setattr(tx, 'is_invalid', True)
                else:
                    tx.is_invalid = True
            pool.add_transaction(tx, raise_exception=False)
        # Remove from pending (not added to chain)
        self._pending_blocks.pop(block.calculated_hash, None)

    # -----------------
    # Add accepted block directly (used only internally / genesis)
    # -----------------
    def add_block(self, block: Block) -> None:
        # Accept directly added blocks by marking them as ACCEPTED if needed
        if block.status in (None, BlockStatus.PENDING):
            block.status = BlockStatus.ACCEPTED
        if block.status not in (BlockStatus.ACCEPTED, BlockStatus.GENESIS):
            raise InvalidBlockException("Only accepted or genesis blocks can be added to the ledger.")
        self._blocks[block.calculated_hash] = block
        self._latest_block = block
        self._save()
        from blockchain import Pool
        Pool.get_instance().remove_transactions(block.transactions)

    @classmethod
    def mine_new_block(cls):
        """ Mines a new block using the currently logged-in user as miner and the transactions marked for inclusion in the pool.
            Automatically adds the block for pending and clear te necessary pool transactions.
        """
        from blockchain import Pool
        from services.user_service import UserService

        marked_transactions = Pool.get_instance().get_transactions_marked_for_block()
        logged_in_user = UserService.logged_in_user

        if logged_in_user is None:
            raise InvalidBlockException("No logged-in user to mine the block.")

        log("Mining new block...")

        block = Block.mine_with_transactions(logged_in_user, marked_transactions)

        log("Block mined with nonce %d and hash %s" % (block.nonce, block.calculated_hash))

        Ledger.get_instance().submit_block(block)
        Pool.get_instance().remove_marked_transaction_from_pool()

    @classmethod
    def _save(cls) -> None:
        super()._save()
        cls._call_subscribers(None)

    @classmethod
    def load(cls) -> Optional["AbstractPickableSingleton"]:
        return super().load()

    @classmethod
    def get_instance(cls) -> "Ledger":
        # Only override for type hinting purposes
        """ Get the singleton instance of the Ledger."""
        return super().get_instance()

    @property
    def block_count(self):
        return len(self._blocks)

    def get_transactions_for_address(self, address: str) -> list["Transaction"]:
        """ Get all transactions in the ledger involving the given address."""
        transactions = []
        for block in self._blocks.values():
            for tx in block.transactions:
                if tx.sender_address == address or tx.receiver_address == address:
                    transactions.append(tx)
        return transactions
