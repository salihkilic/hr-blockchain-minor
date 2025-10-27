import os
import pickle

from models.ledger import Ledger
from services import FileSystemService

class LedgerRepository:
    def __init__(self):

        self.fs_service = FileSystemService()

    def save_to_file(self, ledger) -> None:
        """
        Save the ledger to a file.
        """

        # Get the file path
        file_path = self.fs_service.get_data_root()
        file_path = os.path.join(file_path, "ledger.pkl")

        # Create the file if it doesn't exist
        self.fs_service.create_file(file_path)

        # Save the ledger to the file
        with open(file_path, 'wb') as f:
            pickle.dump(ledger, f, pickle.HIGHEST_PROTOCOL)

    def load_from_file(self) -> Ledger | None:
        """
        Load the ledger from a file.
        """
        # Get the file path
        file_path = self.fs_service.get_data_root()
        file_path = os.path.join(file_path, "ledger.pkl")

        # Load the ledger from the file
        if not self.fs_service.validate_file_exists(file_path):
            return None
        with open(file_path, 'rb') as f:
            return pickle.load(f)
