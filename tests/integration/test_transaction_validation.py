import unittest
from decimal import Decimal
from unittest.mock import patch, MagicMock

import pytest

from exceptions.transaction import InvalidTransactionException, InsufficientBalanceException
from models import User, Transaction, Block, Wallet
from services import FileSystemService, InitializationService


class TestTransactionValidation(unittest.TestCase):

    _user_addresses = {}

    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def setUp(self, mock_get_data_root):
        FileSystemService.clear_temp_data_root()
        InitializationService.initialize_application()
        from blockchain import Pool, Ledger
        Ledger.destroy_instance()
        Pool.destroy_instance()
        self.__class__._user_addresses = {}

    @pytest.mark.skip(reason="TODO")
    def test_transaction_created_with_sufficient_balance_is_added_to_pool(self):
        """
        When creating a transaction:
        If user has enough balance → transaction must be added to the pool as pending.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_transaction_created_with_insufficient_balance_is_rejected(self):
        """
        When creating a transaction:
        If user does NOT have enough balance → transaction creation must be rejected.
        """
        pass

    @pytest.mark.skip(reason="TODO")
    def test_invalid_transaction_creation_is_rejected(self):
        """
        When creating a transaction:
        Any invalid transaction must be rejected (e.g., negative amount, invalid receiver).
        """
        pass

    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    @patch("repositories.user.UserRepository.find_by_address", side_effect=lambda address: TestTransactionValidation._user_addresses.get(address))
    @patch("models.wallet.Wallet.balance", new_callable=lambda: Decimal("10000.0"))
    def test_miner_detects_tampered_signature_transaction_as_invalid(self, mock_from_address, mock_find_by_address, mock_get_data_root):
        """
        When mining a block:
        Tampered or invalid transactions must be detected and flagged as invalid by the miner.
        """

        original_sender = User.create("sender", "secret")
        original_receiver = User.create("receiver", "secret")
        malicious_actor = User.create("malicious", "secret")

        self.__class__._user_addresses[original_sender.address] = original_sender
        self.__class__._user_addresses[original_receiver.address] = original_receiver
        self.__class__._user_addresses[malicious_actor.address] = malicious_actor

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

    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    @patch("repositories.user.UserRepository.username_exists", return_value=False)
    @patch("repositories.user.UserRepository.find_by_address", side_effect=lambda address: TestTransactionValidation._user_addresses.get(address))
    def test_miner_detects_invalid_funds_transaction_as_invalid(self, mock_username_exists, mock_find_by_address, mock_get_data_root):
        """
        When mining a block:
        Tampered or invalid transactions must be detected and flagged as invalid by the miner.
        """

        from blockchain import Ledger, Pool

        user1 = User.create("user1", "password")
        user2 = User.create("user2", "password")
        user3 = User.create("user3", "password")
        user4 = User.create("user4", "password")
        user5 = User.create("user5", "password")

        self.__class__._user_addresses[user1.address] = user1
        self.__class__._user_addresses[user2.address] = user2
        self.__class__._user_addresses[user3.address] = user3
        self.__class__._user_addresses[user4.address] = user4
        self.__class__._user_addresses[user5.address] = user5

        # Create signup transactions to fund the users
        signup_tx1 = Transaction.create_signup_reward(user1.address) # Wallet 50
        signup_tx2 = Transaction.create_signup_reward(user2.address) # Wallet 50
        signup_tx3 = Transaction.create_signup_reward(user3.address) # Wallet 50
        signup_tx4 = Transaction.create_signup_reward(user4.address) # Wallet 50
        signup_tx5 = Transaction.create_signup_reward(user5.address) # Wallet 50

        Pool.get_instance().add_transaction(signup_tx1)
        Pool.get_instance().add_transaction(signup_tx2)
        Pool.get_instance().add_transaction(signup_tx3)
        Pool.get_instance().add_transaction(signup_tx4)
        Pool.get_instance().add_transaction(signup_tx5)

        # Mine and add a block to confirm signup rewards; ensure miner is not user1 to avoid double-funding user1
        from services.difficulty_service import DifficultyService, MAX_TARGET
        with patch.object(DifficultyService, "current_difficulty", MAX_TARGET), \
             patch.object(DifficultyService, "update_time_to_mine", autospec=True) as upd_mock:
            upd_mock.return_value = None
            funding_block = Block.mine_with_transactions(
                miner=user5,
                transactions=[signup_tx1, signup_tx2, signup_tx3, signup_tx4, signup_tx5]
            )
        Ledger.get_instance().add_block(funding_block)

        invalid_transaction1 = Transaction.create(user1, user2.address, Decimal(100), Decimal(0.1))
        invalid_transaction2 = Transaction.create(user1, user2.address, Decimal(50), Decimal(0.1))
        valid_transaction1 = Transaction.create(user4, user5.address, Decimal(10), Decimal(0.1))
        valid_transaction2 = Transaction.create(user1, user2.address, Decimal(49.9), Decimal(0.1))
        valid_transaction3 = Transaction.create(user3, user4.address, Decimal(40), Decimal(0.1))

        valid_transaction1.validate()
        valid_transaction2.validate()
        valid_transaction3.validate()

        with pytest.raises(InsufficientBalanceException):
            invalid_transaction1.validate()

        with pytest.raises(InsufficientBalanceException):
            invalid_transaction2.validate()

        Pool.get_instance().add_transaction(valid_transaction1)
        Pool.get_instance().add_transaction(valid_transaction2)

        # Invalid because user4 already spent 10.1 and this transaction is in the pool
        # User4 also receives 40 in valid_transaction3, but that is not yet confirmed in the ledger
        invalid_transaction3 = Transaction.create(user4, user3.address, Decimal(40), Decimal(0))

        with pytest.raises(InsufficientBalanceException):
            invalid_transaction3.validate()


    @pytest.mark.skip(reason="TODO")
    def test_flagged_invalid_transaction_is_canceled_on_creator_login(self):
        """
        When creator of a flagged transaction logs in:
        The transaction must be automatically canceled and removed from pending state.
        """
        pass


if __name__ == '__main__':
    unittest.main()