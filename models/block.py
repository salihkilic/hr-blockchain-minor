from dataclasses import dataclass, field
from typing import List
from models.tx import Tx

@dataclass
class Block:
    number: int
    hash: str
    parent_hash: str
    timestamp: float
    ttm: float
    miner: str
    txs: List[Tx] = field(default_factory=list)
    gas_used: int = 0
    gas_limit: int = 30_000_000
    size: int = 0
