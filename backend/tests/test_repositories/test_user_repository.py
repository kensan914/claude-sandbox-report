from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


async def _create_user(db: AsyncSession) -> User:
    """テスト用ユーザーを作成するヘルパー。"""
    user = User(
        name="田中太郎",
        email="tanaka@example.com",
        password_hash=hash_password("password123"),
        role=UserRole.SALES,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


class TestFindByEmail:
    async def test_存在するメールアドレスでユーザーが取得できること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        repo = UserRepository(db_session)

        result = await repo.find_by_email("tanaka@example.com")

        assert result is not None
        assert result.id == user.id
        assert result.email == "tanaka@example.com"
        assert result.name == "田中太郎"

    async def test_存在しないメールアドレスでNoneが返ること(
        self, db_session: AsyncSession
    ):
        repo = UserRepository(db_session)

        result = await repo.find_by_email("notexist@example.com")

        assert result is None
