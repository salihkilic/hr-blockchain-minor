import os
import tempfile
import unittest
import pytest

from models.constants import FilesAndDirectories
from repositories.user import UserRepository
from services import CryptographyService


class TestSecurity(unittest.TestCase):


    def setUp(self):
        """ Set up the test environment before each test case. """
        tmp_path = tempfile.TemporaryDirectory().name
        db_path = os.path.join(tmp_path, FilesAndDirectories.DATA_DIR_NAME, FilesAndDirectories.USERS_DB_FILE_NAME)

        # Create folders
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Create the empty DB file
        open(db_path, 'a').close()

        user_repository = UserRepository(db_file_path=db_path)
        user_repository.setup_database_structure()
        self.user_repository = user_repository
        self.db_path = db_path
        self.crypto_service = CryptographyService()

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

    def test_password_is_stored_as_hash(self):
        """
        A password must be saved in the form of a hash in the system.
        """

        from models.user import User

        username = "testuser"
        password = "securepassword123"

        user = User.create(username, password, user_db_path=self.db_path)
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

    def test_username_or_hashed_public_key_is_used_as_account_number(self):
        """
        A username (or hashed unique public key) must be used as the public account number of a user for any transaction.
        """
        from models.user import User

        username = "accountuser"
        password = "anothersecurepassword"

        user = User.create(username, password, user_db_path=self.db_path)
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
