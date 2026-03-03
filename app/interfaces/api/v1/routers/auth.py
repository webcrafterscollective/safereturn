from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.application.use_cases.auth_login import AuthLoginUseCase
from app.application.use_cases.auth_logout import AuthLogoutUseCase
from app.application.use_cases.auth_refresh import AuthRefreshUseCase
from app.application.use_cases.auth_register import AuthRegisterUseCase
from app.interfaces.api.v1.dependencies import AppContainer, get_container, get_current_user_id
from app.interfaces.api.v1.schemas.auth import (
    AuthLoginRequest,
    AuthLogoutResponse,
    AuthRefreshRequest,
    AuthRegisterRequest,
    AuthRegisterResponse,
    AuthTokenPairResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: AuthRegisterRequest, container: AppContainer = Depends(get_container)
) -> AuthRegisterResponse:
    use_case = AuthRegisterUseCase(
        uow=container.new_uow(),
        id_generator=container.id_generator,
        clock=container.clock,
        encryption=container.encryption,
    )
    result = await use_case.execute(email=request.email, phone=request.phone)
    return AuthRegisterResponse(user_id=result.user_id)


@router.post("/login", response_model=AuthTokenPairResponse)
async def login(
    request: AuthLoginRequest, container: AppContainer = Depends(get_container)
) -> AuthTokenPairResponse:
    use_case = AuthLoginUseCase(
        uow=container.new_uow(),
        token_service=container.token_service,
        encryption=container.encryption,
    )
    result = await use_case.execute(
        email_or_phone=request.email_or_phone,
        otp_or_password_stub=request.otp_or_password_stub,
    )
    return AuthTokenPairResponse(
        access_token=result.access_token, refresh_token=result.refresh_token
    )


@router.post("/refresh", response_model=AuthTokenPairResponse)
async def refresh(
    request: AuthRefreshRequest, container: AppContainer = Depends(get_container)
) -> AuthTokenPairResponse:
    use_case = AuthRefreshUseCase(uow=container.new_uow(), token_service=container.token_service)
    result = await use_case.execute(refresh_token=request.refresh_token)
    return AuthTokenPairResponse(
        access_token=result.access_token, refresh_token=result.refresh_token
    )


@router.post("/logout", response_model=AuthLogoutResponse)
async def logout(
    user_id: str = Depends(get_current_user_id),
    container: AppContainer = Depends(get_container),
) -> AuthLogoutResponse:
    use_case = AuthLogoutUseCase(uow=container.new_uow())
    result = await use_case.execute(user_id=user_id)
    return AuthLogoutResponse(success=result.success)
