from __future__ import annotations

import os
import sqlite3
from typing import Optional, List
from src.Models import User


class DuplicateUsernameError(Exception):
    """Raised when attempting to create a user with an existing username."""


class Database:
    """
    Minimal SQLite3 client dedicated to user storage.

    - This database is ONLY for registered users and their credentials/keys.
    - Do NOT store blockchain or pool data here.
    - Passwords are stored as SHA256(salt:password) hash + salt.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        # Default location: <repo_root>/data/users.sqlite3
        if db_path is None:
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
            data_dir = os.path.join(repo_root, "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "users.sqlite3")
        else:
            os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    # --------------
    # Lifecycle
    # --------------
    def connect(self) -> None:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    # --------------
    # Schema
    # --------------
    def init_schema(self) -> None:
        self._require_conn()
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                public_key TEXT NOT NULL,
                private_key TEXT NOT NULL,
                key_type TEXT NOT NULL,
                recovery_phrase TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        # Optional metadata table for future migrations
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    # --------------
    # Helpers
    # --------------
    def _require_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("Database is not connected. Call connect() first.")
        return self._conn

    # --------------
    # User operations
    # --------------
    def insert_user(self, user: User) -> None:
        """Insert a new user. Raises DuplicateUsernameError on conflict."""
        conn = self._require_conn()
        try:
            conn.execute(
                """
                INSERT INTO users(
                    username, password_hash, salt, public_key, private_key, key_type, recovery_phrase, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user.username,
                    user.password_hash,
                    user.salt,
                    user.public_key,
                    user.private_key,
                    user.key_type,
                    user.recovery_phrase,
                    user.created_at,
                ),
            )
            conn.commit()
        except sqlite3.IntegrityError as e:
            # Map UNIQUE constraint violation
            raise DuplicateUsernameError(f"Username already exists: {user.username}") from e

    def get_user_by_username(self, username: str) -> Optional[User]:
        conn = self._require_conn()
        cur = conn.execute(
            "SELECT username, password_hash, salt, public_key, private_key, key_type, recovery_phrase, created_at FROM users WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return User.from_dict(dict(row))

    def username_exists(self, username: str) -> bool:
        conn = self._require_conn()
        cur = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return cur.fetchone() is not None

    def update_user(self, user: User) -> None:
        conn = self._require_conn()
        res = conn.execute(
            """
            UPDATE users
            SET password_hash = ?,
                salt = ?,
                public_key = ?,
                private_key = ?,
                key_type = ?,
                recovery_phrase = ?,
                created_at = ?
            WHERE username = ?
            """,
            (
                user.password_hash,
                user.salt,
                user.public_key,
                user.private_key,
                user.key_type,
                user.recovery_phrase,
                user.created_at,
                user.username,
            ),
        )
        conn.commit()

    def list_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        conn = self._require_conn()
        cur = conn.execute(
            """
            SELECT username, password_hash, salt, public_key, private_key, key_type, recovery_phrase, created_at
            FROM users
            ORDER BY created_at ASC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        rows = cur.fetchall()
        return [User.from_dict(dict(r)) for r in rows]

