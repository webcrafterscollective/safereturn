"""Authentication dependency helpers for extracting owner identity from JWT."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import ACCESS_TOKEN_TYPE, TokenError, decode_jwt_token
from app.core.settings import get_settings
from app.db.session import get_session
from app.repositories.user_repo import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """Return authenticated user id from bearer access token.

    Raises:
        AppError: If token is missing or invalid.
    """
    if credentials is None:
        raise AppError(
            code="UNAUTHORIZED",
            message="Missing bearer token",
            status_code=401,
        )

    try:
        payload = decode_jwt_token(
            token=credentials.credentials,
            settings=get_settings(),
            expected_type=ACCESS_TOKEN_TYPE,
        )
    except TokenError as exc:
        raise AppError(
            code="UNAUTHORIZED",
            message="Access token is invalid",
            status_code=401,
        ) from exc

    user_id = str(payload.get("sub", ""))
    if not user_id:
        raise AppError(
            code="UNAUTHORIZED",
            message="Access token subject is invalid",
            status_code=401,
        )
    return user_id


def get_optional_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str | None:
    """Return user id if bearer token is present and valid; otherwise None.

    This is useful for endpoints that can be called anonymously but should still
    capture authenticated user context when available.
    """
    if credentials is None:
        return None

    try:
        payload = decode_jwt_token(
            token=credentials.credentials,
            settings=get_settings(),
            expected_type=ACCESS_TOKEN_TYPE,
        )
    except TokenError:
        return None

    user_id = str(payload.get("sub", ""))
    return user_id or None


async def require_admin_user_id(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> str:
    """Ensure current authenticated user has admin permissions."""
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None or not user.is_admin:
        raise AppError(
            code="FORBIDDEN",
            message="Admin access required",
            status_code=403,
        )
    return user_id
