import os
import sqlite3
import pytest

from src.Database import Database, DuplicateUsernameError
from src.Models import User


def make_db(tmp_path):
    db_path = os.path.join(tmp_path, "users.sqlite3")
    db = Database(db_path)
    db.connect()
    db.init_schema()
    return db


@pytest.mark.integration
def test_init_schema_creates_tables(tmp_path):
    db = make_db(tmp_path)
    try:
        conn = sqlite3.connect(db.db_path)
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users','meta') ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        assert set(tables) == {"users", "meta"}
    finally:
        db.close()


@pytest.mark.integration
def test_create_and_fetch_user_roundtrip(tmp_path):
    db = make_db(tmp_path)
    try:
        u = User.create("alice", "s3cret")
        db.insert_user(u)

        got = db.get_user_by_username("alice")
        assert got is not None
        assert got.username == "alice"
        assert got.public_key == u.public_key
        assert got.verify_password("s3cret")
    finally:
        db.close()


@pytest.mark.integration
def test_duplicate_username_raises(tmp_path):
    db = make_db(tmp_path)
    try:
        u1 = User.create("bob", "pw1")
        db.insert_user(u1)
        with pytest.raises(DuplicateUsernameError):
            db.insert_user(User.create("bob", "pw2"))
    finally:
        db.close()


@pytest.mark.integration
def test_username_exists(tmp_path):
    db = make_db(tmp_path)
    try:
        assert db.username_exists("carol") is False
        db.insert_user(User.create("carol", "pw"))
        assert db.username_exists("carol") is True
    finally:
        db.close()


@pytest.mark.integration
def test_update_user_changes_password_and_keys(tmp_path):
    db = make_db(tmp_path)
    try:
        u = User.create("dave", "old")
        db.insert_user(u)
        # Rotate credentials by creating a fresh keypair/hash for the same username
        u_new = User.create("dave", "new")
        # Copy new secrets into existing user object
        u.password_hash = u_new.password_hash
        u.salt = u_new.salt
        u.public_key = u_new.public_key
        u.private_key = u_new.private_key
        u.key_type = u_new.key_type
        # Keep created_at as-is or update (both acceptable); we'll update for test
        u.created_at = u_new.created_at

        db.update_user(u)

        got = db.get_user_by_username("dave")
        assert got is not None
        assert got.verify_password("new") is True
        assert got.verify_password("old") is False
        # public key changed with rotation
        assert got.public_key == u_new.public_key
    finally:
        db.close()


@pytest.mark.integration
def test_list_users_returns_inserted(tmp_path):
    db = make_db(tmp_path)
    try:
        names = {"erin", "frank", "grace"}
        for n in sorted(names):
            db.insert_user(User.create(n, f"{n}-pw"))
        listed = db.list_users(limit=10, offset=0)
        listed_names = {u.username for u in listed}
        assert names <= listed_names
    finally:
        db.close()

