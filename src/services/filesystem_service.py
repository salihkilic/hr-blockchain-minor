import os
from typing import Optional, Dict, Any

from exceptions import RequestedDirectoryDoesNotExistException, RequestedFileDoesNotExistException
from models.constants import FilesAndDirectories

import hashlib
import json
import tempfile
import time
from datetime import datetime


class FileSystemService:

    _tmp_data_root: Optional[str] = None

    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = repo_root
        if repo_root is None:
            self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    def initialize_data_files(self):
        self.get_data_file_path(FilesAndDirectories.USERS_DB_FILE_NAME, create_if_missing=True)
        self.get_data_file_path(FilesAndDirectories.POOL_FILE_NAME, create_if_missing=True)
        self.get_data_file_path(FilesAndDirectories.LEDGER_FILE_NAME, create_if_missing=True)

    def get_src_root(self) -> str:
        """ Returns the absolute path to the 'src' directory of the project. """
        data_root = os.path.join(self.repo_root, FilesAndDirectories.SRC_DIR_NAME)
        if not self.validate_directory_exists(data_root):
            raise RequestedDirectoryDoesNotExistException(f"Src root directory does not exist: {data_root}")
        return data_root

    def get_data_root(self, create_if_missing: bool = False) -> str:
        """ Returns the absolute path to the 'data' directory of the project. """
        data_root = os.path.join(self.repo_root, FilesAndDirectories.DATA_DIR_NAME)

        if not self.validate_directory_exists(data_root):
            if create_if_missing:
                os.makedirs(data_root)
            else:
                raise RequestedDirectoryDoesNotExistException(f"Data root directory does not exist: {data_root}")

        return data_root

    def validate_file_exists(self, file_path: str, throw_exception: bool = False) -> bool:
        """ Validates that the specified file exists. Throws an exception if not found, and throw_exception is True. """
        if os.path.isfile(file_path):
            return True
        if throw_exception:
            raise RequestedFileDoesNotExistException(f"File does not exist: {file_path}")
        return False

    def validate_directory_exists(self, dir_path: str, throw_exception: bool = False) -> bool:
        """ Validates that the specified directory exists. Throws an exception if not found, and throw_exception is True. """
        if os.path.isdir(dir_path):
            return True
        if throw_exception:
            raise RequestedDirectoryDoesNotExistException(f"Directory does not exist: {dir_path}")
        return False

    def get_data_file_path(self, data_filename: str, create_if_missing: bool = False) -> str:
        """ Returns the absolute path to the specified file within the data directory. Throws an exception if the data directory does not exist. """
        data_root = self.get_data_root(create_if_missing=create_if_missing)
        data_path = os.path.join(data_root, data_filename)
        if not os.path.exists(data_path):
            if create_if_missing:
                self.create_file(data_path)
            else:
                raise RequestedFileDoesNotExistException(f"File does not exist: {data_path}")
        return data_path

    def get_sql_file_path(self, sql_filename: str) -> str:
        """ Returns the absolute path to the specified SQL file within the src/DatabaseScripts directory. Throws an exception if the directory does not exist. """
        src_root = self.get_src_root()
        sql_dir = os.path.join(src_root, FilesAndDirectories.DATABASE_SCRIPTS_DIR_NAME)
        self.validate_directory_exists(sql_dir, throw_exception=True)
        sql_path = os.path.join(sql_dir, sql_filename)
        self.validate_file_exists(sql_path, throw_exception=True)
        return sql_path

    def create_file(self, file_path: str, throw_exception_if_exists: bool = False):
        """ Creates a file """
        file_path = os.path.abspath(file_path)
        directory = os.path.dirname(file_path)

        if not os.path.isdir(directory):
            raise RequestedDirectoryDoesNotExistException(
                f"Directory does not exist: {directory}"
            )

        if os.path.exists(file_path):
            if throw_exception_if_exists:
                raise IOError(f"File already exists: {file_path}")
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                pass
        except Exception as e:
            # use a safe fallback if file_path is somehow not set
            fp = locals().get('file_path', '<unknown>')
            raise IOError(f"Failed to create file: {fp}") from e

    # ---- File hashing / hash-store methods (SHA-256 only; no env vars) ----

    HASH_STORE_FILE_NAME = "file_hashes.json"
    DEFAULT_HASH_ALGORITHM = "sha256"

    def _format_iso_time(self, ts: float) -> str:
        return datetime.fromtimestamp(ts).isoformat()

    def get_hash_store_path(self) -> str:
        """Return absolute path to data/file_hashes.json (creates data directory if needed)."""
        data_root = self.get_data_root(create_if_missing=True)
        return os.path.join(data_root, self.HASH_STORE_FILE_NAME)

    def compute_file_hash(self, file_path: str) -> str:
        """Compute and return the SHA-256 hex digest of the file at file_path."""
        chunk_size = 8192
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()

    def load_hash_store(self) -> Dict[str, Any]:
        """Load the JSON hash store; return {} if missing or invalid."""
        path = self.get_hash_store_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_hash_store(self, store: Dict[str, Any]) -> None:
        """Atomically save the provided store dict to the hash-store JSON file."""
        path = self.get_hash_store_path()
        dirpath = os.path.dirname(path)
        os.makedirs(dirpath, exist_ok=True)

        fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix=".tmp_hashstore_", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tf:
                json.dump(store, tf, indent=2, sort_keys=True)
                tf.flush()
                os.fsync(tf.fileno())
            os.replace(tmp_path, path)
        except Exception:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
            raise

    def update_hash_for_file(self, data_filename: str) -> Dict[str, Any]:
        """Compute the current hash for the given data file and persist it into the hash store.

        Returns the entry that was stored.
        """

        # Strip any leading directory components from data_filename
        data_filename = os.path.basename(data_filename)

        file_path = self.get_data_file_path(data_filename, create_if_missing=False)
        self.validate_file_exists(file_path, throw_exception=True)

        actual_hash = self.compute_file_hash(file_path)
        size = os.path.getsize(file_path)
        mtime = os.path.getmtime(file_path)

        entry = {
            "algorithm": self.DEFAULT_HASH_ALGORITHM,
            "hash": actual_hash,
            "size": size,
            "mtime": self._format_iso_time(mtime),
            "updated_at": self._format_iso_time(time.time()),
        }

        store = self.load_hash_store()
        store[data_filename] = entry
        self.save_hash_store(store)
        return entry

    def verify_file_hash(self, data_filename: str) -> Dict[str, Any]:
        """Verify a single data file against the stored hash.

        Returns a result dict with keys: 'ok' (bool), 'expected', 'actual', 'reason' (optional).
        """
        store = self.load_hash_store()
        if data_filename not in store:
            return {"ok": False, "reason": "no_stored_hash"}

        expected_entry = store[data_filename]
        expected_hash = expected_entry.get("hash")
        file_path = self.get_data_file_path(data_filename, create_if_missing=False)
        if not os.path.exists(file_path):
            return {"ok": False, "reason": "file_missing"}

        actual_hash = self.compute_file_hash(file_path)

        ok = (actual_hash == expected_hash)
        result = {
            "ok": ok,
            "expected": expected_hash,
            "actual": actual_hash,
            "entry": expected_entry,
        }
        if not ok:
            result["reason"] = "mismatch"
        return result

    def verify_all_data_files(self) -> Dict[str, Dict[str, Any]]:
        """Verify all canonical data files (ledger, pool, users db). Returns mapping filename -> result dict."""
        targets = [
            FilesAndDirectories.LEDGER_FILE_NAME,
            FilesAndDirectories.POOL_FILE_NAME,
            FilesAndDirectories.USERS_DB_FILE_NAME,
        ]
        results: Dict[str, Dict[str, Any]] = {}
        for fn in targets:
            try:
                results[fn] = self.verify_file_hash(fn)
            except RequestedFileDoesNotExistException:
                results[fn] = {"ok": False, "reason": "file_missing"}
        return results

    def initialize_hash_store(self) -> None:
        """Initialize the hash store by computing and storing hashes for all canonical data files."""
        targets = [
            FilesAndDirectories.LEDGER_FILE_NAME,
            FilesAndDirectories.POOL_FILE_NAME,
            FilesAndDirectories.USERS_DB_FILE_NAME,
        ]
        for fn in targets:
            try:
                self.update_hash_for_file(fn)
            except RequestedFileDoesNotExistException:
                pass  # skip missing files

    def can_hash_store_be_initialized(self):
        """ Checks if the has store can be initialized (i.e., all data files exist, but are empty). """
        targets = [
            FilesAndDirectories.LEDGER_FILE_NAME,
            FilesAndDirectories.POOL_FILE_NAME,
            FilesAndDirectories.USERS_DB_FILE_NAME,
        ]
        for fn in targets:
            try:
                file_path = self.get_data_file_path(fn, create_if_missing=False)
                if os.path.getsize(file_path) > 0:
                    return False
            except RequestedFileDoesNotExistException:
                return False
        return True

    def hash_store_exists(self) -> bool:
        """ Checks if a hash store file already exists. """
        path = self.get_hash_store_path()
        return os.path.exists(path)

    @classmethod
    def get_temp_data_root(cls, create_if_missing: bool = False) -> str:
        """ Returns the absolute path to a temporary data directory for testing purposes. """
        if cls._tmp_data_root is not None:
            return cls._tmp_data_root

        import tempfile
        temp_dir = tempfile.TemporaryDirectory().name
        data_root = os.path.join(temp_dir, FilesAndDirectories.DATA_DIR_NAME)
        os.makedirs(data_root, exist_ok=True)
        cls._tmp_data_root = data_root
        return data_root

    @classmethod
    def clear_temp_data_root(cls):
        """ Clears the temporary data root path. """
        cls._tmp_data_root = None
