
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def create_user(db: Session, user_data: UserCreate) -> User:
    # Normalize the email for consistent lookup.
    email = user_data.email.strip().lower()

    # Check whether the email already exists.
    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Hash the password before saving.
    new_user = User(
        email=email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name.strip(),
        is_active=True,
    )

    db.add(new_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    db.refresh(new_user)

    return new_user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    """Authenticate a user using email and password."""

    normalized_email = email.strip().lower()

    user = db.scalar(
        select(User).where(User.email == normalized_email)
    )

    # Use the same error for an unknown email or wrong password.
    if user is None or not verify_password(
        password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    return user

