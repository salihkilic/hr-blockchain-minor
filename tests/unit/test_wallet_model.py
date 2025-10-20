from decimal import Decimal
from src.Models import User, Transaction, Wallet


def mk_user(name: str) -> User:
    return User.create(name, name)


def test_wallet_balance_and_can_send():
    alice = mk_user("alice")
    bob = mk_user("bob")

    wa = Wallet.from_user(alice)
    wb = Wallet.from_user(bob)

    # Initial reward of 50 to Alice
    reward = Transaction(
        sender_address="SYSTEM",
        receiver_address=alice.address,
        amount=Decimal("50"),
        fee=Decimal("0"),
        kind="reward",
    )
    ok, _ = reward.validate_basic()
    assert ok is True

    # Alice sends 3.5 + 0.1 fee to Bob
    t1 = Transaction(
        sender_address=alice.address,
        receiver_address=bob.address,
        amount=Decimal("3.5"),
        fee=Decimal("0.1"),
        kind="transfer",
        sender_public_key=alice.public_key,
    )
    t1.sign(alice.private_key)
    ok, _ = t1.validate_basic()
    assert ok is True

    txs = [reward, t1]

    assert wa.compute_balance(txs) == Decimal("46.4")
    assert wb.compute_balance(txs) == Decimal("3.5")

    assert wa.can_send(Decimal("1"), Decimal("0.1"), txs) is True
    assert wa.can_send(Decimal("100"), Decimal("0"), txs) is False
