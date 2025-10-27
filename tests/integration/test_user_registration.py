import unittest
import pytest

from repositories.user.mock_user_repository import MockUserRepository
from services.user_service import UserService


class UserRegistration(unittest.TestCase):

    def setUp(self):
        """ Set up the test environment before each test case. """
        self.user_service = UserService(MockUserRepository())


    def test_validation_of_unique_username(self):
        """ A user must provide a unique username when registering in the system. """
        user1 = self.user_service.create_user("testuser_unique",
                                              "newpassword456")

        # Should return none or raise an exception for duplicate username
        user2 = self.user_service.create_user("testuser_unique",
                                              "newpassword456")

        assert user1 is not None
        assert user2 is None


    def test_validation_of_required_user_fields(self):
        """ A user must provide a unique username and a password when registering in the system. """

        good_user = self.user_service.create_user("validuser",
                                                  "validpassword123")

        no_username = self.user_service.create_user("",
                                                 "somepassword")

        no_password = self.user_service.create_user("someuser",
                                                    "")

        # Assert that good_user is created successfully
        assert good_user is not None

        # Assert that failing cases return None
        assert no_username is None
        assert no_password is None

    @pytest.mark.skip(reason="TODO")
    def test_signup_reward(self):
        """ A node user will receive 50 coins as a sign-up reward, after registration. """
        pass

    def test_key_creation_on_signup(self):
        """ A unique pair of private key and public key must be created for a node user, after registration. """
        user1 = self.user_service.create_user("testuser_key",
                                              "securepassword123")

        assert user1 is not None
        assert hasattr(user1, 'public_key') # Check if attribute exists on model
        assert user1.public_key is not None # Check if attribute is not null
        assert hasattr(user1, 'private_key')
        assert user1.private_key is not None


if __name__ == '__main__':
    unittest.main()
