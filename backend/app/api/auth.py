
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user import create_user


from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.user import authenticate_user

from app.core.dependencies import get_current_user
from app.models.user import User



router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    return create_user(db, user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login_user(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
):
    """Authenticate a user and issue a JWT access token."""

    user = authenticate_user(
        db=db,
        email=credentials.email,
        password=credentials.password,
    )

    access_token = create_access_token(
        user_id=str(user.id)
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    """Return the currently authenticated user's profile."""
    return current_user
