import os
from decimal import Decimal

from blockchain import Ledger, Pool
from exceptions.user import DuplicateUsernameException
from models import User, Transaction, Block
from models.block import BlockStatus
from models.enum import TransactionType
from repositories.user import UserRepository
from services import InitializationService, FileSystemService


def break_ledger():
    block = Ledger.get_instance().get_block_by_number(0)

    receiver_address = "2763b9dec23335612d4bd0fa307dbe4ec1899809b913121f21434645630919bb"

    # Add a signup reward transaction to the genesis block that gives the receiver 1_000_000 coins

    signup_reward_tx = Transaction(
        receiver_address=receiver_address,
        amount=Decimal(1_000_000),
        fee=Decimal(0),
        kind=TransactionType.SIGNUP_REWARD
    )

    block.transactions.append(signup_reward_tx)


    Ledger.force_save()


if __name__ == "__main__":
    break_ledger()