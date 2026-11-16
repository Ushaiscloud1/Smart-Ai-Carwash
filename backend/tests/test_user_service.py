
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user import create_user


def test_create_user_success():
    db = MagicMock()
    db.scalar.return_value = None

    user_data = UserCreate(
        email="TEST@example.com",
        password="SmartWash123!",
        full_name="Test User",
    )

    with patch("app.services.user.hash_password") as mock_hash:
        mock_hash.return_value = "test-hash"
        result = create_user(db, user_data)

    assert isinstance(result, User)
    assert result.email == "test@example.com"
    assert result.hashed_password == "test-hash"
    assert result.full_name == "Test User"

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_duplicate_email_rejected():
    db = MagicMock()
    db.scalar.return_value = User(
        email="test@example.com",
        hashed_password="existing-hash",
        full_name="Existing User",
    )

    user_data = UserCreate(
        email="test@example.com",
        password="SmartWash123!",
        full_name="Test User",
    )

    with pytest.raises(HTTPException) as error:
        create_user(db, user_data)

    assert error.value.status_code == 409
    db.add.assert_not_called()
    db.commit.assert_not_called()
