from __future__ import annotations

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import base64
import hashlib
import os


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_password(password: str, salt: str) -> str:
    # SHA256 for hashing, as required by assignment
    h = hashlib.sha256()
    h.update(salt.encode("utf-8"))
    h.update(b":")
    h.update(password.encode("utf-8"))
    return h.hexdigest()


@dataclass
class User:
    """
    User entity as stored in the relational database.
    """

    # ----------------------------
    # Core Properties
    # ----------------------------
    username: str
    password_hash: str
    salt: str
    public_key: str
    private_key: str
    key_type: str
    recovery_phrase: Optional[str] = None
    created_at: str = field(default_factory=_now_iso)

    # ----------------------------
    # Creation & password handling
    # ----------------------------
    @classmethod
    def create(
        cls,
        username: str,
        password: str,
        *,
        recovery_phrase: Optional[str] = None) -> "User":
        """
        Factory method to create a new user with a fresh Ed25519 keypair and hashed password.
        """
        salt = base64.urlsafe_b64encode(os.urandom(16)).decode("ascii")
        password_hash = _hash_password(password, salt)

        # Always generate a real Ed25519 keypair and
        # store as PEM so we don't leak it by logging it or something
        private_key_obj = Ed25519PrivateKey.generate()
        public_key_obj = private_key_obj.public_key()

        private_key_pem = private_key_obj.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
            ).decode("ascii")
        public_key_pem = public_key_obj.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode("ascii")

        key_type = "ed25519-pem"
        public_key = public_key_pem
        private_key = private_key_pem

        return cls(
            username=username,
            password_hash=password_hash,
            salt=salt,
            public_key=public_key,
            private_key=private_key,
            key_type=key_type,
            recovery_phrase=recovery_phrase,
        )

    def verify_password(self, password: str) -> bool:
        return _hash_password(password, self.salt) == self.password_hash

    # -------------
    # Public fields
    # -------------
    @property
    def address(self) -> str:
        """Public account number (SHA256 of public_key)."""
        return hashlib.sha256(self.public_key.encode("utf-8")).hexdigest()

    # ----------
    # Signatures
    # ----------
    def sign(self, message: bytes) -> str:
        """Sign a message using the user's private Ed25519 key. Returns base64 signature."""
        private_key_obj = serialization.load_pem_private_key(
            self.private_key.encode("ascii"), password=None
        )
        signature = private_key_obj.sign(message)
        return base64.b64encode(signature).decode("ascii")

    def verify(self, message: bytes, signature_b64: str) -> bool:
        """Verify a signature against the user's public Ed25519 key."""
        public_key_obj = serialization.load_pem_public_key(self.public_key.encode("ascii"))
        try:
            signature = base64.b64decode(signature_b64.encode("ascii"))
            public_key_obj.verify(signature, message)
            return True
        # TODO SK: narrow exception type(s)?
        except Exception:
            return False

    # ---------
    # String conversion and secrets redaction
    # ---------
    def public_profile(self) -> Dict[str, Any]:
        """Redacted profile safe for display/logging."""
        return {
            "username": self.username,
            "address": self.address,
            "public_key": self.public_key,
            "created_at": self.created_at,
            "key_type": self.key_type,
        }

    def __repr__(self) -> str:  # pragma: no cover - convenience only
        return f"User({self.public_profile()})"
