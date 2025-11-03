import os
from typing import Optional

from blockchain.abstract_pickable_singleton import AbstractPickableSingleton
from models import Transaction, Block
from services import FileSystemService

class Ledger(AbstractPickableSingleton):

    _blocks: list[Block] = []

    def __init__(self, file_path: Optional[str] = None):
        self._blocks = []
        if file_path is None:
            filesystem_service = FileSystemService()
            file_path = os.path.join(filesystem_service.get_data_root(), FileSystemService.POOL_FILE_NAME)
        super().__init__(file_path)

    def get_latest_block(self) -> Optional[Block]:
        if not self._blocks:
            return None
        return self._blocks[-1]

    def get_block_by_number(self) -> Optional[Block]:
        pass

    def add_block(self, block: Block) -> None:
        self.get_instance()._blocks.append(block)
        self._save()

    @classmethod
    def load(cls, file_path) -> Optional["AbstractPickableSingleton"]:
        if file_path is None:
            filesystem_service = FileSystemService()
            file_path = os.path.join(filesystem_service.get_data_root(), FileSystemService.LEDGER_FILE_NAME)
        return super().load(file_path)

    @classmethod
    def get_instance(cls) -> "Ledger":
        # Only override for type hinting purposes
        """ Get the singleton instance of the Pool."""
        return super().get_instance()