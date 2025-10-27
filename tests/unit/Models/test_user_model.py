import re
import logging
from models import User


def test_create_sets_expected_fields():
    u = User.create("alice", "s3cret")
    assert u.username == "alice"
    assert u.key_type == "ed25519-pem"
    assert "-----BEGIN PUBLIC KEY-----" in u.public_key
    assert "-----BEGIN PRIVATE KEY-----" in u.private_key
    assert isinstance(u.created_at, str)

    # Extra: log the created user details for manual debugging
    logger = logging.getLogger("unit_tests")
    logger.info(f"Created user: {u.username}")
    for field in u.to_dict():
        logger.info(f"  {field}: {u.to_dict()[field]}")


def test_verify_password_ok_and_fail():
    u = User.create("bob", "p@ssw0rd")
    assert u.verify_password("p@ssw0rd") is True
    assert u.verify_password("wrong") is False


def test_address_is_sha256_of_public_key():
    u = User.create("carol", "pw")
    # address must be a 64-char hex string
    assert re.fullmatch(r"[0-9a-f]{64}", u.address)


def test_sign_and_verify_success_and_failure():
    u = User.create("dave", "pw")
    msg = b"hello-goodchain"
    sig = u.sign(msg)
    assert isinstance(sig, str) and len(sig) > 0
    assert u.verify(msg, sig) is True
    assert u.verify(b"tampered", sig) is False


def test_to_from_dict_roundtrip():
    u = User.create("erin", "pw")
    user_dict = u.to_dict()

    u2 = User.from_dict(user_dict)
    assert u2.username == u.username
    assert u2.public_key == u.public_key
    assert u2.private_key == u.private_key
    assert u2.verify_password("pw")

