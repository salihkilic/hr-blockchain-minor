from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import pickle


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stable_bytes(obj: Any) -> bytes:
    """
    Convert obj into stable bytes for hashing/merkle.
    Stable means that dicts have sorted keys, and objects with to_dict are converted first.
    This way, we produce the same byte representation, given the same object (state).
    """
    def norm(o: Any) -> Any:
        if hasattr(o, "to_dict") and callable(getattr(o, "to_dict")):
            o = o.to_dict()
        if isinstance(o, dict):
            return tuple((k, norm(o[k])) for k in sorted(o.keys()))
        if isinstance(o, (list, tuple)):
            return tuple(norm(x) for x in o)
        return o

    normalized = norm(obj)
    return repr(normalized).encode("utf-8")


def _merkle_root(items: List[Any]) -> str:
    if not items:
        return _sha256_hex(b"")
    level = [hashlib.sha256(_stable_bytes(it)).digest() for it in items]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1]) # duplicate last in uneven tree so we always have symmetric pairs
        next_level: List[bytes] = []
        for i in range(0, len(level), 2):
            next_level.append(hashlib.sha256(level[i] + level[i + 1]).digest())
        level = next_level
    return level[0].hex()


@dataclass
class ValidationFlag:
    validator: str  # username or address
    valid: bool     # True=accept, False=reject
    at: str = field(default_factory=_now_iso)


@dataclass
class Block:
    """
    Blockchain block structure (in-memory model).

    - id: sequential block number (0 for genesis)
    - previous_hash: hex string of previous block hash (64 chars for SHA256)
    - transactions: list of 5..10 items (dicts or objects with to_dict)
    - timestamp: ISO UTC creation time
    - nonce: PoW nonce
    - hash: block hash (SHA256 of header)
    - miner: creator identifier (username/address)
    - validators: list of ValidationFlag
    - merkle_root: SHA256-based merkle root of transactions
    - version: schema version of block structure
    """

    id: int
    previous_hash: str
    transactions: List[Any]
    timestamp: str = field(default_factory=_now_iso)
    nonce: int = 0
    hash: Optional[str] = None
    miner: Optional[str] = None
    validators: List[ValidationFlag] = field(default_factory=list)
    merkle_root: Optional[str] = None
    version: int = 1
    difficulty: Optional[int] = None

    # ------------------
    # Core computations
    # ------------------
    def compute_merkle_root(self) -> str:
        self.merkle_root = _merkle_root(self.transactions)
        return self.merkle_root

    def header_bytes(self) -> bytes:
        merkle = self.merkle_root or self.compute_merkle_root()
        parts = [
            f"id:{self.id}",
            f"prev:{self.previous_hash}",
            f"time:{self.timestamp}",
            f"merkle:{merkle}",
            f"nonce:{self.nonce}",
            f"miner:{self.miner or ''}",
            f"ver:{self.version}",
        ]
        return "|".join(parts).encode("utf-8")

    def compute_hash(self) -> str:
        self.hash = _sha256_hex(self.header_bytes())
        return self.hash

    # --------------
    # Mining & checks
    # --------------
    def tx_count_valid(self) -> bool:
        return 5 <= len(self.transactions) <= 10

    def mine(self, difficulty: int) -> Tuple[str, int]:
        """
        Find a nonce such that block hash has `difficulty` leading zeros in hex.
        Returns (hash, nonce). Difficulty determines expected time externally.
        Also records the difficulty used on this block (self.difficulty).
        """
        assert difficulty >= 0
        self.difficulty = difficulty
        prefix = "0" * difficulty
        # Ensure merkle root computed before mining
        self.compute_merkle_root()
        nonce = self.nonce
        while True:
            self.nonce = nonce
            h = self.compute_hash()
            if h.startswith(prefix):
                return h, nonce
            nonce += 1

    def meets_difficulty(self, difficulty: int) -> bool:
        if self.hash is None:
            return False
        return self.hash.startswith("0" * difficulty)

    # -----------------
    # Validation status
    # -----------------
    def add_validation_flag(self, validator: str, valid: bool) -> None:
        if validator is None or validator == "":
            raise ValueError("validator must be non-empty")
        if self.miner and validator == self.miner:
            raise ValueError("miner cannot validate their own block")
        if any(v.validator == validator for v in self.validators):
            raise ValueError("validator already voted")
        self.validators.append(ValidationFlag(validator=validator, valid=valid))

    def validation_tally(self) -> Tuple[int, int]:
        ok = sum(1 for v in self.validators if v.valid)
        bad = sum(1 for v in self.validators if not v.valid)
        return ok, bad

    def validation_state(self) -> str:
        ok, bad = self.validation_tally()
        if ok >= 3 > bad:
            return "accepted"
        if bad >= 3 > ok:
            return "rejected"
        return "pending"

    # -----------------
    # Structural checks
    # -----------------
    def validate_block(self, previous_block: Optional[Block] = None, *, difficulty: Optional[int] = None) -> Tuple[bool, str]:
        # TX count rule
        if not self.tx_count_valid():
            return False, "invalid transaction count (must be 5..10)"
        # ID rule
        if previous_block is None:
            if self.id != 0:
                return False, "genesis block id must be 0"
        else:
            if self.id != previous_block.id + 1:
                return False, "block id must increment from previous"
            if self.previous_hash != (previous_block.hash or previous_block.compute_hash()):
                return False, "previous_hash mismatch"

        # Hash/current_difficulty rule
        expected = _sha256_hex(self.header_bytes())
        if self.hash != expected:
            return False, "hash does not match header"
        eff_diff = difficulty if difficulty is not None else (self.difficulty or 0)
        if eff_diff > 0 and not self.meets_difficulty(eff_diff):
            return False, "does not meet difficulty"
        return True, "ok"

    # -------------
    # Serialization
    # -------------
    def to_dict(self, include_transactions: bool = True) -> Dict[str, Any]:
        txs: List[Any]
        if include_transactions:
            txs = []
            for t in self.transactions:
                if hasattr(t, "to_dict") and callable(getattr(t, "to_dict")):
                    txs.append(t.to_dict())  # type: ignore[attr-defined]
                else:
                    txs.append(t)
        else:
            txs = []
        return {
            "id": self.id,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "hash": self.hash,
            "miner": self.miner,
            "validators": [
                {"validator": v.validator, "valid": v.valid, "at": v.at}
                for v in self.validators
            ],
            "merkle_root": self.merkle_root,
            "version": self.version,
            "difficulty": self.difficulty,
            "transactions": txs,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Block:
        validators = [ValidationFlag(**v) for v in data.get("validators", [])]
        return cls(
            id=data["id"],
            previous_hash=data["previous_hash"],
            transactions=list(data.get("transactions", [])),
            timestamp=data.get("timestamp", _now_iso()),
            nonce=data.get("nonce", 0),
            hash=data.get("hash"),
            miner=data.get("miner"),
            validators=validators,
            merkle_root=data.get("merkle_root"),
            version=data.get("version", 1),
            difficulty=data.get("difficulty"),
        )

    def to_bytes(self) -> bytes:
        return pickle.dumps(self.to_dict(include_transactions=True), protocol=4)

    @classmethod
    def from_bytes(cls, data: bytes) -> Block:
        return cls.from_dict(pickle.loads(data))
