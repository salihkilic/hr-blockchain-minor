from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from decimal import Decimal, ROUND_DOWN, getcontext

from exceptions.transaction import InvalidTransactionException
from models import User, Block
from models.enum import TransactionType
from services import CryptographyService

@dataclass
class Transaction:
    """
    Account-based transaction model
    """
    id: str

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
        self._id = self.cryptography_service.cryptographic_hash(self.as_content_line())

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

        tx_content = transaction.as_content_line()
        transaction.sender_signature = sender.sign(tx_content.encode())

        return transaction


    @classmethod
    def create_mining_reward(
            cls,
            receiver_address: str,
            block: Block
    ):
        # TODO
        #  If there is already a mining reward in the block, raise an error
        #  If there are fees from other transactions in the block, include them in the reward
        pass

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

    def as_content_line(self) -> str:
        return f"{self.kind.value}:{self.sender_address}:{self.receiver_address}:{self.amount}:{self.fee}:{self.timestamp}"

    def validate(self):
        """ Validates the transaction content and signature. Raises exception if invalid. """
        match self.kind:
            case TransactionType.TRANSFER:
                self._validate_transfer()
            case TransactionType.MINING_REWARD:
                self._validate_mining_reward()
            case TransactionType.SIGNUP_REWARD:
                self._validate_signup_reward()
            case _:
                raise ValueError(f"Unknown transaction type: {self.kind}")

    def _validate_transfer(self):
        senders_public_key = self.sender_public_key
        if not senders_public_key:
            raise InvalidTransactionException("Sender's public key is missing.")

        signature = self.sender_signature

        if not signature:
            raise InvalidTransactionException("Transaction signature is missing.")

        valid = self.cryptography_service.validate_signature(
            message=self.as_content_line(),
            signature_b64=signature,
            public_key_pem=senders_public_key
        )

        if not valid:
            raise InvalidTransactionException("Invalid transaction signature.")

    def _validate_mining_reward(self):
        raise NotImplementedError("Mining reward validation not implemented yet.")

    def _validate_signup_reward(self):
        raise NotImplementedError("Signup reward validation not implemented yet.")