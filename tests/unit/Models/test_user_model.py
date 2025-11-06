import os
import re
import logging
import tempfile
import unittest

from models import User
from models.constants import FilesAndDirectories
from repositories.user import UserRepository


class TestUserModel(unittest.TestCase):

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


    def test_create_sets_expected_fields(self):
        u = User.create("alice", "s3cret", user_db_path=self.db_path)
        assert u.username == "alice"
        assert u.key_type == "ed25519-pem"
        assert "-----BEGIN PUBLIC KEY-----" in u.public_key
        assert "-----BEGIN PRIVATE KEY-----" in u.private_key
        assert isinstance(u.created_at, str)

        # Extra: log the created user details for manual debugging
        logger = logging.getLogger("unit_tests")
        logger.info(f"Created user: {u.username}")
        for field in u.to_dict():
            logger.info(f"  {field}: {u.to_dict()[field]}")


    def test_verify_password_ok_and_fail(self):
        u = User.create("bob", "p@ssw0rd", user_db_path=self.db_path)
        assert u.verify_password("p@ssw0rd") is True
        assert u.verify_password("wrong") is False


    def test_address_is_sha256_of_public_key(self):
        u = User.create("carol", "pw", user_db_path=self.db_path)
        # address must be a 64-char hex string
        assert re.fullmatch(r"[0-9a-f]{64}", u.address)


    def test_sign_and_verify_success_and_failure(self):
        u = User.create("dave", "pw", user_db_path=self.db_path)
        msg = b"hello-goodchain"
        sig = u.sign(msg)
        assert isinstance(sig, str) and len(sig) > 0
        assert u.verify(msg, sig) is True
        assert u.verify(b"tampered", sig) is False


    def test_to_from_dict_roundtrip(self):
        u = User.create("erin", "pw", user_db_path=self.db_path)
        user_dict = u.to_dict()

        u2 = User.from_dict(user_dict)
        assert u2.username == u.username
        assert u2.public_key == u.public_key
        assert u2.private_key == u.private_key
        assert u2.verify_password("pw")
