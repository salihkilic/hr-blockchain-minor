from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from decimal import Decimal, ROUND_DOWN, getcontext

from exceptions.transaction import InvalidTransactionException
from .abstract_hashable_model import AbstractHashableModel
from .user import User
from .enum.transaction_type import TransactionType
from services import CryptographyService


@dataclass
class Transaction(AbstractHashableModel):
    """
    Account-based transaction model
    """
    _hash: str

    receiver_address: str

    sender_address: Optional[str]
    sender_public_key: Optional[str]
    sender_signature: Optional[str]

    amount: Decimal
    fee: Decimal

    kind: TransactionType

    # Metadata
    timestamp: str

    def __init__(
            self,
            receiver_address: str,
            amount: Decimal,
            fee: Decimal,
            kind: TransactionType = TransactionType.TRANSFER,
            sender_address: Optional[str] = None,
            sender_public_key: Optional[str] = None,
            sender_signature: Optional[str] = None,
    ):
        cryptography_service = CryptographyService()
        self.cryptography_service = cryptography_service

        self.receiver_address = receiver_address
        self.amount = amount.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)
        self.fee = fee.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)
        self.kind = kind
        self.sender_address = sender_address
        self.sender_public_key = sender_public_key
        self.sender_signature = sender_signature
        self.timestamp = datetime.now(timezone.utc).isoformat()

        # Important that other fields are set before id generation
        self._hash = self.cryptography_service.sha256_hash(self.canonicalize())

    def to_hash(self) -> str:
        return self._hash

    @property
    def hash(self) -> str:
        return self._hash

    @classmethod
    def create(
            cls,
            sender: User,
            receiver_address: str,
            amount: Decimal,
            fee: Decimal,
    ):
        transaction = Transaction(
            sender_address=sender.address,
            sender_public_key=sender.public_key,
            receiver_address=receiver_address,
            amount=amount,
            fee=fee,
        )

        tx_content = transaction.canonicalize()
        transaction.sender_signature = sender.sign(tx_content.encode())

        return transaction

    @classmethod
    def create_mining_reward(
            cls,
            receiver_address: str,
            transactions_to_be_mined: list[Transaction],
    ):
        reward_amount = Decimal(50)  # Base reward

        for tx in transactions_to_be_mined:
            if tx.kind == TransactionType.TRANSFER:
                reward_amount += tx.fee

        return Transaction(
            receiver_address=receiver_address,
            amount=reward_amount,
            fee=Decimal.from_float(0),
            kind=TransactionType.MINING_REWARD,
        )



    @classmethod
    def create_signup_reward(
            cls,
            receiver_address: str
    ):
        return Transaction(
            receiver_address=receiver_address,
            amount=Decimal.from_float(50.0),
            fee=Decimal.from_float(0),
            kind=TransactionType.SIGNUP_REWARD,
        )

    def canonicalize(self) -> str:
        return f"{self.kind.value}|{self.sender_address}|{self.receiver_address}|{self.amount}|{self.fee}|{self.timestamp}"

    def canonicalize_with_signature_and_hash(self) -> str:
        if not self.hash:
            raise ValueError("Transaction hash is not set.")
        if not self.sender_signature:
            raise ValueError("Sender signature is not set.")
        return f"{self.canonicalize()}|{self.sender_signature}|{self.hash}"

    def validate(self, raise_exception: bool = True) -> bool:
        """ Validates the transaction content and signature. Raises exception if invalid. """
        match self.kind:
            case TransactionType.TRANSFER:
                return self._validate_transfer()
            case TransactionType.MINING_REWARD:
                return self._validate_mining_reward()
            case TransactionType.SIGNUP_REWARD:
                return self._validate_signup_reward()
            case _:
                raise ValueError(f"Unknown transaction type: {self.kind}")

    def _validate_transfer(self, raise_exception: bool = True) -> bool:

        # TODO Validate spender has sufficient funds
        # TODO Mark transaction as invalid when necessary

        senders_public_key = self.sender_public_key
        if not senders_public_key:
            if raise_exception:
                raise InvalidTransactionException("Sender's public key is missing.")
            return False

        signature = self.sender_signature

        if not signature:
            if raise_exception:
                raise InvalidTransactionException("Transaction signature is missing.")
            return False

        valid = self.cryptography_service.validate_signature(
            message=self.canonicalize(),
            signature_b64=signature,
            public_key_pem=senders_public_key
        )

        if not valid:
            if raise_exception:
                raise InvalidTransactionException("Invalid transaction signature.")
            return False

        return True

    def _validate_mining_reward(self) -> bool:
        raise NotImplementedError("Mining reward validation not implemented yet.")

    def _validate_signup_reward(self) -> bool:
        raise NotImplementedError("Signup reward validation not implemented yet.")
