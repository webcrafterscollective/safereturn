"""Authentication endpoints for login, refresh, and logout."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import get_settings
from app.db.session import get_session
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    payload: LoginRequest, session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    """Authenticate credentials and return access/refresh tokens."""
    service = AuthService(session=session, settings=get_settings())
    user_id = await service.authenticate_user(email=payload.email, password=payload.password)
    return await service.issue_tokens(user_id=user_id)


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest, session: AsyncSession = Depends(get_session)
) -> RegisterResponse:
    """Register a new user account with unique email/password credentials."""
    service = AuthService(session=session, settings=get_settings())
    user_id, email = await service.register_user(email=payload.email, password=payload.password)
    return RegisterResponse(user_id=user_id, email=email)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh(
    payload: RefreshRequest, session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    """Rotate refresh token and issue a new token pair."""
    service = AuthService(session=session, settings=get_settings())
    return await service.refresh_tokens(refresh_token=payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: LogoutRequest, session: AsyncSession = Depends(get_session)) -> None:
    """Revoke provided refresh token."""
    service = AuthService(session=session, settings=get_settings())
    await service.logout(refresh_token=payload.refresh_token)
