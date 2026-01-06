import os
import pickle
import warnings
from abc import ABC
from typing import Optional, cast, Any

from services import FileSystemService, NodeFileSystemService


class AbstractSingleton(ABC):

    _instance = None

    def __init__(self, file_path: Optional[str] = None):
        """ Initializes the singleton instance. """
        super().__init__()
        self.__class__._instance = self

    @classmethod
    def create_instance(cls) -> None:
        """
        Deprecated: Old behavior to create the singleton instance.
        Use get_instance() instead to get or create the instance.
        """
        if cls._instance is not None:
            raise Exception("Instance already created. Use get_instance() to access it.")
        # Delegate to get_instance which will attempt to load from disk or create.
        cls.get_instance()

    @classmethod
    def get_instance(cls):
        """Return the singleton instance for this class.
        """
        if cls._instance is not None:
            return cls._instance
        # No saved instance found: create a new one and set cls._instance
        return cls()

    @classmethod
    def destroy_instance(cls, raise_exception_if_no_instance: bool = False) -> None:
        if cls._instance is None:
            if raise_exception_if_no_instance:
                raise Exception("Instance not initialized. Cannot destroy non-existent instance.")
            return
        cls._instance = None