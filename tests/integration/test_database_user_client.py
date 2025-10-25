import os
import sqlite3
import pytest

from repositories.user import UserRepository
from models.user import User
from exceptions.user import DuplicateUsernameException


def _initialize_test_db(tmp_path):
    db_path = os.path.join(tmp_path, "users.sqlite3")

    # Create the empty DB file
    open(db_path, 'a').close()

    user_repository = UserRepository(db_path=db_path)
    user_repository.setup_database_structure()
    return db_path, user_repository


@pytest.mark.integration
def test_init_schema_creates_tables(tmp_path):
    db_path, user_repository = _initialize_test_db(tmp_path)

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users','meta') ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        assert set(tables) == {"users", "meta"}
    finally:
        conn.close()

@pytest.mark.integration
def test_create_and_fetch_user_roundtrip(tmp_path):
    db_path, user_repository = _initialize_test_db(tmp_path)

    u = User.create("alice", "s3cret")
    user_repository.persist(u)

    got = user_repository.find_by_username("alice")
    assert got is not None
    assert got.username == "alice"
    assert got.public_key == u.public_key
    assert got.verify_password("s3cret")


@pytest.mark.integration
def test_duplicate_username_raises(tmp_path):
    db_path, user_repository = _initialize_test_db(tmp_path)

    u = User.create("bob", "pw1")
    user_repository.persist(u)
    with pytest.raises(DuplicateUsernameException):
        user_repository.persist(User.create("bob", "pw2"))


@pytest.mark.integration
def test_username_exists(tmp_path):
    db_path, user_repository = _initialize_test_db(tmp_path)

    assert user_repository.username_exists("carol") is False
    user_repository.persist(User.create("carol", "pw"))
    assert user_repository.username_exists("carol") is True


@pytest.mark.integration
def test_update_user_changes_password_and_keys(tmp_path):
    db_path, user_repository = _initialize_test_db(tmp_path)

    u = User.create("dave", "old")
    user_repository.persist(u)
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

    user_repository.update(u)

    got = user_repository.find_by_username("dave")
    assert got is not None
    assert got.verify_password("new") is True
    assert got.verify_password("old") is False
    # public key changed with rotation
    assert got.public_key == u_new.public_key


@pytest.mark.integration
def test_list_users_returns_inserted(tmp_path):
    db_path, user_repository = _initialize_test_db(tmp_path)

    names = {"erin", "frank", "grace"}
    for n in sorted(names):
        user_repository.persist(User.create(n, f"{n}-pw"))
    listed = user_repository.find_all(limit=10, offset=0)
    listed_names = {u.username for u in listed}
    assert names <= listed_names

