import os
import pickle
from abc import ABC
from io import BufferedWriter
from typing import Optional

from services import FileSystemService


class AbstractPickableSingleton(ABC):

    _instance = None

    def __init__(self, file_path: Optional[str] = None):
        """ Initializes the singleton instance. """
        super().__init__()
        self._file_path = file_path
        self.__class__._instance = self

    @property
    def file_path(self) -> str:
        return self._file_path

    @classmethod
    def create_instance(cls, file_path: Optional[str] = None) -> None:
        """ Creates the singleton instance of the class."""
        if cls._instance is not None:
            raise Exception("Instance already created. Use get_instance() to access it.")
        saved_instance = cls.load(file_path)
        if saved_instance is not None:
            cls._instance = saved_instance
        else:
            cls(file_path)

    @classmethod
    def get_instance(cls):
        """ Returns the singleton instance of the class."""
        if cls._instance is None:
            raise Exception("Instance not initialized. Please create an instance first.")
        return cls._instance

    @classmethod
    def _save(cls) -> None:
        """Save the entire object to disk."""
        instance = cls.get_instance()
        with open(instance.file_path, "wb") as f:
            pickle.dump(instance, f)

    @classmethod
    def load(cls, file_path) -> Optional["AbstractPickableSingleton"]:
        """Load the object from disk."""
        with open(file_path, "rb") as f:
            try:
                instance = pickle.load(f)
            except EOFError:
                return None
        return instance

    @classmethod
    def destroy_instance(cls, raise_exception_if_no_instance: bool = False) -> None:
        """Destroys the singleton instance and deletes the associated file."""
        if cls._instance is None:
            if raise_exception_if_no_instance:
                raise Exception("Instance not initialized. Cannot destroy non-existent instance.")
            return
        cls._save()
        cls._instance = None

