from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import base64
import hashlib
import pickle
from decimal import Decimal, ROUND_DOWN, getcontext

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# Ensure sufficient precision for monetary amounts
getcontext().prec = 28


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stable_bytes(obj: Any) -> bytes:
    """
    Convert obj into stable bytes for hashing/signing.
    Dict keys are sorted; objects with to_dict are converted first.
    Decimals are stringified with normalized exponent to avoid float drift.
    """
    def norm(o: Any) -> Any:
        if hasattr(o, "to_dict") and callable(getattr(o, "to_dict")):
            o = o.to_dict()
        if isinstance(o, dict):
            return tuple((k, norm(o[k])) for k in sorted(o.keys()))
        if isinstance(o, (list, tuple)):
            return tuple(norm(x) for x in o)
        if isinstance(o, Decimal):
            # Normalize to 8 decimal places (like many crypto amounts)
            return f"{o.quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)}"
        return o

    normalized = norm(obj)
    return repr(normalized).encode("utf-8")


SUPPORTED_KINDS = {"transfer", "reward"}


@dataclass
class Transaction:
    """
    Account-based transaction model.

    Fields:
    - kind: "transfer" (default) or "reward" (system-generated reward; signature may be omitted)
    - sender_address: 64-hex SHA256(public_key) for transfers, or "SYSTEM" for rewards
    - receiver_address: 64-hex address
    - amount: Decimal > 0 for transfer; >= 0 for reward
    - fee: Decimal >= 0 (ignored for reward)
    - timestamp: ISO UTC string
    - message: optional memo
    - sender_public_key: PEM public key for signature verification (for transfer)
    - signature: base64 signature of the transaction core (stable bytes of core dict)
    - txid: hex SHA256 of the transaction core (assigned on creation/compute)
    - version: schema version
    - status: lifecycle marker: pending|included|confirmed|flagged_invalid|canceled
    - flagged_by / invalid_reason: optional metadata when flagged
    """

    receiver_address: str
    amount: Decimal
    fee: Decimal
    # Optional/derived/core metadata
    sender_address: str = ""
    kind: str = "transfer"
    timestamp: str = field(default_factory=_now_iso)
    message: Optional[str] = None
    sender_public_key: Optional[str] = None
    signature: Optional[str] = None
    txid: Optional[str] = None
    version: int = 1

    # lifecycle flags
    status: str = "pending"
    flagged_by: Optional[str] = None
    invalid_reason: Optional[str] = None

    # -----------------
    # Core dict/hash
    # -----------------
    def core_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "kind": self.kind,
            "sender_address": self.sender_address,
            "receiver_address": self.receiver_address,
            "amount": self._q(self.amount),
            "fee": self._q(self.fee),
            "timestamp": self.timestamp,
            "message": self.message or "",
        }

    @staticmethod
    def _q(v: Decimal) -> str:
        # Quantize once for stable hashing
        return f"{v.quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)}"

    def compute_txid(self) -> str:
        self.txid = _sha256_hex(_stable_bytes(self.core_dict()))
        return self.txid

    # -----------------
    # Sign & Verify
    # -----------------
    def sign(self, private_key_pem: str) -> str:
        if self.kind != "reward":
            private_key_obj: Ed25519PrivateKey = serialization.load_pem_private_key(
                private_key_pem.encode("ascii"), password=None)
            msg = _stable_bytes(self.core_dict())
            sig_b = private_key_obj.sign(msg)
            self.signature = base64.b64encode(sig_b).decode("ascii")
            return self.signature
        # reward tx may be unsigned
        self.signature = None
        return ""

    def verify_signature(self, *, public_key_pem: Optional[str] = None) -> bool:
        if self.kind == "reward":
            return True  # TODO SK: further checks? How to handle unsigned reward tx?
        if not self.signature:
            return False
        pk_pem = public_key_pem or self.sender_public_key
        if not pk_pem:
            return False
        try:
            pub = serialization.load_pem_public_key(pk_pem.encode("ascii"))
            sig = base64.b64decode(self.signature)
            pub.verify(sig, _stable_bytes(self.core_dict()))
            return True
        except Exception:
            return False

    # -----------------
    # Validation
    # -----------------
    def validate_basic(self) -> (bool, str):
        if self.kind not in SUPPORTED_KINDS:
            return False, "unsupported kind"
        if not self.receiver_address or not isinstance(self.receiver_address, str):
            return False, "receiver address missing"
        if self.kind == "transfer":
            if not self.sender_address or not isinstance(self.sender_address, str):
                return False, "sender address missing"
            if self.sender_address == self.receiver_address:
                return False, "sender and receiver cannot be the same"
            if self.amount <= Decimal("0"):
                return False, "amount must be > 0"
            if self.fee < Decimal("0"):
                return False, "fee must be >= 0" # TODO SK: from config?
            if not self.verify_signature():
                return False, "invalid or missing signature"
        else:  # reward case
            if self.sender_address and self.sender_address != "SYSTEM":
                return False, "reward sender must be SYSTEM"
            if self.amount < Decimal("0"):
                return False, "reward amount must be >= 0"
            if self.fee != Decimal("0"):
                return False, "reward fee must be 0"
        # txid stable
        self.compute_txid()
        return True, "ok"

    # -----------------
    # Serialization
    # -----------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            **self.core_dict(),
            "sender_public_key": self.sender_public_key,
            "signature": self.signature,
            "txid": self.txid or self.compute_txid(),
            "status": self.status,
            "flagged_by": self.flagged_by,
            "invalid_reason": self.invalid_reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Transaction:
        tx = cls(
            receiver_address=data["receiver_address"],
            amount=Decimal(str(data["amount"])) if not isinstance(data["amount"], Decimal) else data["amount"],
            fee=Decimal(str(data["fee"])) if not isinstance(data["fee"], Decimal) else data["fee"],
            sender_address=data.get("sender_address", ""),
            kind=data.get("kind", "transfer"),
            timestamp=data.get("timestamp", _now_iso()),
            message=data.get("message") or None,
            sender_public_key=data.get("sender_public_key"),
            signature=data.get("signature"),
            txid=data.get("txid"),
            version=int(data.get("version", 1)),
            status=data.get("status", "pending"),
            flagged_by=data.get("flagged_by"),
            invalid_reason=data.get("invalid_reason"),
        )
        # Ensure txid computed for consistency
        if not tx.txid:
            tx.compute_txid()
        return tx

    def to_bytes(self) -> bytes:
        return pickle.dumps(self.to_dict(), protocol=4)

    @classmethod
    def from_bytes(cls, data: bytes) -> Transaction:
        return cls.from_dict(pickle.loads(data))

