import os

from exceptions import RequestedDirectoryDoesNotExistException, RequestedFileDoesNotExistException


class FileSystemService:

    def get_src_root(self, create_if_missing: bool = True) -> str:
        """ Returns the absolute path to the 'src' directory of the project. """
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        data_root = os.path.join(repo_root, "src")
        if create_if_missing and not self.validate_directory_exists(data_root):
            os.makedirs(data_root)
        else:
            raise RequestedDirectoryDoesNotExistException(f"Data root directory does not exist: {data_root}")
        return data_root

    def get_data_root(self, create_if_missing: bool = True) -> str:
        """ Returns the absolute path to the 'data' directory of the project. """
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        data_root = os.path.join(repo_root, "data")
        if create_if_missing and not self.validate_directory_exists(data_root):
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

    def get_db_file_path(self, db_filename: str, create_if_missing: bool = True) -> str:
        """ Returns the absolute path to the specified database file within the data directory. Throws an exception if the data directory does not exist. """
        data_root = self.get_data_root()
        db_path = os.path.join(data_root, db_filename)
        if create_if_missing and not os.path.exists(data_root):
            os.makedirs(data_root)
        else:
            raise RequestedFileDoesNotExistException(f"File does not exist: {data_root}")
        return db_path

    def get_sql_file_path(self, sql_filename: str, create_if_missing: bool = True) -> str:
        """ Returns the absolute path to the specified SQL file within the src/DatabaseScripts directory. Throws an exception if the directory does not exist. """
        src_root = self.get_src_root()
        sql_dir = os.path.join(src_root, "DatabaseScripts")
        self.validate_directory_exists(sql_dir, throw_exception=True)
        sql_path = os.path.join(sql_dir, sql_filename)
        self.validate_file_exists(sql_path, throw_exception=True)
        return sql_path
