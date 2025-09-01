# Tx dataclass
from dataclasses import dataclass
from typing import Optional

@dataclass
class Tx:
    hash: str
    frm: str
    to: str
    value: float
    fee: float
    timestamp: float
    status: str  # pending/confirmed
    block_number: Optional[int] = None

