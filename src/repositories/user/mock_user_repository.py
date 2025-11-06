from typing import List, Optional

from exceptions.user import DuplicateUsernameException
from models import User
from repositories.user.abstract_user_repository import AbstractUserRepository
from repositories.database_connection import DatabaseConnection

class MockUserRepository(AbstractUserRepository, DatabaseConnection):

    def __init__(self, db_file_path: Optional[str] = None):
        self.users = {}

    def setup_database_structure(self) -> None:
        pass

    def persist(self, user: User) -> None:
        if user.username in self.users:
            raise DuplicateUsernameException(f"Username '{user.username}' already exists.")
        self.users[user.username] = user

    def find_by_username(self, username: str) -> Optional[User]:
        return self.users.get(username)

    def find_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        return list(self.users.values())[offset:offset + limit]

    def update(self, user: User) -> None:
        if user.username not in self.users:
            raise ValueError(f"User '{user.username}' does not exist.")
        self.users[user.username] = user

    def username_exists(self, username: str) -> bool:
        return username in self.users

    def hydrate(self, row) -> User:
        raise NotImplementedError("Hydrate is a private method and thus not implemented for MockUserRepository.")

    def find_by_id(self, entity_id: int) -> User:
        raise NotImplementedError("Find by ID is not YET implemented for MockUserRepository.")

    def delete(self, entity: User) -> None:
        if entity.username in self.users:
            del self.users[entity.username]


