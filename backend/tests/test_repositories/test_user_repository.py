from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


async def _create_user(
    db: AsyncSession,
    *,
    email: str = "tanaka@example.com",
    role: UserRole = UserRole.SALES,
    name: str = "田中太郎",
) -> User:
    """テスト用ユーザーを作成するヘルパー。"""
    user = User(
        name=name,
        email=email,
        password_hash=hash_password("password123"),
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


class TestFindList:
    async def test_全ユーザーを取得できること(self, db_session: AsyncSession):
        await _create_user(db_session, email="sales@example.com", name="営業A")
        await _create_user(
            db_session,
            email="manager@example.com",
            role=UserRole.MANAGER,
            name="上長A",
        )
        repo = UserRepository(db_session)

        result = await repo.find_list()

        assert len(result) == 2

    async def test_roleで絞り込めること(self, db_session: AsyncSession):
        await _create_user(db_session, email="sales@example.com", name="営業A")
        await _create_user(
            db_session,
            email="manager@example.com",
            role=UserRole.MANAGER,
            name="上長A",
        )
        repo = UserRepository(db_session)

        result = await repo.find_list(role=UserRole.SALES)

        assert len(result) == 1
        assert result[0].role == UserRole.SALES

    async def test_該当なしで空リストが返ること(self, db_session: AsyncSession):
        await _create_user(db_session, email="sales@example.com", name="営業A")
        repo = UserRepository(db_session)

        result = await repo.find_list(role=UserRole.MANAGER)

        assert len(result) == 0


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
