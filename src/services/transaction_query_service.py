from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Literal

from blockchain import Ledger, Pool
from models import Transaction
from models.block import BlockStatus


Direction = Literal["in", "out"]
Status = Literal["confirmed", "pending"]


@dataclass(frozen=True)
class TransactionView:
    tx: Transaction
    direction: Direction
    status: Status
    block_number: Optional[int] = None
    block_hash: Optional[str] = None


class TransactionQueryService:
    """
    Query utility to fetch a user's transactions.

    Methods return lightweight TransactionView records denoting direction and status.
    """

    @staticmethod
    def _involves_address(tx: Transaction, address: str) -> Optional[Direction]:
        if tx.receiver_address == address:
            return "in"
        if tx.sender_address == address:
            return "out"
        return None

    @classmethod
    def get_confirmed_transactions(cls, address: str) -> List[TransactionView]:
        ledger = Ledger.get_instance()
        views: List[TransactionView] = []

        # Iterate accepted blocks and collect matching txs
        for block in ledger.get_all_blocks():
            if block.status != BlockStatus.ACCEPTED:
                continue
            for tx in block.transactions:
                direction = cls._involves_address(tx, address)
                if direction is None:
                    continue
                views.append(TransactionView(
                    tx=tx,
                    direction=direction,
                    status="confirmed",
                    block_number=block.number,
                    block_hash=block.calculated_hash,
                ))

        # Sort by block_number then tx timestamp
        views.sort(key=lambda v: (v.block_number or -1, cls._parse_ts(v.tx.timestamp)))
        return views

    @classmethod
    def get_pending_transactions(cls, address: str) -> List[TransactionView]:
        pool = Pool.get_instance()
        views: List[TransactionView] = []

        for tx in pool.get_transactions():
            direction = cls._involves_address(tx, address)
            if direction is None:
                continue
            views.append(TransactionView(
                tx=tx,
                direction=direction,
                status="pending",
            ))

        # Sort by tx timestamp
        views.sort(key=lambda v: cls._parse_ts(v.tx.timestamp))
        return views

    @classmethod
    def get_all_transactions(cls, address: str) -> List[TransactionView]:
        confirmed = cls.get_confirmed_transactions(address)
        pending = cls.get_pending_transactions(address)
        all_views = confirmed + pending
        # Sort by (status: confirmed first), then block_number, then timestamp
        status_rank = {"confirmed": 0, "pending": 1}
        all_views.sort(key=lambda v: (
            status_rank[v.status],
            v.block_number if v.block_number is not None else float("inf"),
            cls._parse_ts(v.tx.timestamp),
        ))
        return all_views

    @staticmethod
    def _parse_ts(ts: str) -> float:
        try:
            return datetime.fromisoformat(ts).timestamp()
        except Exception:
            return 0.0

