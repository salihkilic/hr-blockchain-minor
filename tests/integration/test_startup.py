import os
import unittest

import pytest

from services import FileSystemService


@pytest.mark.integration
def test_system_initializes_database_and_files_at_startup(tmp_path):
    """
    System must check and initialize the database, ledger, and transaction pool at startup.
    """
    filesystem_service = FileSystemService(repo_root=tmp_path.absolute().as_posix())
    filesystem_service.initialize_data_files()

    tmp_data_path = os.path.join(tmp_path.as_posix(), FileSystemService.DATA_DIR_NAME)
    db_path = os.path.join(tmp_data_path, FileSystemService.USERS_DB_FILE_NAME)
    ledger_path = os.path.join(tmp_data_path, FileSystemService.LEDGER_FILE_NAME)
    pool_path = os.path.join(tmp_data_path, FileSystemService.POOL_FILE_NAME)

    assert os.path.isdir(tmp_data_path)
    assert os.path.isfile(db_path)
    assert os.path.isfile(ledger_path)
    assert os.path.isfile(pool_path)




@pytest.mark.integration
def test_system_creates_missing_ledger_file_on_startup(tmp_path):
    """
    If data files are missing (DB / ledger / pool), system must create and configure them.
    """
    filesystem_service = FileSystemService(repo_root=tmp_path.absolute().as_posix())

    tmp_data_path = os.path.join(tmp_path.as_posix(), FileSystemService.DATA_DIR_NAME)
    db_path = os.path.join(tmp_data_path, FileSystemService.USERS_DB_FILE_NAME)
    ledger_path = os.path.join(tmp_data_path, FileSystemService.LEDGER_FILE_NAME)
    pool_path = os.path.join(tmp_data_path, FileSystemService.POOL_FILE_NAME)

    # Create a subset of the required files
    os.makedirs(tmp_data_path)

    _create_file(db_path)
    _create_file(pool_path)

    filesystem_service.initialize_data_files()

    assert os.path.isfile(db_path)
    assert os.path.isfile(ledger_path)
    assert os.path.isfile(pool_path)

    _check_if_file_was_changed(db_path)
    _check_if_file_was_changed(pool_path)


@pytest.mark.integration
def test_system_creates_missing_db_file_on_startup(tmp_path):
    """
        If data files are missing (DB / ledger / pool), system must create and configure them.
        """
    filesystem_service = FileSystemService(repo_root=tmp_path.absolute().as_posix())

    tmp_data_path = os.path.join(tmp_path.as_posix(), FileSystemService.DATA_DIR_NAME)
    db_path = os.path.join(tmp_data_path, FileSystemService.USERS_DB_FILE_NAME)
    ledger_path = os.path.join(tmp_data_path, FileSystemService.LEDGER_FILE_NAME)
    pool_path = os.path.join(tmp_data_path, FileSystemService.POOL_FILE_NAME)

    # Create a subset of the required files
    os.makedirs(tmp_data_path)

    _create_file(ledger_path)
    _create_file(pool_path)

    filesystem_service.initialize_data_files()

    assert os.path.isfile(db_path)
    assert os.path.isfile(ledger_path)
    assert os.path.isfile(pool_path)

    _check_if_file_was_changed(ledger_path)
    _check_if_file_was_changed(pool_path)

@pytest.mark.integration
def test_system_creates_missing_pool_file_on_startup(tmp_path):
    """
        If data files are missing (DB / ledger / pool), system must create and configure them.
        """
    filesystem_service = FileSystemService(repo_root=tmp_path.absolute().as_posix())

    tmp_data_path = os.path.join(tmp_path.as_posix(), FileSystemService.DATA_DIR_NAME)
    db_path = os.path.join(tmp_data_path, FileSystemService.USERS_DB_FILE_NAME)
    ledger_path = os.path.join(tmp_data_path, FileSystemService.LEDGER_FILE_NAME)
    pool_path = os.path.join(tmp_data_path, FileSystemService.POOL_FILE_NAME)

    # Create a subset of the required files
    os.makedirs(tmp_data_path)

    _create_file(ledger_path)
    _create_file(db_path)

    filesystem_service.initialize_data_files()

    assert os.path.isfile(db_path)
    assert os.path.isfile(ledger_path)
    assert os.path.isfile(pool_path)

    _check_if_file_was_changed(ledger_path)
    _check_if_file_was_changed(db_path)

def _check_if_file_was_changed(pool_path):
    with open(pool_path, 'rb') as pool_file:
        pool_content = pool_file.read()
        assert pool_content == b"original data"


def _create_file(pool_path):
    with open(pool_path, 'wb') as pool_file:
        pool_file.write(b"original data")

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
