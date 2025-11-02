import unittest
from decimal import Decimal

import pytest

from exceptions.transaction import InvalidTransactionException
from models import User, Transaction


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

    @pytest.mark.integration
    def test_miner_detects_tampered_signature_transaction_as_invalid(self):
        """
        When mining a block:
        ✅ Tampered or invalid transactions must be detected and flagged as invalid by the miner.
        """

        original_sender = User.create_for_test("sender", "secret")
        original_receiver = User.create_for_test("receiver", "secret")
        malicious_actor = User.create_for_test("malicious", "secret")

        valid_transaction = Transaction.create(original_sender, original_receiver.address, Decimal(10), Decimal(0.1))

        valid_transaction.validate()

        # Simulate tampering by changing the amount after creation
        tampered_transaction1 = Transaction.create(original_sender, original_receiver.address, Decimal(10), Decimal(0.1))
        tampered_transaction1.amount = Decimal(1000)  # Tampered amount

        with pytest.raises(InvalidTransactionException):
            tampered_transaction1.validate()

        tampered_transaction2 = Transaction.create(original_sender, original_receiver.address, Decimal(10), Decimal(0.1))
        tampered_transaction2.receiver_address = malicious_actor.address  # Tampered receiver

        with pytest.raises(InvalidTransactionException):
            tampered_transaction2.validate()

    @pytest.mark.skip(reason="TODO")
    def test_miner_detects_invalid_funds_transaction_as_invalid(self):
        """
        When mining a block:
        ✅ Tampered or invalid transactions must be detected and flagged as invalid by the miner.
        """
        # TODO: Test that the amount can be spent by the sender
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
