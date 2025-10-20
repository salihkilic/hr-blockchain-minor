import re
from decimal import Decimal

from src.Models import User, Transaction


def make_user(name: str) -> User:
    return User.create(name, name)


def test_transfer_sign_verify_and_validate_basic():
    sender = make_user("alice")
    receiver = make_user("bob")

    tx = Transaction(
        sender_address=sender.address,
        receiver_address=receiver.address,
        amount=Decimal("3.5"),
        fee=Decimal("0.1"),
        kind="transfer",
        sender_public_key=sender.public_key,
    )
    sig = tx.sign(sender.private_key)
    assert isinstance(sig, str) and len(sig) > 0
    assert tx.verify_signature() is True
    ok, msg = tx.validate_basic()
    assert ok is True

    # txid must be a 64-char hex string
    assert re.fullmatch(r"[0-9a-f]{64}", tx.txid)


def test_invalid_transfer_cases():
    sender = make_user("carol")
    receiver = make_user("dave")

    # Negative amount
    tx1 = Transaction(
        sender_address=sender.address,
        receiver_address=receiver.address,
        amount=Decimal("-1.0"),
        fee=Decimal("0.0"),
        kind="transfer",
        sender_public_key=sender.public_key,
    )
    tx1.sign(sender.private_key)
    ok, msg = tx1.validate_basic()
    assert ok is False and "amount" in msg

    # Negative fee
    tx2 = Transaction(
        sender_address=sender.address,
        receiver_address=receiver.address,
        amount=Decimal("1.0"),
        fee=Decimal("-0.1"),
        kind="transfer",
        sender_public_key=sender.public_key,
    )
    tx2.sign(sender.private_key)
    ok, msg = tx2.validate_basic()
    assert ok is False and "fee" in msg

    # Same sender and receiver
    tx3 = Transaction(
        sender_address=sender.address,
        receiver_address=sender.address,
        amount=Decimal("1.0"),
        fee=Decimal("0.0"),
        kind="transfer",
        sender_public_key=sender.public_key,
    )
    tx3.sign(sender.private_key)
    ok, msg = tx3.validate_basic()
    assert ok is False and "cannot be the same" in msg

    # Missing signature
    tx4 = Transaction(
        sender_address=sender.address,
        receiver_address=receiver.address,
        amount=Decimal("1.0"),
        fee=Decimal("0.0"),
        kind="transfer",
        sender_public_key=sender.public_key,
    )
    ok, msg = tx4.validate_basic()
    assert ok is False and "signature" in msg


def test_reward_transaction_validation():
    miner = make_user("miner")
    # Reward with zero fee is valid without signature
    reward = Transaction(
        sender_address="SYSTEM",
        receiver_address=miner.address,
        amount=Decimal("50"),
        fee=Decimal("0"),
        kind="reward",
    )
    ok, msg = reward.validate_basic()
    assert ok is True

    # Reward with non-zero fee is invalid
    bad_reward = Transaction(
        sender_address="SYSTEM",
        receiver_address=miner.address,
        amount=Decimal("50"),
        fee=Decimal("0.1"),
        kind="reward",
    )
    ok, msg = bad_reward.validate_basic()
    assert ok is False and "fee" in msg


def test_serialization_roundtrip_dict_and_bytes():
    s = make_user("erin")
    r = make_user("frank")
    tx = Transaction(
        sender_address=s.address,
        receiver_address=r.address,
        amount=Decimal("2.3456789"),
        fee=Decimal("0.0001"),
        kind="transfer",
        sender_public_key=s.public_key,
    )
    tx.sign(s.private_key)
    ok, _ = tx.validate_basic()
    assert ok is True

    d = tx.to_dict()
    tx2 = Transaction.from_dict(d)
    assert tx2.to_dict() == d

    b = tx.to_bytes()
    tx3 = Transaction.from_bytes(b)
    assert tx3.to_dict() == d

