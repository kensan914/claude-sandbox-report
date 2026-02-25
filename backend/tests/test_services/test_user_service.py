from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import ForbiddenError
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.services.user_service import UserService


def _make_user(*, role: UserRole = UserRole.MANAGER, user_id: int = 1) -> User:
    """テスト用ユーザーオブジェクトを作成する。"""
    return User(
        id=user_id,
        name="テストユーザー",
        email="test@example.com",
        password_hash=hash_password("password123"),
        role=role,
    )


class TestGetList:
    async def test_MANAGERがユーザー一覧を取得できること(self):
        manager = _make_user(role=UserRole.MANAGER)
        mock_repo = AsyncMock()
        mock_repo.find_list.return_value = [manager]
        service = UserService(mock_repo)

        result = await service.get_list(current_user=manager)

        assert len(result) == 1
        mock_repo.find_list.assert_called_once_with(role=None)

    async def test_roleパラメータが渡されること(self):
        manager = _make_user(role=UserRole.MANAGER)
        mock_repo = AsyncMock()
        mock_repo.find_list.return_value = []
        service = UserService(mock_repo)

        await service.get_list(current_user=manager, role=UserRole.SALES)

        mock_repo.find_list.assert_called_once_with(role=UserRole.SALES)

    async def test_SALESがアクセスするとForbiddenErrorが発生すること(self):
        sales = _make_user(role=UserRole.SALES)
        mock_repo = AsyncMock()
        service = UserService(mock_repo)

        with pytest.raises(ForbiddenError):
            await service.get_list(current_user=sales)

        mock_repo.find_list.assert_not_called()
