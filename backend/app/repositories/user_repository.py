"""ユーザーのデータアクセス層。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_email(self, email: str) -> User | None:
        """メールアドレスでユーザーを取得する。"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def find_list(self, *, role: UserRole | None = None) -> list[User]:
        """ユーザー一覧を取得する。roleで絞り込み可能。"""
        query = select(User)
        if role is not None:
            query = query.where(User.role == role)
        query = query.order_by(User.id.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
