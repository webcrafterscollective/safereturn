"""Authentication dependency helpers for extracting owner identity from JWT."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.errors import AppError
from app.core.security import ACCESS_TOKEN_TYPE, TokenError, decode_jwt_token
from app.core.settings import get_settings

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
