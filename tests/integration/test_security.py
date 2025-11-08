import os
import tempfile
import unittest
from unittest.mock import patch

import pytest

from models.constants import FilesAndDirectories
from repositories.user import UserRepository
from services import CryptographyService, InitializationService, FileSystemService


class TestSecurity(unittest.TestCase):

    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def setUp(self, mock_get_data_root):
        FileSystemService.clear_temp_data_root()
        InitializationService.initialize_application()
        self.crypto_service = CryptographyService()
        self.user_repository = UserRepository()

    def test_sha256_is_used_for_hashing(self):
        """
        SHA256 must be used for any hashing in the system.
        """

        # Verify that the CryptographyService produces SHA256 hashes
        test_string = "test_input"
        expected_hash = self.crypto_service.sha256_hash(test_string)

        # Manually create a Sha256 hash using hashlib for comparison
        import hashlib
        actual_hash = hashlib.sha256(test_string.encode('ascii')).hexdigest()

        assert expected_hash == actual_hash

    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_password_is_stored_as_hash(self, mock_get_data_root):
        """
        A password must be saved in the form of a hash in the system.
        """

        from models.user import User

        username = "testuser"
        password = "securepassword123"

        user = User.create(username, password)
        self.user_repository.persist(user)

        # Check our normal assumptions about password storage
        fetched_user = self.user_repository.find_by_username(username)
        assert fetched_user is not None                # User was fetched successfully
        assert fetched_user.password_hash != password  # Password is not stored in plain text
        assert fetched_user.verify_password(password)  # Password can be verified

        # Additionally, check that the password hash matches the expected hash
        expected_hash = self.crypto_service.sha256_hash(fetched_user.salt + ":" + password)
        assert fetched_user.password_hash == expected_hash

    @pytest.mark.skip(reason="TODO")
    def test_user_can_view_private_and_public_key_when_logged_in(self):
        """
        A user must be able to see their private key and public key when logged in.
        """
        pass

    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_username_or_hashed_public_key_is_used_as_account_number(self, mock_get_data_root):
        """
        A username (or hashed unique public key) must be used as the public account number of a user for any transaction.
        """
        from models.user import User

        username = "accountuser"
        password = "anothersecurepassword"

        user = User.create(username, password)
        self.user_repository.persist(user)

        fetched_user = self.user_repository.find_by_username(username)
        assert fetched_user is not None

        # The account number is the username
        account_number = fetched_user.username
        assert account_number == username

        # Alternatively, we can hash the public key to derive an account number
        public_key_hash = self.crypto_service.sha256_hash(fetched_user.public_key)
        assert public_key_hash is not None


if __name__ == '__main__':
    unittest.main()
