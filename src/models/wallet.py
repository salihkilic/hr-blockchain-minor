from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

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
    - created_at: ISO UTC timestamp
    """

    address: str
    owner_username: Optional[str] = None
    public_key: Optional[str] = None
    created_at: str = field(default_factory=_now_iso)

    # -----------------
    # Constructor
    # -----------------
    @classmethod
    def from_user(cls, user: User) -> "Wallet":
        return cls(address=user.address, owner_username=user.username, public_key=user.public_key)


