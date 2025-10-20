import re
import pytest
from src.Models import Block, ValidationFlag


def make_block(id=0, prev="0"*64, n_tx=5, miner=None):
    txs = list(range(n_tx))  # simple deterministic tx list
    b = Block(id=id, previous_hash=prev, transactions=txs, miner=miner)
    # Ensure initial hash computed for validation without mining
    b.compute_merkle_root()
    b.compute_hash()
    return b


def test_tx_count_rule():
    b_bad_low = make_block(n_tx=4)
    ok, msg = b_bad_low.validate_block(previous_block=None)
    assert ok is False and "transaction count" in msg

    b_bad_high = make_block(n_tx=11)
    ok, msg = b_bad_high.validate_block(previous_block=None)
    assert ok is False

    b_ok = make_block(n_tx=5)
    ok, msg = b_ok.validate_block(previous_block=None)
    assert ok is True


def test_genesis_validation_and_hash_stability():
    b0 = make_block(id=0)
    # Hash must equal recomputed expected
    expected = b0.compute_hash()
    ok, msg = b0.validate_block(previous_block=None)
    assert ok is True
    assert b0.hash == expected


def test_non_genesis_validation_prev_hash_match():
    b0 = make_block(id=0)
    b0.compute_hash()

    b1 = make_block(id=1, prev=b0.hash)
    b1.compute_hash()

    ok, _ = b1.validate_block(previous_block=b0)
    assert ok is True


def test_non_genesis_prev_hash_mismatch_fails():
    b0 = make_block(id=0)
    b0.compute_hash()

    wrong_prev = "f"*64
    b1 = make_block(id=1, prev=wrong_prev)
    b1.compute_hash()

    ok, msg = b1.validate_block(previous_block=b0)
    assert ok is False and "previous_hash" in msg


def test_mining_meets_difficulty_small():
    b = make_block(id=0)
    h, nonce = b.mine(difficulty=2)
    assert h.startswith("00")
    assert b.meets_difficulty(2) is True
    # Validate with current_difficulty 2
    ok, _ = b.validate_block(previous_block=None, difficulty=2)
    assert ok is True


def test_validation_flags_and_state():
    b = make_block(id=0, miner="minerX")
    # Add three accept flags (from different validators)
    b.add_validation_flag("v1", True)
    b.add_validation_flag("v2", True)
    b.add_validation_flag("v3", True)
    assert b.validation_tally() == (3, 0)
    assert b.validation_state() == "accepted"

    # Duplicate vote should fail
    with pytest.raises(ValueError):
        b.add_validation_flag("v1", True)

    # Miner cannot validate own block
    with pytest.raises(ValueError):
        b.add_validation_flag("minerX", True)

    # Rejection path
    b2 = make_block(id=0)
    b2.add_validation_flag("a", False)
    b2.add_validation_flag("b", False)
    b2.add_validation_flag("c", False)
    assert b2.validation_state() == "rejected"


def test_serialization_roundtrip_dict_and_bytes():
    b = make_block(id=0)
    d = b.to_dict(include_transactions=True)
    b2 = Block.from_dict(d)
    # Recompute hash/merkle for b2 since timestamps and nonce match
    b2.compute_merkle_root()
    b2.compute_hash()
    assert b.id == b2.id
    assert b.previous_hash == b2.previous_hash
    assert b.merkle_root == b2.merkle_root

    data = b.to_bytes()
    b3 = Block.from_bytes(data)
    b3.compute_merkle_root()
    b3.compute_hash()
    assert b3.to_dict() == b.to_dict()

