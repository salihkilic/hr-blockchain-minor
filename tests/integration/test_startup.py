import os
import unittest
from unittest.mock import patch

import pytest

from models.constants import FilesAndDirectories
from services import FileSystemService, InitializationService


class TestStartup(unittest.TestCase):

    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def setUp(self, mock_get_data_root):
        FileSystemService.clear_temp_data_root()
        self.tmp_data_path = FileSystemService.get_temp_data_root()
        self.initialization_service = InitializationService()

    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_system_initializes_database_and_files_at_startup(self, mock_get_data_root):
        """
        System must check and initialize the database, ledger, and transaction pool at startup.
        """
        filesystem_service = FileSystemService()
        filesystem_service.initialize_data_files()

        db_path = os.path.join(self.tmp_data_path, FilesAndDirectories.USERS_DB_FILE_NAME)
        ledger_path = os.path.join(self.tmp_data_path, FilesAndDirectories.LEDGER_FILE_NAME)
        pool_path = os.path.join(self.tmp_data_path, FilesAndDirectories.POOL_FILE_NAME)

        assert os.path.isdir(self.tmp_data_path)
        assert os.path.isfile(db_path)
        assert os.path.isfile(ledger_path)
        assert os.path.isfile(pool_path)


    @pytest.mark.skip(reason="Fix test with Pool and Ledger interaction with their own files")
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_system_creates_missing_ledger_file_on_startup(self, mock_get_data_root):
        """
        If data files are missing (DB / ledger / pool), system must create and configure them.
        """
        db_path = os.path.join(self.tmp_data_path, FilesAndDirectories.USERS_DB_FILE_NAME)
        ledger_path = os.path.join(self.tmp_data_path, FilesAndDirectories.LEDGER_FILE_NAME)
        pool_path = os.path.join(self.tmp_data_path, FilesAndDirectories.POOL_FILE_NAME)

        self._create_file(db_path)
        self._create_file(pool_path)

        self.initialization_service.initialize_application()

        assert os.path.isfile(db_path)
        assert os.path.isfile(ledger_path)
        assert os.path.isfile(pool_path)

        self._check_if_file_was_changed(db_path)
        self._check_if_file_was_changed(pool_path)


    @pytest.mark.skip(reason="Fix test with Pool and Ledger interaction with their own files")
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_system_creates_missing_db_file_on_startup(self, mock_get_data_root):
        """
            If data files are missing (DB / ledger / pool), system must create and configure them.
            """
        db_path = os.path.join(self.tmp_data_path, FilesAndDirectories.USERS_DB_FILE_NAME)
        ledger_path = os.path.join(self.tmp_data_path, FilesAndDirectories.LEDGER_FILE_NAME)
        pool_path = os.path.join(self.tmp_data_path, FilesAndDirectories.POOL_FILE_NAME)

        self._create_file(ledger_path)
        self._create_file(pool_path)

        self.initialization_service.initialize_application()

        assert os.path.isfile(db_path)
        assert os.path.isfile(ledger_path)
        assert os.path.isfile(pool_path)

        self._check_if_file_was_changed(ledger_path)
        self._check_if_file_was_changed(pool_path)

    @pytest.mark.skip(reason="Fix test with Pool and Ledger interaction with their own files")
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_system_creates_missing_pool_file_on_startup(self, mock_get_data_root):
        """
            If data files are missing (DB / ledger / pool), system must create and configure them.
            """
        db_path = os.path.join(self.tmp_data_path, FilesAndDirectories.USERS_DB_FILE_NAME)
        ledger_path = os.path.join(self.tmp_data_path, FilesAndDirectories.LEDGER_FILE_NAME)
        pool_path = os.path.join(self.tmp_data_path, FilesAndDirectories.POOL_FILE_NAME)

        self._create_file(ledger_path)
        self._create_file(db_path)

        self.initialization_service.initialize_application()

        assert os.path.isfile(db_path)
        assert os.path.isfile(ledger_path)
        assert os.path.isfile(pool_path)

        self._check_if_file_was_changed(ledger_path)
        self._check_if_file_was_changed(db_path)

    def _check_if_file_was_changed(self, path):
        with open(path, 'rb') as file:
            content = file.read()
            assert content == b"original data"

    def _create_file(self, path):
        with open(path, 'wb') as file:
            file.write(b"original data")

    @pytest.mark.skip(reason="TODO")
    def test_system_detects_tampering_in_database(self):
        """
        System must detect any unauthorized modification in the user database at startup.
        """
        pass


    @pytest.mark.skip(reason="TODO")
    def test_system_detects_tampering_in_ledger(self):
        """
        System must detect any unauthorized modification in the blockchain ledger at startup.
        """
        pass


    @pytest.mark.skip(reason="TODO")
    def test_system_detects_tampering_in_transaction_pool(self):
        """
        System must detect any unauthorized modification in the transaction pool at startup.
        """
        pass


if __name__ == '__main__':
    unittest.main()
