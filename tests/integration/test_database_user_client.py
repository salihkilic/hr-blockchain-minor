import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import pytest

from models.constants import FilesAndDirectories
from repositories.user import UserRepository
from models.user import User
from exceptions.user import DuplicateUsernameException
from services import FileSystemService, InitializationService


class TestDatabaseUserClient(unittest.TestCase):

    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def setUp(self, mock_get_data_root):
        FileSystemService.clear_temp_data_root()
        InitializationService.initialize_application()
        self.user_repository = UserRepository()

    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_init_schema_creates_tables(self, mock_get_data_root):
        fs_service = FileSystemService()
        db_path = fs_service.get_data_file_path(FilesAndDirectories.USERS_DB_FILE_NAME)
        
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users','meta') ORDER BY name")
            tables = [r[0] for r in cur.fetchall()]
            assert set(tables) == {"users", "meta"}
        finally:
            conn.close()

    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_create_and_fetch_user_roundtrip(self, mock_get_data_root):
        u = User.create("alice", "s3cret")
        self.user_repository.persist(u)

        got = self.user_repository.find_by_username("alice")
        assert got is not None
        assert got.username == "alice"
        assert got.public_key == u.public_key
        assert got.verify_password("s3cret")

    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_duplicate_username_raises(self, mock_get_data_root):
        u = User.create("bob", "pw1")
        self.user_repository.persist(u)
        with pytest.raises(DuplicateUsernameException):
            self.user_repository.persist(User.create("bob", "pw2"))

    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_username_exists(self, mock_get_data_root):
        assert self.user_repository.username_exists("carol") is False
        self.user_repository.persist(User.create("carol", "pw"))
        assert self.user_repository.username_exists("carol") is True

    @pytest.mark.integration
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_update_user_changes_password_and_keys(self, mock_get_data_root):
        u = User.create("dave", "old")
        self.user_repository.persist(u)
        # Rotate credentials by creating a fresh keypair/hash for the same username
        u_new = User.create("testnew", "new")
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
    @patch("services.filesystem_service.FileSystemService.get_data_root",
           side_effect=FileSystemService.get_temp_data_root)
    def test_list_users_returns_inserted(self, mock_get_data_root):
        names = {"erin", "frank", "grace"}
        for n in sorted(names):
            self.user_repository.persist(User.create(n, f"{n}-pw"))
        listed = self.user_repository.find_all(limit=10, offset=0)
        listed_names = {u.username for u in listed}
        assert names <= listed_names
