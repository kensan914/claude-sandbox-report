"""認証のビジネスロジック層。"""

from app.core.exceptions import UnauthorizedError
from app.core.security import verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def authenticate(self, email: str, password: str) -> User:
        """メールアドレスとパスワードで認証を行う。

        認証失敗時は UnauthorizedError を送出する。
        """
        user = await self.user_repository.find_by_email(email)
        if user is None:
            raise UnauthorizedError(
                message="メールアドレスまたはパスワードが正しくありません"
            )

        if not verify_password(password, user.password_hash):
            raise UnauthorizedError(
                message="メールアドレスまたはパスワードが正しくありません"
            )

        return user
