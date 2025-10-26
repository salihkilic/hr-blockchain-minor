import unittest

import pytest


class TestTransactionValidation(unittest.TestCase):

    @pytest.mark.skip(reason="TODO")
    def test_transaction_created_with_sufficient_balance_is_added_to_pool(self):
        """
        When creating a transaction:
        ✅ If user has enough balance → transaction must be added to the pool as pending.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_transaction_created_with_insufficient_balance_is_rejected(self):
        """
        When creating a transaction:
        ❌ If user does NOT have enough balance → transaction creation must be rejected.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_invalid_transaction_creation_is_rejected(self):
        """
        When creating a transaction:
        ❌ Any invalid transaction must be rejected (e.g., negative amount, invalid receiver).
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_miner_detects_tampered_transaction_as_invalid(self):
        """
        When mining a block:
        ✅ Tampered or invalid transactions must be detected and flagged as invalid by the miner.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_flagged_invalid_transaction_is_canceled_on_creator_login(self):
        """
        When creator of a flagged transaction logs in:
        ✅ The transaction must be automatically canceled and removed from pending state.
        """
        pass


if __name__ == '__main__':
    unittest.main()
