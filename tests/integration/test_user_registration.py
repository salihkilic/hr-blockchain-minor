import os
import pickle
import tempfile
import unittest
from unittest.mock import patch

import pytest

from blockchain import Pool
from exceptions.user import DuplicateUsernameException, InvalidUserException
from models import User, Transaction
from models.constants import FilesAndDirectories
from models.enum import TransactionType
from repositories.user import UserRepository
from services import FileSystemService, InitializationService


class UserRegistrationTests(unittest.TestCase):

    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def setUp(self, mock_get_data_root):
        FileSystemService.clear_temp_data_root()
        fs_service = FileSystemService()
        InitializationService.initialize_application()
        self.user_repository = UserRepository()
        self.pool_file_path = fs_service.get_data_file_path(FilesAndDirectories.POOL_FILE_NAME)
        Pool.destroy_instance()

    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_validation_of_unique_username(self, mock_get_data_root):
        """ A user must provide a unique username when registering in the system. """
        user1 = User.create("testuser_unique",
                            "newpassword456")

        self.user_repository.persist(user1)

        with pytest.raises(DuplicateUsernameException):
            User.create("testuser_unique",
                        "newpassword789")

    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_validation_of_required_user_fields(self, mock_get_data_root):
        """ A user must provide a unique username and a password when registering in the system. """

        good_user = User.create("valid_user", "valid_password123")

        with pytest.raises(InvalidUserException) as invalid_username_exception:
            no_username = User.create("", "some_password")

        assert invalid_username_exception.value.field == "username"

        with pytest.raises(InvalidUserException) as invalid_password_exception:
            no_password = User.create("some_username", "")

        assert invalid_password_exception.value.field == "password"

    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_signup_reward(self, mock_get_data_root):
        """ A node user will receive 50 coins as a sign-up reward, after registration. """

        user = User.create("testuser_reward", "strongpassword789")

        reward_transaction = Transaction.create_signup_reward(user.address)

        Pool.get_instance().add_transaction(reward_transaction)

        transactions_in_pool = Pool.get_instance().get_transactions()

        assert len(transactions_in_pool) == 1
        # Check if the transaction is indeed a signup reward to the correct address
        assert transactions_in_pool[0].amount == 50
        assert transactions_in_pool[0].receiver_address == user.address
        assert transactions_in_pool[0].kind == TransactionType.SIGNUP_REWARD

        # Fetch the stored instance with pickle
        with open(self.pool_file_path, 'rb') as f:
            stored_pool = pickle.load(f)

        stored_transactions = stored_pool.get_transactions()
        assert len(stored_transactions) == 1
        assert stored_transactions[0].amount == 50
        assert stored_transactions[0].receiver_address == user.address
        assert stored_transactions[0].kind == TransactionType.SIGNUP_REWARD


    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_key_creation_on_signup(self, mock_get_data_root):
        """ A unique pair of private key and public key must be created for a node user, after registration. """
        user1 = User.create("testuser_key", "secure_password123")

        assert user1 is not None
        assert hasattr(user1, 'public_key')  # Check if attribute exists on model
        assert user1.public_key is not None  # Check if attribute is not null
        assert hasattr(user1, 'private_key')
        assert user1.private_key is not None


if __name__ == '__main__':
    unittest.main()
