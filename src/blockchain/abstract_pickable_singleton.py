import os
import pickle
import warnings
from abc import ABC
from typing import Optional, cast, Any

from services import FileSystemService


class AbstractPickableSingleton(ABC):

    _instance = None
    _fs_service: FileSystemService = FileSystemService()

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

        It takes the following paths:
        - If the instance does not exist yet, this will attempt to load it from `file_path` (if provided)
        - Else from the default path based on class name.
        - If no on-disk instance exists a new instance is created.
        """
        if cls._instance is not None:
            return cls._instance

        # Try to load from disk if possible
        from_file = cls.load()
        if from_file is not None:
            cls._instance = from_file
            return cls._instance

        # No saved instance found: create a new one and set cls._instance
        return cls()

    @classmethod
    def _save(cls) -> None:
        """Save the entire object to disk."""
        instance = cls.get_instance()
        # Ensure target directory exists
        file_path = cls._fs_service.get_data_file_path(f"{cls.__name__.lower()}.pkl")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            pickle.dump(instance, cast(Any, f))

    @classmethod
    def load(cls) -> Optional["AbstractPickableSingleton"]:
        """Load the object from disk.

        Returns None if file_path is falsy, the file does not exist, or the file
        cannot be unpickled.
        """
        file_path = cls._fs_service.get_data_file_path(f"{cls.__name__.lower()}.pkl")
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, "rb") as f:
                try:
                    instance = pickle.load(f)
                except EOFError:
                    return None
        except (pickle.UnpicklingError, Exception):
            # If unpickling fails or any IO error occurs, return None so callers
            # can fall back to creating a fresh instance.
            return None
        return instance

    @classmethod
    def destroy_instance(cls, raise_exception_if_no_instance: bool = False) -> None:
        if cls._instance is None:
            if raise_exception_if_no_instance:
                raise Exception("Instance not initialized. Cannot destroy non-existent instance.")
            return
        cls._save()
        cls._instance = None

    @classmethod
    def force_save(cls):
        """ Force saving the current instance to disk. FOR DEBUGGING PURPOSES ONLY. """
        cls._save()
