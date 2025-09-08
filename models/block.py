from __future__ import annotations

from dataclasses import dataclass, field, asdict
from hashlib import sha256
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - type hint support only
    from .transaction import Transaction


def _calc_hash(index: int, timestamp: float, previous_hash: str, nonce: int, transactions: List["Transaction"]) -> str:
    payload = f"{index}{timestamp}{previous_hash}{nonce}{[t.to_compact_dict() for t in transactions]}".encode()
    return sha256(payload).hexdigest()


@dataclass(slots=True)
class Block:
    index: int
    timestamp: float
    transactions: List["Transaction"]
    previous_hash: str
    nonce: int = 0
    hash: str = field(init=False)

    def __post_init__(self) -> None:
        self.hash = _calc_hash(self.index, self.timestamp, self.previous_hash, self.nonce, self.transactions)

    def mine(self, difficulty_prefix: str = "0000", max_nonce: int = 100_000) -> None:
        """Very small PoW demonstration. Not secure, just educational."""
        while not self.hash.startswith(difficulty_prefix) and self.nonce < max_nonce:
            self.nonce += 1
            self.hash = _calc_hash(self.index, self.timestamp, self.previous_hash, self.nonce, self.transactions)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["transactions"] = [t.to_dict() for t in self.transactions]
        return d
