from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from decimal import Decimal, ROUND_DOWN, getcontext



def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


SUPPORTED_KINDS = {"transfer", "reward"}


@dataclass
class Transaction:
    """
    Account-based transaction model
    """

    receiver_address: str
    amount: Decimal
    fee: Decimal
    sender_address: str = ""
    kind: str = "transfer"
    timestamp: str = field(default_factory=_now_iso)
    message: Optional[str] = None
    sender_public_key: Optional[str] = None
    signature: Optional[str] = None
    txid: Optional[str] = None

    # lifecycle flags
    status: str = "pending"
    flagged_by: Optional[str] = None
    invalid_reason: Optional[str] = None
    block_hash: Optional[str] = None        # assigned when included in block

