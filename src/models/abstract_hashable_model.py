from abc import ABC


class AbstractHashableModel(ABC):

    def to_hash(self) -> str:
        """ Returns the hex hash representation of the object. """
        ...