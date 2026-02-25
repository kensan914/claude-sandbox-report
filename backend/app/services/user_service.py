"""ユーザーのビジネスロジック層。"""

from app.core.exceptions import ForbiddenError
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_list(
        self,
        *,
        current_user: User,
        role: UserRole | None = None,
    ) -> list[User]:
        """ユーザー一覧を取得する。MANAGERのみアクセス可能。"""
        if current_user.role != UserRole.MANAGER:
            raise ForbiddenError(message="この操作を行う権限がありません")
        return await self.user_repository.find_list(role=role)
