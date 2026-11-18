
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash
import uuid
from fastapi import HTTPException, status


# Load local environment configuration.
# Production environments can supply JWT_SECRET_KEY directly.
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=False)

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2id."""
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a plaintext password against its stored hash."""
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(user_id: str) -> str:
    """Generate a signed JWT access token for a user."""
    secret_key = os.getenv("JWT_SECRET_KEY")

    if not secret_key or len(secret_key) < 32:
        raise RuntimeError(
            "JWT_SECRET_KEY must be configured with a secure random key."
        )

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access",
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> uuid.UUID:
    """Validate a JWT access token and return its user ID."""

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    secret_key = os.getenv("JWT_SECRET_KEY")

    if not secret_key or len(secret_key) < 32:
        raise RuntimeError(
            "JWT_SECRET_KEY must be configured with a secure random key."
        )

    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "iat", "exp", "type"]},
        )

        if payload.get("type") != "access":
            raise credentials_error

        user_id = payload.get("sub")

        if not isinstance(user_id, str):
            raise credentials_error

        return uuid.UUID(user_id)

    except (jwt.InvalidTokenError, ValueError, TypeError) as exc:
        raise credentials_error from exc
