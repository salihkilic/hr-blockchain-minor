import os

from exceptions import RequestedDirectoryDoesNotExistException
from models.constants import FilesAndDirectories

from services import FileSystemService


class NodeFileSystemService(FileSystemService):

    _node_data_directory: str = None

    _file_targets = [
        FilesAndDirectories.LEDGER_FILE_NAME,
        FilesAndDirectories.POOL_FILE_NAME,
    ]

    @classmethod
    def get_name(cls) -> str:
        return "Node files"

    @classmethod
    def set_node_data_directory_by_number(cls, number: int) -> None:
        if cls._node_data_directory is not None:
            raise Exception("Node data directory has already been set.")
        cls._node_data_directory = f"data_node_{number}"

    def get_data_root(self, create_if_missing: bool = False) -> str:
        """ Returns the absolute path to the 'data' directory of the project specific to this node. """
        data_root = os.path.join(self.repo_root, self.__class__._node_data_directory)

        if not self.validate_directory_exists(data_root):
            if create_if_missing:
                os.makedirs(data_root)
            else:
                raise RequestedDirectoryDoesNotExistException(f"Node data root directory does not exist: {data_root}")

        return data_root

