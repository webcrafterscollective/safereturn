from __future__ import annotations

from dataclasses import dataclass

from app.application.errors import ValidationError
from app.domain.entities.user import User


@dataclass(slots=True)
class AuthRegisterResult:
    user_id: str


class AuthRegisterUseCase:
    def __init__(self, uow, id_generator, clock, encryption) -> None:  # type: ignore[no-untyped-def]
        self._uow = uow
        self._id_generator = id_generator
        self._clock = clock
        self._encryption = encryption

    async def execute(self, email: str | None, phone: str | None) -> AuthRegisterResult:
        if not email and not phone:
            raise ValidationError("email or phone is required")

        async with self._uow:
            user_id = self._id_generator.new_id()
            user = User(
                id=user_id,
                created_at=self._clock.now(),
                email_encrypted=self._encryption.encrypt(email) if email else None,
                phone_encrypted=self._encryption.encrypt(phone) if phone else None,
                email_verified=False,
                phone_verified=False,
                status="active",
                refresh_token_hash=None,
            )
            self._uow.users[user.id] = user
            await self._uow.commit()
            return AuthRegisterResult(user_id=user.id)
