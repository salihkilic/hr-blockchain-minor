import os
import pickle
from abc import ABC
from typing import Optional, cast, Any

from services import FileSystemService


class AbstractPickableSingleton(ABC):

    _instance = None
    _fs_service: FileSystemService = FileSystemService()

    def __init__(self, file_path: Optional[str] = None):
        """ Initializes the singleton instance. """
        super().__init__()
        self._file_path = file_path if file_path is not None else os.path.join(
            self._fs_service.get_data_root(), f"{self.__class__.__name__.lower()}.dat")
        self.__class__._instance = self

    @property
    def file_path(self) -> str:
        return self._file_path

    @classmethod
    def create_instance(cls, file_path: Optional[str] = None) -> None:
        """
        Deprecated: Old behavior to create the singleton instance.
        Use get_instance() instead to get or create the instance.
        """
        if cls._instance is not None:
            raise Exception("Instance already created. Use get_instance() to access it.")
        # Delegate to get_instance which will attempt to load from disk or create.
        cls.get_instance(file_path=file_path)

    @classmethod
    def get_instance(cls, file_path: Optional[str] = None):
        """Return the singleton instance for this class.

        It takes the following paths:
        - If the instance does not exist yet, this will attempt to load it from `file_path` (if provided)
        - Else from the default path based on class name.
        - If no on-disk instance exists a new instance is created.
        """
        if cls._instance is not None:
            return cls._instance

        # No instance yet: determine file path to load from.
        chosen_path = file_path
        if chosen_path is None:
            # From class name
            data_root = cls._fs_service.get_data_root()
            chosen_path = os.path.join(data_root, f"{cls.__name__.lower()}.pkl")

        # Try to load from disk if possible
        from_file = cls.load(chosen_path)
        if from_file is not None:
            cls._instance = from_file
            return cls._instance

        # No saved instance found: create a new one and set cls._instance
        return cls(chosen_path)

    @classmethod
    def _save(cls) -> None:
        """Save the entire object to disk."""
        instance = cls.get_instance()
        # Ensure target directory exists
        os.makedirs(os.path.dirname(instance.file_path), exist_ok=True)
        with open(instance.file_path, "wb") as f:
            pickle.dump(instance, cast(Any, f))

    @classmethod
    def load(cls, file_path: Optional[str]) -> Optional["AbstractPickableSingleton"]:
        """Load the object from disk.

        Returns None if file_path is falsy, the file does not exist, or the file
        cannot be unpickled.
        """
        if not file_path:
            return None
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
