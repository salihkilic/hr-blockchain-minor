import os
from typing import Optional

from blockchain.abstract_pickable_singleton import AbstractPickableSingleton
from models import Block
from models.constants import FilesAndDirectories
from services import FileSystemService


class Ledger(AbstractPickableSingleton):

    # Hash - Block pairs
    _blocks: dict[str, "Block"] = {}
    _latest_block: Optional[Block] = None

    def __init__(self, file_path: Optional[str] = None):
        if file_path is None:
            filesystem_service = FileSystemService()
            file_path = os.path.join(filesystem_service.get_data_root(), FilesAndDirectories.POOL_FILE_NAME)
        super().__init__(file_path)

    def get_latest_block(self) -> Optional[Block]:
        return self._latest_block

    def get_block(self, hash: str) -> Optional[Block]:
        return self._blocks.get(hash, None)

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

    def add_block(self, block: Block) -> None:
        self._blocks[block.hash] = block
        self._latest_block = block
        self._save()

    @classmethod
    def load(cls, file_path) -> Optional["AbstractPickableSingleton"]:
        if file_path is None:
            filesystem_service = FileSystemService()
            file_path = os.path.join(filesystem_service.get_data_root(), FilesAndDirectories.LEDGER_FILE_NAME)
        return super().load(file_path)

    @classmethod
    def get_instance(cls, file_path: Optional[str] = None) -> "Ledger":
        # Only override for type hinting purposes
        """ Get the singleton instance of the Ledger."""
        return super().get_instance()

    @property
    def block_count(self):
        return len(self._blocks)
