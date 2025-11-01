import unittest
import pytest

from repositories.user.mock_user_repository import MockUserRepository
from services.user_service import UserService


class UserServiceTests(unittest.TestCase):

    def setUp(self):
        """ Set up the test environment before each test case. """
        self.user_service = UserService(MockUserRepository())

    # @pytest.mark.unit
    # def test_create_user_with_valid_credentials(self):
    #     """Happy path: User created successfully with valid credentials."""
    #     # ARRANGE
    #     username = "validuser"
    #     password = "validpass123"
    #
    #     # ACT
    #     user = self.user_service.create_user(username, password)
    #
    #     # ASSERT
    #     assert user is not None, "User should be created successfully"
    #     assert user.username == username, "Username should match"
    #     assert hasattr(user, 'password_hash'), "User should have password_hash"
    #     assert hasattr(user, 'salt'), "User should have salt"
    #     assert hasattr(user, 'public_key'), "User should have public_key"
    #     assert hasattr(user, 'private_key'), "User should have private_key"
    #
    # @pytest.mark.unit
    # def test_create_user_with_empty_username(self):
    #     """Empty username should return None."""
    #     # ARRANGE
    #     username = ""
    #     password = "validpass123"
    #
    #     # ACT
    #     user = self.user_service.create_user(username, password)
    #
    #     # ASSERT
    #     assert user is None, "Should return None for empty username"
    #
    # @pytest.mark.unit
    # def test_create_user_with_empty_password(self):
    #     """Empty password should return None."""
    #     # ARRANGE
    #     username = "validuser"
    #     password = ""
    #
    #     # ACT
    #     user = self.user_service.create_user(username, password)
    #
    #     # ASSERT
    #     assert user is None, "Should return None for empty password"
    #
    # @pytest.mark.unit
    # def test_create_user_with_duplicate_username(self):
    #     """Duplicate username should return None."""
    #     # ARRANGE
    #     username = "duplicateuser"
    #     password = "validpass123"
    #     self.user_service.create_user(username, password)  # Create first user
    #
    #     # ACT
    #     duplicate_user = self.user_service.create_user(username, "anotherpass")
    #
    #     # ASSERT
    #     assert duplicate_user is None, "Should return None for duplicate username"
    #
    # @pytest.mark.unit
    # def test_create_user_with_short_username(self):
    #     """Username less than 3 characters should return None."""
    #     # ARRANGE
    #     username = "ab"  # 2 characters
    #     password = "validpass123"
    #
    #     # ACT
    #     user = self.user_service.create_user(username, password)
    #
    #     # ASSERT
    #     assert user is None, "Should return None for username less than 3 chars"
    #
    # @pytest.mark.unit
    # def test_create_user_with_long_username(self):
    #     """Username more than 30 characters should return None."""
    #     # ARRANGE
    #     username = "a" * 31  # 31 characters
    #     password = "validpass123"
    #
    #     # ACT
    #     user = self.user_service.create_user(username, password)
    #
    #     # ASSERT
    #     assert user is None, "Should return None for username more than 30 chars"
    #
    # @pytest.mark.unit
    # def test_create_user_with_short_password(self):
    #     """Password less than 5 characters should return None."""
    #     # ARRANGE
    #     username = "validuser"
    #     password = "1234"  # 4 characters
    #
    #     # ACT
    #     user = self.user_service.create_user(username, password)
    #
    #     # ASSERT
    #     assert user is None, "Should return None for password less than 5 chars"
    #
    # @pytest.mark.unit
    # def test_create_user_with_long_password(self):
    #     """Password more than 20 characters should return None."""
    #     # ARRANGE
    #     username = "validuser"
    #     password = "a" * 21  # 21 characters
    #
    #     # ACT
    #     user = self.user_service.create_user(username, password)
    #
    #     # ASSERT
    #     assert user is None, "Should return None for password more than 20 chars"
    #
    # @pytest.mark.unit
    # def test_login_with_valid_credentials(self):
    #     """Valid credentials should return User object."""
    #     # ARRANGE
    #     username = "loginuser"
    #     password = "loginpass123"
    #     self.user_service.create_user(username, password)
    #
    #     # ACT
    #     user = self.user_service.login(username, password)
    #
    #     # ASSERT
    #     assert user is not None, "Should return User object for valid credentials"
    #     assert user.username == username, "Username should match"
    #
    # @pytest.mark.unit
    # def test_login_with_invalid_password(self):
    #     """Invalid password should return None."""
    #     # ARRANGE
    #     username = "loginuser"
    #     password = "loginpass123"
    #     self.user_service.create_user(username, password)
    #
    #     # ACT
    #     user = self.user_service.login(username, "wrongpassword")
    #
    #     # ASSERT
    #     assert user is None, "Should return None for invalid password"

    @pytest.mark.unit
    def test_login_with_nonexistent_username(self):
        """Non-existent username should return None."""
        # ARRANGE
        username = "nonexistentuser"
        password = "somepass123"

        # ACT
        user = self.user_service.login(username, password)

        # ASSERT
        assert user is None, "Should return None for non-existent username"

    @pytest.mark.unit
    def test_login_with_empty_username(self):
        """Empty username should return None."""
        # ARRANGE
        username = ""
        password = "validpass123"

        # ACT
        user = self.user_service.login(username, password)

        # ASSERT
        assert user is None, "Should return None for empty username"

    @pytest.mark.unit
    def test_login_with_empty_password(self):
        """Empty password should return None."""
        # ARRANGE
        username = "validuser"
        password = ""

        # ACT
        user = self.user_service.login(username, password)

        # ASSERT
        assert user is None, "Should return None for empty password"

    # @pytest.mark.unit
    # def test_get_user_existing(self):
    #     """Get existing user should return correct User object."""
    #     # ARRANGE
    #     username = "existinguser"
    #     password = "validpass123"
    #     created_user = self.user_service.create_user(username, password)
    #
    #     # ACT
    #     retrieved_user = self.user_service.get_user(username)
    #
    #     # ASSERT
    #     assert retrieved_user is not None, "Should return User object for existing user"
    #     assert retrieved_user.username == username, "Username should match"
    #     assert retrieved_user.username == created_user.username, "Should be the same user"
    #
    # @pytest.mark.unit
    # def test_get_user_nonexistent(self):
    #     """Get non-existent user should return None."""
    #     # ARRANGE
    #     username = "nonexistentuser"
    #
    #     # ACT
    #     user = self.user_service.get_user(username)
    #
    #     # ASSERT
    #     assert user is None, "Should return None for non-existent user"

