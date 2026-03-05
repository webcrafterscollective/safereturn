"""Repository for user persistence operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Data access object for users table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        """Return user by email or None when absent."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        """Return user by primary key."""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, *, email: str, password_hash: str) -> User:
        """Create and persist new user with hashed password."""
        user = User(email=email, password_hash=password_hash)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def create_user_with_role(
        self, *, email: str, password_hash: str, is_admin: bool
    ) -> User:
        """Create user with explicit admin role assignment."""
        user = User(email=email, password_hash=password_hash, is_admin=is_admin)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def count_users(self) -> int:
        """Return total number of users."""
        count = await self.session.scalar(select(func.count()).select_from(User))
        return int(count or 0)

    async def count_admin_users(self) -> int:
        """Return number of accounts with admin role."""
        count = await self.session.scalar(
            select(func.count()).select_from(User).where(User.is_admin.is_(True))
        )
        return int(count or 0)
