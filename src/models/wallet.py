from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from blockchain.ledger import Ledger
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

    @property
    def balance(self) -> Decimal:
        """
        Get the balance of this wallet.
        """
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


