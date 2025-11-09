import os
from typing import Optional

from blockchain.abstract_pickable_singleton import AbstractPickableSingleton
from models import Block
from models.constants import FilesAndDirectories


class Ledger(AbstractPickableSingleton):

    # Hash - Block pairs
    _blocks: dict[str, "Block"]
    _latest_block: Optional[Block]

    def __init__(self):
        self._blocks = {}
        self._latest_block = None
        super().__init__()
        self._initialize()

    def _initialize(self) -> None:
        """ Initialize the ledger with the genesis block if empty."""
        if not self._blocks:
            genesis_block = Block.create_genesis_block()
            self.add_block(genesis_block)

    def get_latest_block(self) -> Optional[Block]:
        return self._latest_block

    def get_block(self, hash: str) -> Optional[Block]:
        return self._blocks.get(hash, None)

    def get_block_by_number(self, number: int) -> Optional[Block]:
        """ Get a block by its number."""
        for block in self._blocks.values():
            if block.number == number:
                return block
        return None

    def get_n_blocks(self, n: int) -> list[Block]:

        # Invalid input
        if n <= 0:
            return []

        # Traverse back n blocks from the latest block
        current_block = self._latest_block
        blocks = []
        for _ in range(n):
            if current_block is None:
                break
            blocks.append(current_block)

            # We might have fewer blocks than n
            if current_block.previous_hash is None:
                break

            current_block = self._blocks[current_block.previous_hash]

        return blocks

    def get_all_blocks(self) -> list[Block]:
        return list(self._blocks.values())

    def add_block(self, block: Block) -> None:
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
