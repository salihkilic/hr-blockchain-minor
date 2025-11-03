from abc import ABC, abstractmethod


class AbstractDatabaseRepository(ABC):

    @abstractmethod
    def persist(self, entity) -> None:
        ...

    @abstractmethod
    def find_by_id(self, entity_id: int):
        ...

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> list:
        ...

    @abstractmethod
    def delete(self, entity) -> None:
        ...

    @abstractmethod
    def update(self, entity) -> None:
        ...

    @abstractmethod
    def hydrate(self, row) -> object:
        ...
