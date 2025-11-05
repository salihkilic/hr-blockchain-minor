import os
import pickle
import tempfile
import unittest
import pytest

from blockchain import Pool
from exceptions.user import DuplicateUsernameException, InvalidUserException
from models import User, Transaction
from models.enum import TransactionType
from repositories.user import UserRepository
from services import FileSystemService


class UserRegistrationTests(unittest.TestCase):

    def setUp(self):
        """ Set up the test environment before each test case. """
        tmp_path = tempfile.TemporaryDirectory().name
        db_file_path = os.path.join(tmp_path, FileSystemService.DATA_DIR_NAME, FileSystemService.USERS_DB_FILE_NAME)
        pool_file_path = os.path.join(tmp_path, FileSystemService.DATA_DIR_NAME, FileSystemService.POOL_FILE_NAME)

        filesystem_service = FileSystemService(tmp_path)
        filesystem_service.initialize_data_files()

        # Create folders
        os.makedirs(os.path.dirname(db_file_path), exist_ok=True)

        # Create the empty DB file
        open(db_file_path, 'a').close()

        user_repository = UserRepository(db_file_path=db_file_path)
        user_repository.setup_database_structure()

        self.user_repository = user_repository
        self.db_path = db_file_path
        self.pool_file_path = pool_file_path

        Pool.destroy_instance()
        Pool.create_instance(file_path=pool_file_path)

    @pytest.mark.integration
    def test_validation_of_unique_username(self):
        """ A user must provide a unique username when registering in the system. """
        user1 = User.create("testuser_unique",
                            "newpassword456",
                            user_db_path=self.db_path)

        self.user_repository.persist(user1)

        with pytest.raises(DuplicateUsernameException):
            User.create("testuser_unique",
                        "newpassword789",
                        user_db_path=self.db_path
                        )

    @pytest.mark.integration
    def test_validation_of_required_user_fields(self):
        """ A user must provide a unique username and a password when registering in the system. """

        good_user = User.create("valid_user", "valid_password123", user_db_path=self.db_path)

        with pytest.raises(InvalidUserException) as invalid_username_exception:
            no_username = User.create("", "some_password", user_db_path=self.db_path)

        assert invalid_username_exception.value.field == "username"

        with pytest.raises(InvalidUserException) as invalid_password_exception:
            no_password = User.create("some_username", "", user_db_path=self.db_path)

        assert invalid_password_exception.value.field == "password"

    @pytest.mark.integration
    def test_signup_reward(self):
        """ A node user will receive 50 coins as a sign-up reward, after registration. """

        user = User.create("testuser_reward", "strongpassword789", user_db_path=self.db_path)

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
    def test_key_creation_on_signup(self):
        """ A unique pair of private key and public key must be created for a node user, after registration. """
        user1 = User.create("testuser_key", "secure_password123", user_db_path=self.db_path)

        assert user1 is not None
        assert hasattr(user1, 'public_key')  # Check if attribute exists on model
        assert user1.public_key is not None  # Check if attribute is not null
        assert hasattr(user1, 'private_key')
        assert user1.private_key is not None


if __name__ == '__main__':
    unittest.main()
