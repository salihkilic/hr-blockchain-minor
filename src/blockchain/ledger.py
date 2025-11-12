from typing import Optional

from blockchain.abstract_pickable_singleton import AbstractPickableSingleton
from models import Block
from models.block import BlockStatus, ValidationFlag
from exceptions.mining import InvalidBlockException


class Ledger(AbstractPickableSingleton):

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
    def get_latest_block(self) -> Optional[Block]:
        return self._latest_block

    def get_block(self, hash: str) -> Optional[Block]:
        return self._blocks.get(hash, None)

    def get_block_by_number(self, number: int) -> Optional[Block]:
        for block in self._blocks.values():
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

    # -----------------
    # Pending blocks & consensus
    # -----------------
    def has_pending_blocks(self) -> bool:
        return len(self._pending_blocks) > 0

    def submit_block(self, block: Block) -> None:
        # Do not allow submitting a new block while another is pending validation
        if self.has_pending_blocks():
            raise InvalidBlockException("Cannot submit new block: a previous block is still pending validation.")
        # Structural validation before accepting as pending
        previous = self.get_latest_block()
        validation = block.validate(previous)
        if not validation.valid:
            raise InvalidBlockException(f"Block structural/transaction validation failed: {validation.reasons}")
        block.status = BlockStatus.PENDING
        self._pending_blocks[block.calculated_hash] = block
        self._save()

    def get_pending_block(self, block_hash: str) -> Optional[Block]:
        return self._pending_blocks.get(block_hash)

    def add_validation_flag(self, block_hash: str, validator_address: str, valid: bool, reason: Optional[str] = None) -> dict:
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
        # Create reward transaction and place in pool
        from models import Transaction
        reward_tx = Transaction.create_mining_reward(block.miner_address, block.transactions)
        from blockchain import Pool
        Pool.get_instance().add_transaction(reward_tx)
        # Remove from pending
        self._pending_blocks.pop(block.calculated_hash, None)

    def _finalize_reject(self, block: Block) -> None:
        block.status = BlockStatus.REJECTED
        from blockchain import Pool
        pool = Pool.get_instance()
        # Return valid transactions to pool; flag invalid ones
        for tx in block.transactions:
            if tx.validate(raise_exception=False):
                pool.add_transaction(tx)
            else:
                # Mark as invalid (attribute added later if needed)
                if not hasattr(tx, 'is_invalid'):
                    setattr(tx, 'is_invalid', True)
                else:
                    tx.is_invalid = True
        # Remove from pending (not added to chain)
        self._pending_blocks.pop(block.calculated_hash, None)

    # -----------------
    # Add accepted block directly (used only internally / genesis)
    # -----------------
    def add_block(self, block: Block) -> None:
        if block.status not in (BlockStatus.ACCEPTED, BlockStatus.GENESIS, None):
            raise InvalidBlockException("Only accepted or genesis blocks can be added to the ledger.")
        self._blocks[block.calculated_hash] = block
        self._latest_block = block
        self._save()
        from blockchain import Pool
        Pool.get_instance().remove_transactions(block.transactions)

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