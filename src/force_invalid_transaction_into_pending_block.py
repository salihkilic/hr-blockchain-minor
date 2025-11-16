import os
from decimal import Decimal

from blockchain import Ledger, Pool
from exceptions.user import DuplicateUsernameException
from models import User, Transaction, Block
from models.block import BlockStatus
from models.constants import FilesAndDirectories
from models.enum import TransactionType
from repositories.user import UserRepository
from services import InitializationService, FileSystemService


def force_invalid_transaction_into_pending_block():

    user_repo = UserRepository()
    sender = user_repo.find_by_username('tom')
    receiver = user_repo.find_by_username('emma')

    # Add a signup reward transaction to the genesis block that gives the receiver 1_000_000 coins

    invalid_transaction = Transaction.create(sender, receiver.address, Decimal(.1), Decimal(5))

    invalid_transaction.amount = Decimal(1_000_000_000)  # Invalid amount, assuming this exceeds balance

    Pool.get_instance().add_transaction(invalid_transaction,raise_exception=False)

    Pool.force_save()

    fs_service = FileSystemService()
    fs_service.update_hash_for_file(FilesAndDirectories.POOL_FILE_NAME)


if __name__ == "__main__":
    force_invalid_transaction_into_pending_block()