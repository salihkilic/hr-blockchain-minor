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

    tmp_data_path = tmp_path.as_posix() + "/data"
    db_path = os.path.join(tmp_data_path, "users.sqlite3")
    ledger_path = os.path.join(tmp_data_path, "ledger")
    pool_path = os.path.join(tmp_data_path, "pool")

    assert os.path.isdir(tmp_data_path)
    assert os.path.isfile(db_path)
    assert os.path.isfile(ledger_path)
    assert os.path.isfile(pool_path)




@pytest.mark.skip(reason="TODO")
def test_system_creates_missing_data_files_on_startup(self):
    """
    If data files are missing (DB / ledger / pool), system must create and configure them.
    """
    pass


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
