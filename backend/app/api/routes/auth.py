from datetime import timedelta
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.config import get_settings
from app.core.logging import logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    verify_password,
)
from app.repositories.user_repo import UserRepository
from app.schemas.schemas import RefreshTokenRequest, StandardResponse, TokenResponse, UserLogin, UserOut, UserRegister

router = APIRouter(prefix="/auth", tags=["Authentication"])
user_repo = UserRepository()
settings = get_settings()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: UserRegister) -> TokenResponse:
    """Registers a new user account with email and password."""
    existing = user_repo.find_by_email(req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    user = user_repo.create_user(
        email=req.email,
        password=req.password,
        name=req.name,
    )

    token_data = {
        "sub": user["id"],
        "email": user["email"],
        "name": user["name"],
        "plan": user["plan"],
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    user_out = UserOut(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        plan=user["plan"],
        created_at=user["created_at"],
        is_active=user["is_active"],
        usage_count=user.get("usage_count", 0),
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_out,
    )


@router.post("/login", response_model=TokenResponse)
def login(req: UserLogin) -> TokenResponse:
    """Authenticates user credentials and issues access and refresh tokens."""
    user = user_repo.find_by_email(req.email)
    if not user or not verify_password(req.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    token_data = {
        "sub": user["id"],
        "email": user["email"],
        "name": user["name"],
        "plan": user.get("plan", "free"),
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    user_out = UserOut(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        plan=user.get("plan", "free"),
        created_at=user["created_at"],
        is_active=user.get("is_active", True),
        usage_count=user.get("usage_count", 0),
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_out,
    )


@router.post("/refresh", response_model=Dict[str, str])
def refresh_token(req: RefreshTokenRequest) -> Dict[str, str]:
    """Generates a new access token from a valid refresh token."""
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    sub = payload.get("sub")
    user = user_repo.find_by_id(sub)
    if not user or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
        )

    token_data = {
        "sub": user["id"],
        "email": user["email"],
        "name": user["name"],
        "plan": user.get("plan", "free"),
    }
    new_access_token = create_access_token(token_data)
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout", response_model=StandardResponse[bool])
def logout(current_user: Dict[str, Any] = Depends(get_current_user)) -> StandardResponse[bool]:
    """Logs out user (stateless JWT client discards tokens)."""
    return StandardResponse(success=True, message="Successfully logged out.", data=True)


@router.get("/me", response_model=UserOut)
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)) -> UserOut:
    """Returns current authenticated user profile."""
    user = user_repo.find_by_id(current_user["id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return UserOut(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        plan=user.get("plan", "free"),
        created_at=user["created_at"],
        is_active=user.get("is_active", True),
        usage_count=user.get("usage_count", 0),
    )
