"""認証エンドポイント（login / logout / me）。"""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import (
    COOKIE_NAME,
    COOKIE_PATH,
    COOKIE_SAMESITE,
    create_access_token,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from app.schemas.common import DataResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["認証"])


def _get_auth_service(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> AuthService:
    """認証サービスの依存注入。"""
    return AuthService(UserRepository(db))


@router.post("/login", response_model=DataResponse[LoginResponse])
async def login(
    request: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(_get_auth_service),  # noqa: B008
):
    """メール・パスワード認証を行い、httpOnly CookieにJWTを設定する。"""
    user = await auth_service.authenticate(request.email, request.password)

    token = create_access_token(user.id)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=COOKIE_SAMESITE,
        path=COOKIE_PATH,
    )

    user_response = UserResponse.model_validate(user)
    return DataResponse(data=LoginResponse(user=user_response))


@router.post("/logout", status_code=204)
async def logout(
    response: Response,
    _current_user: User = Depends(get_current_user),  # noqa: B008
):
    """Cookieを削除してログアウトする。"""
    response.delete_cookie(
        key=COOKIE_NAME,
        path=COOKIE_PATH,
    )


@router.get("/me", response_model=DataResponse[UserResponse])
async def get_me(
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    """現在のログインユーザー情報を返す。"""
    user_response = UserResponse.model_validate(current_user)
    return DataResponse(data=user_response)
