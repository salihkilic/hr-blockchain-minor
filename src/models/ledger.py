import os
import pickle

from dataclasses import dataclass, field
from .block import Block
from services import FileSystemService


@dataclass
class Ledger:
    """
    A dataclass representing a blockchain ledger containing all blocks containing blocks.

    """

    blocks: dict[str, "Block"] = field(default_factory=dict)
    latest_block: Block | None = None

    def add_block(self, block: "Block") -> None:
        """
        Add a block to the ledger.

        :param block: A dictionary representing the contained blocks.
        """
        # TODO SK: Probably need to validate the block before adding? Or is that the miner's job?
        self.latest_block = block
        self.blocks[block.hash] = block

    def get_block(self, block_hash: str) -> "Block | None":
        """
        Retrieve a block from the ledger by its hash.

        :param block_hash: The hash of the block to retrieve.
        :return: The block if found, else None.
        """
        return self.blocks.get(block_hash, None)

