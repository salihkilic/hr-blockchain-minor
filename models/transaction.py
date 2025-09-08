from __future__ import annotations
from dataclasses import dataclass, asdict
from time import time
from typing import Dict, Any


@dataclass(slots=True)
class Transaction:
    sender: str
    recipient: str
    amount: float
    timestamp: float

    @classmethod
    def create(cls, sender: str, recipient: str, amount: float) -> 'Transaction':
        return cls(sender=sender, recipient=recipient, amount=amount, timestamp=time())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_compact_dict(self) -> Dict[str, Any]:  # used for hashing to avoid float repr surprises
        return {
            's': self.sender,
            'r': self.recipient,
            'a': round(self.amount, 8),
            't': int(self.timestamp)  # coarse second-level to stabilise hash for demo
        }

