import os
import pickle

from models.ledger import Ledger
from services import FileSystemService

class LedgerRepository:

    # Static instance of the ledger so all calls return the same instance
    _ledger: Ledger = None

    def __init__(self):

        self.fs_service = FileSystemService()

    def get_ledger(self) -> Ledger | None:
        if LedgerRepository._ledger is None:
            self.load_from_file()
        return LedgerRepository._ledger

    def save_to_file(self) -> None:
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
            pickle.dump(LedgerRepository._ledger, f, pickle.HIGHEST_PROTOCOL)

    def load_from_file(self) -> None:
        """
        Load the ledger from a file.
        """
        # Get the file path
        file_path = self.fs_service.get_data_root()
        file_path = os.path.join(file_path, "ledger.pkl")

        # Load the ledger from the file
        if not self.fs_service.validate_file_exists(file_path):
            # TODO SK: Make this a proper logging statement
            print("Error: Loading ledger from file: File does not exist.")
            return None
        with open(file_path, 'rb') as f:
            LedgerRepository._ledger =  pickle.load(f)
            return None
