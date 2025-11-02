import os
import sqlite3
import tempfile
import unittest

import pytest

from repositories.user import UserRepository
from models.user import User
from exceptions.user import DuplicateUsernameException
from services import FileSystemService

class TestDatabaseUserClient(unittest.TestCase):

    def setUp(self):
        """ Set up the test environment before each test case. """
        tmp_path = tempfile.TemporaryDirectory().name
        db_path = os.path.join(tmp_path, FileSystemService.DATA_DIR_NAME, FileSystemService.USERS_DB_FILE_NAME)

        # Create folders
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Create the empty DB file
        open(db_path, 'a').close()

        user_repository = UserRepository(db_file_path=db_path)
        user_repository.setup_database_structure()
        self.user_repository = user_repository
        self.db_path = db_path

    @pytest.mark.integration
    def test_init_schema_creates_tables(self):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users','meta') ORDER BY name")
            tables = [r[0] for r in cur.fetchall()]
            assert set(tables) == {"users", "meta"}
        finally:
            conn.close()
    
    @pytest.mark.integration
    def test_create_and_fetch_user_roundtrip(self):
        u = User.create("alice", "s3cret", user_db_path=self.db_path)
        self.user_repository.persist(u)
    
        got = self.user_repository.find_by_username("alice")
        assert got is not None
        assert got.username == "alice"
        assert got.public_key == u.public_key
        assert got.verify_password("s3cret")
    
    
    @pytest.mark.integration
    def test_duplicate_username_raises(self):
        u = User.create("bob", "pw1", user_db_path=self.db_path)
        self.user_repository.persist(u)
        with pytest.raises(DuplicateUsernameException):
            self.user_repository.persist(User.create("bob", "pw2", user_db_path=self.db_path))
    
    
    @pytest.mark.integration
    def test_username_exists(self):
        assert self.user_repository.username_exists("carol") is False
        self.user_repository.persist(User.create("carol", "pw", user_db_path=self.db_path))
        assert self.user_repository.username_exists("carol") is True
    
    
    @pytest.mark.integration
    def test_update_user_changes_password_and_keys(self):
        u = User.create("dave", "old", user_db_path=self.db_path)
        self.user_repository.persist(u)
        # Rotate credentials by creating a fresh keypair/hash for the same username
        u_new = User.create("testnew", "new", user_db_path=self.db_path)
        # Copy new secrets into existing user object
        u.password_hash = u_new.password_hash
        u.salt = u_new.salt
        u.public_key = u_new.public_key
        u.private_key = u_new.private_key
        u.key_type = u_new.key_type
        # Keep created_at as-is or update (both acceptable); we'll update for test
        u.created_at = u_new.created_at
    
        self.user_repository.update(u)
    
        got = self.user_repository.find_by_username("dave")
        assert got is not None
        assert got.verify_password("new") is True
        assert got.verify_password("old") is False
        # public key changed with rotation
        assert got.public_key == u_new.public_key
    
    
    @pytest.mark.integration
    def test_list_users_returns_inserted(self):
        names = {"erin", "frank", "grace"}
        for n in sorted(names):
            self.user_repository.persist(User.create(n, f"{n}-pw", user_db_path=self.db_path))
        listed = self.user_repository.find_all(limit=10, offset=0)
        listed_names = {u.username for u in listed}
        assert names <= listed_names

