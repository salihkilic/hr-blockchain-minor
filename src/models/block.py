from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import pickle


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    - blocks: list of 5..10 items (dicts or objects with to_dict)
    - timestamp: ISO UTC creation time
    - nonce: PoW nonce
    - hash: block hash (SHA256 of header)
    - miner: creator identifier (username/address)
    - validators: list of ValidationFlag
    - merkle_root: SHA256-based merkle root of blocks
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

