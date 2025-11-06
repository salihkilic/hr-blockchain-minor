import sqlite3
from typing import List, Optional

from exceptions.user import DuplicateUsernameException
from models import User
from repositories.user.abstract_user_repository import AbstractUserRepository
from repositories.database_connection import DatabaseConnection

# TODO
#  - Centralize duplicate try exception handling
class UserRepository(AbstractUserRepository, DatabaseConnection):

    def __init__(self, db_file_path: Optional[str] = None):
        super().__init__(db_file_path)

    def setup_database_structure(self) -> None:
        self._db_connect()

        meta_table_script = self.FileSystemService.get_sql_file_path("create_meta_table.sql")
        user_table_script = self.FileSystemService.get_sql_file_path("create_user_table.sql")

        with open(user_table_script, 'r') as sql_file:
            user_sql_script = sql_file.read()

        self._db_connection.cursor().executescript(user_sql_script)

        with open(meta_table_script, 'r') as sql_file:
            meta_sql_script = sql_file.read()

        self._db_connection.cursor().executescript(meta_sql_script)
        self._db_connection.commit()

        self._db_close()


    def persist(self, user: User) -> None:
        self._db_connect()

        try:
            self._db_connection.execute(
                """
                INSERT INTO users(
                    username, 
                    password_hash, 
                    salt, 
                    public_key, 
                    private_key, 
                    key_type, 
                    recovery_phrase, 
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
            self._db_connection.commit()
        except sqlite3.IntegrityError:
            self._db_close()
            raise DuplicateUsernameException(f"Username '{user.username}' already exists.")

        self._db_close()

    def find_by_username(self, username: str) -> Optional[User]:
        self._db_connect()

        try:
            cursor = self._db_connection.execute(
                """
                SELECT username,
                       password_hash,
                       salt,
                       public_key,
                       private_key,
                       key_type,
                       recovery_phrase,
                       created_at
                FROM users
                WHERE username = ?
                """,
                (username,), )
            row = cursor.fetchone()
        except Exception as e:
            self._db_close()
            raise e

        self._db_close()

        return self.hydrate(row) if row else None


    def find_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        self._db_connect()

        try:
            cursor = self._db_connection.execute(
                """
                SELECT username,
                       password_hash,
                       salt,
                       public_key,
                       private_key,
                       key_type,
                       recovery_phrase,
                       created_at
                FROM users
                ORDER BY created_at
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )
            rows = cursor.fetchall()
        except Exception as e:
            self._db_close()
            raise e

        self._db_close()

        return [self.hydrate(row) for row in rows]

    def update(self, user: User) -> None:
        self._db_connect()

        try:
            self._db_connection.execute(
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
            self._db_connection.commit()
        except sqlite3.InternalError:
            self._db_close()
            raise ValueError(f"User '{user.username}' does not exist.")

        self._db_close()

    def username_exists(self, username: str) -> bool:
        self._db_connect()

        try:
            cursor = self._db_connection.execute(
                "SELECT 1 FROM users WHERE username = ?",
                (username,),
            )
            exists = cursor.fetchone() is not None
        except Exception as e:
            self._db_close()
            raise e

        self._db_close()
        return exists

    def hydrate(self, row) -> User:
        return User.from_dict(dict(row))

    def find_by_id(self, entity_id: int) -> User:
        raise NotImplementedError("Find by ID is not implemented for UserRepository. (yet")

    def delete(self, entity: User) -> None:
        self._db_connect()
        try:
            self._db_connection.execute(
                "DELETE FROM users WHERE username = ?",
                (entity.username,)
            )
            self._db_connection.commit()
        except Exception as e:
            self._db_close()
            raise e