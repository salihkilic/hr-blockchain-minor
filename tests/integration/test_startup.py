import unittest

import pytest


class TestStartup(unittest.TestCase):

    @pytest.mark.skip(reason="TODO")
    def test_system_initializes_database_and_files_at_startup(self):
        """
        System must check and initialize the database, ledger, and transaction pool at startup.
        """
        pass

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
