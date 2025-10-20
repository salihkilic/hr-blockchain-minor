from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, Dict, Any, Optional
from decimal import Decimal

from .transaction import Transaction
from .user import User


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Wallet:
    """
    A simple account-based wallet bound to a user/address.

    - address: 64-hex string (sha256 of user's public key)
    - owner_username: optional, convenience identifier
    - public_key: PEM (for information; signature uses User model)
    - created_at: ISO UTC

    The wallet itself does not persist balances; instead it computes them from
    a sequence of transactions (ledger + possibly pool) using account rules:
      balance = sum(received amounts) - sum(sent amounts + fees)
    """

    address: str
    owner_username: Optional[str] = None
    public_key: Optional[str] = None
    created_at: str = field(default_factory=_now_iso)

    # -----------------
    # Constructors
    # -----------------
    @classmethod
    def from_user(cls, user: User) -> "Wallet":
        return cls(address=user.address, owner_username=user.username, public_key=user.public_key)

    # -----------------
    # Balance & validation
    # -----------------
    def compute_balance(self, transactions: Iterable[Transaction]) -> Decimal:
        bal = Decimal("0")

        # TODO SK: How else does one calculate balance? This seems like the most fool-proof way.
        for tx in transactions:
            # TODO SK: skip transactions not yet validated? Or maybe even return a tuple of (current_balance, post_processed_balance)?
            if tx.kind == "transfer":
                if tx.receiver_address == self.address:
                    bal += tx.amount
                if tx.sender_address == self.address:
                    bal -= (tx.amount + tx.fee)
            elif tx.kind == "reward":
                if tx.receiver_address == self.address:
                    bal += tx.amount
        return bal

    def can_send(self, amount: Decimal, fee: Decimal, transactions: Iterable[Transaction]) -> bool:
        if amount <= Decimal("0") or fee < Decimal("0"):
            return False
        bal = self.compute_balance(transactions)
        return bal >= (amount + fee)

    # -----------------
    # Serialization
    # -----------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "address": self.address,
            "owner_username": self.owner_username,
            "public_key": self.public_key,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Wallet":
        return cls(
            address=data["address"],
            owner_username=data.get("owner_username"),
            public_key=data.get("public_key"),
            created_at=data.get("created_at", _now_iso()),
        )

