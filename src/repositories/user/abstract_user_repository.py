from abc import abstractmethod
from typing import List
from models import User
from repositories.abstract_database_repository import AbstractDatabseRepository


class AbstractUserRepository(AbstractDatabseRepository):

    @abstractmethod
    def persist(self, entity: User) -> None:
        ...

    @abstractmethod
    def find_by_id(self, entity_id: int) -> User:
        ...

    @abstractmethod
    def find_all(self) -> List[User]:
        ...

    @abstractmethod
    def delete(self, entity: User) -> None:
        ...

    @abstractmethod
    def update(self, entity: User) -> None:
        ...