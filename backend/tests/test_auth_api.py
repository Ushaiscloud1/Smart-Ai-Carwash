
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_user_success():
    fake_user = {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    with patch("app.api.auth.create_user", return_value=fake_user):
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "SmartWash123!",
                "full_name": "Test User",
            },
        )

    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    assert "hashed_password" not in response.json()


def test_register_user_invalid_email():
    response = client.post(
        "/api/auth/register",
        json={
            "email": "invalid-email",
            "password": "SmartWash123!",
            "full_name": "Test User",
        },
    )

    assert response.status_code == 422
