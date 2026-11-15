
from app.core.security import hash_password, verify_password


def test_password_hashing():
    password = "SmartWashTest123!"

    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2id$")


def test_correct_password():
    password = "SmartWashTest123!"

    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_incorrect_password():
    password = "SmartWashTest123!"

    hashed = hash_password(password)

    assert verify_password("WrongPassword123!", hashed) is False


def test_same_password_produces_different_hashes():
    password = "SmartWashTest123!"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert verify_password(password, first_hash) is True
    assert verify_password(password, second_hash) is True
