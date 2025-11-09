from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum

from exceptions.mining import InvalidBlockException
from exceptions.transaction import InvalidTransactionException
from .user import User
from .transaction import Transaction


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class BlockStatus(Enum):
    GENESIS = "genesis"
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass
class ValidationFlag:
    validator: str  # username or address
    valid: bool     # True=accept, False=reject
    at: str = field(default_factory=_now_iso)
    reason: Optional[str] = None


@dataclass
class BlockValidationResult:
    valid: bool
    reasons: List[str]
    invalid_transactions: List[Transaction]


@dataclass
class Block:
    """In-memory blockchain block structure.

    Fields intentionally normalized for later consensus & persistence.
    """

    number: int
    previous_hash: Optional[str]
    timestamp: str
    nonce: int
    version: int
    difficulty: Optional[int]
    miner_address: Optional[str]
    merkle_root: Optional[str]
    calculated_hash: Optional[str]
    transactions: list[Transaction]
    validators: List[ValidationFlag] = field(default_factory=list)
    status: BlockStatus | None = None
    mined_duration: Optional[float] = None  # seconds; populated when PoW is implemented

    # Custom __init__ retained (dataclass will not auto-generate one)
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
        self.miner_address = miner_address
        self.version = version
        self.difficulty = difficulty
        self.transactions = transactions
        self.validators = []
        self.status = None
        self.mined_duration = None

        # Compute merkle root from transaction hashes
        tx_hashes = [tx.to_hash() for tx in transactions]
        from services import CryptographyService
        crypto_service = CryptographyService()
        self.merkle_root = crypto_service.find_merkle_root_for_list(tx_hashes)

        self.calculated_hash = calculated_hash  # may be recomputed after full initialization

    # -----------------
    # Mining / Creation
    # -----------------
    @classmethod
    def mine_with_transactions(
        cls,
        miner: User,
        transactions: list[Transaction]
    ) -> "Block":
        # Validate all transactions first
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

        # Genesis already exists, ensure previous has a hash value (empty string treated as set)
        if previous_block is None:
            raise InvalidBlockException("Previous block not found.")
        if previous_block.calculated_hash is None:
            raise InvalidBlockException("Previous block has no calculated hash.")

        block = cls(
            number=previous_block.number + 1,
            miner_address=miner.address,
            version=1,
            difficulty=0,
            previous_hash=previous_block.calculated_hash,
            nonce=0,
            transactions=transactions
        )

        # Compute final hash
        block.calculated_hash = block.compute_hash()
        # Do not alter ledger/pool here; return the mined block for caller to handle
        return block

    @classmethod
    def create_genesis_block(cls) -> "Block":
        block = cls(
            number=0,
            miner_address="",
            version=1,
            difficulty=0,
            previous_hash=None,
            nonce=0,
            transactions=[]
        )
        block.calculated_hash = block.compute_hash()
        block.status = BlockStatus.ACCEPTED
        return block

    # -----------------
    # Canonical / Hash
    # -----------------
    def canonicalize(self) -> str:
        transactions = map(lambda tx: tx.canonicalize_with_signature_and_hash(), self.transactions)
        canonicalized_transactions = ":".join(transactions)
        return f"{self.number}|{self.previous_hash}|{self.timestamp}|{self.nonce}|{self.miner_address}|{self.version}|{self.merkle_root}|{self.difficulty}|TRANSACTIONS|{canonicalized_transactions}"

    def compute_hash(self) -> str:
        from services import CryptographyService
        crypto_service = CryptographyService()
        return crypto_service.sha256_hash(self.canonicalize())

    # -----------------
    # Validation helpers (Phase 1/2)
    # -----------------
    def validate_structure(self, previous_block: Optional["Block"]) -> tuple[bool, List[str]]:
        reasons: List[str] = []

        # Genesis special case
        if self.number == 0:
            if self.previous_hash is not None:
                reasons.append("Genesis block previous_hash must be None.")
            if len(self.transactions) != 0:
                reasons.append("Genesis block must have 0 transactions.")
        else:
            # Previous block linkage
            if previous_block is None:
                reasons.append("Previous block missing.")
            else:
                if self.previous_hash != previous_block.calculated_hash:
                    reasons.append("previous_hash does not match previous block hash.")
                if self.number != previous_block.number + 1:
                    reasons.append("Block number not sequential.")
            # Transaction count
            if not (5 <= len(self.transactions) <= 10):
                reasons.append("Non-genesis block must have between 5 and 10 transactions.")

        # Merkle root integrity
        from services import CryptographyService
        crypto_service = CryptographyService()
        recomputed_merkle = crypto_service.find_merkle_root_for_list([tx.to_hash() for tx in self.transactions])
        if recomputed_merkle != self.merkle_root:
            reasons.append("Merkle root mismatch.")

        # Hash integrity
        recomputed_hash = self.compute_hash()
        if self.calculated_hash != recomputed_hash:
            reasons.append("Block hash mismatch.")

        return (len(reasons) == 0, reasons)

    def validate_transactions(self) -> tuple[bool, List[str], List[Transaction]]:
        reasons: List[str] = []
        invalid: List[Transaction] = []
        for tx in self.transactions:
            if not tx.validate(raise_exception=False):
                invalid.append(tx)
        if invalid:
            reasons.append(f"{len(invalid)} invalid transactions found.")
        return (len(invalid) == 0, reasons, invalid)

    def validate(self, previous_block: Optional["Block"]) -> BlockValidationResult:
        struct_ok, struct_reasons = self.validate_structure(previous_block)
        tx_ok, tx_reasons, invalid_txs = self.validate_transactions()
        all_reasons = struct_reasons + tx_reasons
        return BlockValidationResult(valid=struct_ok and tx_ok, reasons=all_reasons, invalid_transactions=invalid_txs)

    # -----------------
    # (De)serialization helpers
    # -----------------
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Block":
        data = data.copy()
        data['validators'] = [ValidationFlag(**vf) for vf in data.get('validators', [])]
        block = cls(
            number=data['number'],
            previous_hash=data.get('previous_hash'),
            nonce=data['nonce'],
            miner_address=data.get('miner_address', ''),
            version=data['version'],
            difficulty=data.get('difficulty'),
            transactions=data.get('transactions', []),
            calculated_hash=data.get('calculated_hash', '')
        )
        block.timestamp = data.get('timestamp', block.timestamp)
        block.merkle_root = data.get('merkle_root', block.merkle_root)
        block.validators = data.get('validators', [])
        block.status = data.get('status', block.status)
        block.mined_duration = data.get('mined_duration', block.mined_duration)
        return block

    def to_dict(self) -> Dict[str, Any]:
        data = self.__dict__.copy()
        data['validators'] = [vf.__dict__ for vf in self.validators]
        if isinstance(self.status, BlockStatus):
            data['status'] = self.status.value
        return data
