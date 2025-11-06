from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from exceptions.mining import InvalidBlockException
from exceptions.transaction import InvalidTransactionException
from .user import User
from .transaction import Transaction


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

    number: int
    previous_hash: str
    timestamp: str
    nonce: int
    version: int

    calculated_hash: Optional[str]
    miner_address: Optional[str]
    merkle_root: Optional[str]
    difficulty: Optional[int]

    transactions: list[Transaction]

    # TODO: Implement validations

    # id: int
    # previous_hash: str
    # transactions: list[Transaction]
    # timestamp: str = field(default_factory=_now_iso)
    # nonce: int = 0
    # hash: Optional[str] = None
    # miner: Optional[str] = None
    # validators: List[ValidationFlag] = field(default_factory=list)
    # merkle_root: Optional[str] = None
    # version: int = 1
    # difficulty: Optional[int] = None

    def __init__(
            self,
            number: int,
            previous_hash: Optional[str],
            nonce: int,
            miner_address: str,
            version: int,
            difficulty: Optional[int],
            transactions: list[Transaction],
            calculated_hash: Optional[str] = ""
    ):
        self.number = number
        self.previous_hash = previous_hash
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.nonce = nonce
        self.calculated_hash = calculated_hash
        self.miner_address = miner_address
        self.version = version
        self.difficulty = difficulty
        self.transactions = transactions

        # Compute merkle root
        tx_hashes = [tx.to_hash() for tx in transactions]

        from services import CryptographyService
        crypto_service = CryptographyService()
        self.merkle_root = crypto_service.find_merkle_root_for_list(tx_hashes)


    @classmethod
    def mine_with_transactions(
            cls,
            miner: User,
            transactions: list[Transaction]
    ) -> "Block":


        # Validate all transactions
        for tx in transactions:
            try:
                tx.validate()
            except InvalidTransactionException as e:
                raise InvalidBlockException(f"Invalid transaction in block: {e}")

        if not (5 <= len(transactions) <= 10):
            raise InvalidBlockException("Block must contain between 5 and 10 valid transactions.")

        from blockchain.ledger import Ledger
        ledger = Ledger.get_instance()
        previous_block = ledger.get_latest_block()

        block = cls(
            number=1,
            miner_address=miner.address,
            version=1,
            difficulty=0,
            previous_hash=previous_block.hash if previous_block else None,
            nonce=0,
            transactions=transactions
        )

        from services import CryptographyService
        crypto_service = CryptographyService()

        block.hash = crypto_service.sha256_hash(block.canonicalize())

        return block

    def canonicalize(self) -> str:
        transactions = map(lambda tx: tx.canonicalize_with_signature_and_hash(), self.transactions)
        canonicalized_transactions = ":".join(transactions)
        return f"{self.number}|{self.previous_hash}|{self.timestamp}|{self.nonce}|{self.miner_address}|{self.version}|{self.merkle_root}|{self.difficulty}|TRANSACTIONS|{canonicalized_transactions}"


    def from_dict(cls, data: Dict[str, Any]) -> "Block":
        data = data.copy()
        data['validators'] = [ValidationFlag(**vf) for vf in data.get('validators', [])]
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        data = self.__dict__.copy()
        data['validators'] = [vf.__dict__ for vf in self.validators]
        return data
