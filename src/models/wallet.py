from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

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

