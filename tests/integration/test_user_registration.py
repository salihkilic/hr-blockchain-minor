import os
import tempfile
import unittest
import pytest

from exceptions.user import DuplicateUsernameException
from exceptions.user.invalid_user_exception import InvalidUserException
from models import User
from repositories.user import UserRepository
from services import FileSystemService


class UserRegistrationTests(unittest.TestCase):

    def setUp(self):
        """ Set up the test environment before each test case. """
        tmp_path = tempfile.TemporaryDirectory().name
        db_path = os.path.join(tmp_path, FileSystemService.DATA_DIR_NAME, FileSystemService.USERS_DB_FILE_NAME)

        # Create folders
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Create the empty DB file
        open(db_path, 'a').close()

        user_repository = UserRepository(db_path=db_path)
        user_repository.setup_database_structure()
        self.user_repository = user_repository
        self.db_path = db_path

    @pytest.mark.integration
    def test_validation_of_unique_username(self):
        """ A user must provide a unique username when registering in the system. """
        user1 = User.create("testuser_unique",
                            "newpassword456")

        self.user_repository.persist(user1)

        with pytest.raises(DuplicateUsernameException):
            User.create("testuser_unique",
                        "newpassword789",
                        user_db_path=self.db_path
                        )

    @pytest.mark.integration
    def test_validation_of_required_user_fields(self):
        """ A user must provide a unique username and a password when registering in the system. """

        good_user = User.create("valid_user", "valid_password123")

        with pytest.raises(InvalidUserException) as invalid_username_exception:
            no_username = User.create("", "some_password")

        assert invalid_username_exception.value.field == "username"

        with pytest.raises(InvalidUserException) as invalid_password_exception:
            no_password = User.create("some_username", "")

        assert invalid_password_exception.value.field == "password"

    @pytest.mark.skip(reason="TODO")
    def test_signup_reward(self):
        """ A node user will receive 50 coins as a sign-up reward, after registration. """
        pass

    @pytest.mark.integration
    def test_key_creation_on_signup(self):
        """ A unique pair of private key and public key must be created for a node user, after registration. """
        user1 = User.create("testuser_key", "secure_password123")

        assert user1 is not None
        assert hasattr(user1, 'public_key')  # Check if attribute exists on model
        assert user1.public_key is not None  # Check if attribute is not null
        assert hasattr(user1, 'private_key')
        assert user1.private_key is not None


if __name__ == '__main__':
    unittest.main()
