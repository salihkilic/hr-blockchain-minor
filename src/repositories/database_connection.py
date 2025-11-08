import sqlite3
from abc import abstractmethod
from typing import Optional


class DatabaseConnection:

    def __init__(self, db_file_path: Optional[str] = None):
        # Injected services
        from services import FileSystemService
        self.FileSystemService = FileSystemService()

        db_file_path = self.FileSystemService.get_data_file_path("users.sqlite3")

        self.db_path = db_file_path
        self._db_connection: sqlite3.Connection | None = None

    @abstractmethod
    def setup_database_structure(self) -> None:
        """ Creates the necessary database tables and structure. """
        ...

    def _db_connect(self) -> None:
        """ Establishes a connection to the SQLite database if not already connected. """
        if self._db_connection is None:
            self._db_connection = sqlite3.connect(self.db_path)
            self._db_connection.row_factory = sqlite3.Row

    def _db_close(self) -> None:
        """ Closes the connection to the SQLite database if it is open. """
        if self._db_connection is not None:
            self._db_connection.close()
            self._db_connection = None
