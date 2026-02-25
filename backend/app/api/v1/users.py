"""ユーザーエンドポイント。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.common import DataResponse
from app.schemas.user import UserListItemResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["ユーザー"])


def _get_user_service(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> UserService:
    """ユーザーサービスの依存注入。"""
    return UserService(UserRepository(db))


@router.get("", response_model=DataResponse[list[UserListItemResponse]])
async def get_users(
    role: UserRole | None = Query(default=None),  # noqa: B008
    service: UserService = Depends(_get_user_service),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    """ユーザー一覧を取得する。MANAGERのみアクセス可能。"""
    users = await service.get_list(current_user=current_user, role=role)
    data = [UserListItemResponse.model_validate(u) for u in users]
    return DataResponse(data=data)
