from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from repositories.user import UserRepository
from .user import User


@dataclass
class Wallet:
    """
    A simple account-based wallet bound to a user/address.

    - address: 64-hex string (sha256 of user's public key)
    - owner_username: optional, convenience identifier
    - public_key: PEM (for information; signature uses User model)
    """

    address: str
    owner_username: Optional[str] = None
    public_key: Optional[str] = None

    # -----------------
    # Constructor
    # -----------------
    @classmethod
    def from_user(cls, user: User) -> "Wallet":
        return cls(address=user.address, owner_username=user.username, public_key=user.public_key)

    @classmethod
    def from_address(cls, address: str) -> "Wallet":
        user_repository = UserRepository()
        user = user_repository.find_by_address(address)
        if user is None:
            raise ValueError(f"No user found with address: {address}")
        return cls(address=user.address, owner_username=user.username, public_key=user.public_key)

    @property
    def balance(self) -> Decimal:
        """
        Get the balance of this wallet.
        """
        from blockchain import Ledger, Pool
        ledger = Ledger.get_instance()
        balance = Decimal("0.0")

        # Traverse all blocks and transactions to calculate balance
        for block in ledger.get_all_blocks():
            for transaction in block.transactions:
                if transaction.receiver_address == self.address:
                    balance += transaction.amount
                if transaction.sender_address == self.address:
                    balance -= (transaction.amount + transaction.fee)

        return balance

    @property
    def reserved_balance(self) -> Decimal:
        """
        Get the reserved balance of this wallet (amount locked in pending transactions).
        """
        balance = Decimal("0.0")

        from blockchain import Pool
        pool = Pool.get_instance()
        for transaction in pool.get_transactions():
            if transaction.sender_address == self.address:
                balance -= (transaction.amount + transaction.fee)

        return balance


