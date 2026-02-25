import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from tests.helpers import create_user


def _build_auth_service(db: AsyncSession) -> AuthService:
    return AuthService(UserRepository(db))


class TestAuthenticate:
    async def test_正しいメールとパスワードで認証が成功すること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        service = _build_auth_service(db_session)

        result = await service.authenticate("tanaka@example.com", "password123")

        assert result.id == user.id
        assert result.email == "tanaka@example.com"
        assert result.role == UserRole.SALES

    async def test_存在しないメールアドレスでUnauthorizedErrorが発生すること(
        self, db_session: AsyncSession
    ):
        await create_user(db_session)
        service = _build_auth_service(db_session)

        with pytest.raises(UnauthorizedError) as exc_info:
            await service.authenticate("notexist@example.com", "password123")

        expected = "メールアドレスまたはパスワードが正しくありません"
        assert exc_info.value.message == expected

    async def test_誤ったパスワードでUnauthorizedErrorが発生すること(
        self, db_session: AsyncSession
    ):
        await create_user(db_session)
        service = _build_auth_service(db_session)

        with pytest.raises(UnauthorizedError) as exc_info:
            await service.authenticate("tanaka@example.com", "wrongpassword")

        expected = "メールアドレスまたはパスワードが正しくありません"
        assert exc_info.value.message == expected
