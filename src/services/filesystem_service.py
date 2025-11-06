import os
from typing import Optional

from exceptions import RequestedDirectoryDoesNotExistException, RequestedFileDoesNotExistException
from models.constants import FilesAndDirectories


class FileSystemService:

    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = repo_root
        if repo_root is None:
            self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    def initialize_data_files(self):
        self.get_data_file_path(FilesAndDirectories.USERS_DB_FILE_NAME, create_if_missing=True)
        self.get_data_file_path(FilesAndDirectories.POOL_FILE_NAME, create_if_missing=True)
        self.get_data_file_path(FilesAndDirectories.LEDGER_FILE_NAME, create_if_missing=True)

    def get_src_root(self) -> str:
        """ Returns the absolute path to the 'src' directory of the project. """
        data_root = os.path.join(self.repo_root, FilesAndDirectories.SRC_DIR_NAME)
        if not self.validate_directory_exists(data_root):
            raise RequestedDirectoryDoesNotExistException(f"Src root directory does not exist: {data_root}")
        return data_root

    def get_data_root(self, create_if_missing: bool = False) -> str:
        """ Returns the absolute path to the 'data' directory of the project. """
        data_root = os.path.join(self.repo_root, FilesAndDirectories.DATA_DIR_NAME)

        if not self.validate_directory_exists(data_root):
            if create_if_missing:
                os.makedirs(data_root)
            else:
                raise RequestedDirectoryDoesNotExistException(f"Data root directory does not exist: {data_root}")

        return data_root

    def validate_file_exists(self, file_path: str, throw_exception: bool = False) -> bool:
        """ Validates that the specified file exists. Throws an exception if not found, and throw_exception is True. """
        if os.path.isfile(file_path):
            return True
        if throw_exception:
            raise RequestedFileDoesNotExistException(f"File does not exist: {file_path}")
        return False

    def validate_directory_exists(self, dir_path: str, throw_exception: bool = False) -> bool:
        """ Validates that the specified directory exists. Throws an exception if not found, and throw_exception is True. """
        if os.path.isdir(dir_path):
            return True
        if throw_exception:
            raise RequestedDirectoryDoesNotExistException(f"Directory does not exist: {dir_path}")
        return False

    def get_data_file_path(self, data_filename: str, create_if_missing: bool = False) -> str:
        """ Returns the absolute path to the specified file within the data directory. Throws an exception if the data directory does not exist. """
        data_root = self.get_data_root(create_if_missing=create_if_missing)
        data_path = os.path.join(data_root, data_filename)
        if not os.path.exists(data_path):
            if create_if_missing:
                self.create_file(data_path)
            else:
                raise RequestedFileDoesNotExistException(f"File does not exist: {data_path}")
        return data_path

    def get_sql_file_path(self, sql_filename: str) -> str:
        """ Returns the absolute path to the specified SQL file within the src/DatabaseScripts directory. Throws an exception if the directory does not exist. """
        src_root = self.get_src_root()
        sql_dir = os.path.join(src_root, FilesAndDirectories.DATABASE_SCRIPTS_DIR_NAME)
        self.validate_directory_exists(sql_dir, throw_exception=True)
        sql_path = os.path.join(sql_dir, sql_filename)
        self.validate_file_exists(sql_path, throw_exception=True)
        return sql_path

    def create_file(self, file_path: str, throw_exception_if_exists: bool = False):
        """ Creates a file """
        file_path = os.path.abspath(file_path)
        directory = os.path.dirname(file_path)

        if not os.path.isdir(directory):
            raise RequestedDirectoryDoesNotExistException(
                f"Directory does not exist: {directory}"
            )

        if os.path.exists(file_path):
            if throw_exception_if_exists:
                raise IOError(f"File already exists: {file_path}")
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                pass
        except Exception as e:
            raise IOError(f"Failed to create file: {file_path}") from e
