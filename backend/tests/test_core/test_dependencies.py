import httpx
from fastapi import Depends, FastAPI, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.security import COOKIE_NAME, create_access_token, hash_password
from app.models.user import User, UserRole


async def _create_user(db: AsyncSession, *, role: UserRole = UserRole.SALES) -> User:
    """テスト用ユーザーを作成するヘルパー。"""
    user = User(
        name="テストユーザー",
        email=f"test-{role.value.lower()}@example.com",
        password_hash=hash_password("password123"),
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def _build_app(db_session: AsyncSession, *, endpoint_dependency) -> FastAPI:
    """テスト用のFastAPIアプリを構築するヘルパー。"""
    app = FastAPI()

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    @app.get("/test")
    async def _endpoint(
        current_user: User = Depends(endpoint_dependency),  # noqa: B008
    ):
        return {"id": current_user.id, "role": current_user.role}

    return app


def _build_client(app: FastAPI, *, token: str | None = None) -> httpx.AsyncClient:
    """テスト用の非同期HTTPクライアントを構築するヘルパー。"""
    cookies = httpx.Cookies()
    if token is not None:
        cookies.set(COOKIE_NAME, token)
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        cookies=cookies,
    )


class TestGetCurrentUser:
    async def test_有効なトークンでユーザーが取得できること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        token = create_access_token(user_id=user.id)

        app = _build_app(db_session, endpoint_dependency=get_current_user)
        async with _build_client(app, token=token) as client:
            response = await client.get("/test")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == user.id

    async def test_トークンなしで401エラーが返ること(self, db_session: AsyncSession):
        app = _build_app(db_session, endpoint_dependency=get_current_user)
        async with _build_client(app) as client:
            response = await client.get("/test")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_不正なトークンで401エラーが返ること(self, db_session: AsyncSession):
        app = _build_app(db_session, endpoint_dependency=get_current_user)
        async with _build_client(app, token="invalid-token") as client:
            response = await client.get("/test")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_存在しないユーザーIDのトークンで401エラーが返ること(
        self, db_session: AsyncSession
    ):
        token = create_access_token(user_id=99999)

        app = _build_app(db_session, endpoint_dependency=get_current_user)
        async with _build_client(app, token=token) as client:
            response = await client.get("/test")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRequireRole:
    async def test_正しいロールでアクセスできること(self, db_session: AsyncSession):
        user = await _create_user(db_session, role=UserRole.MANAGER)
        token = create_access_token(user_id=user.id)

        app = _build_app(db_session, endpoint_dependency=require_role(UserRole.MANAGER))
        async with _build_client(app, token=token) as client:
            response = await client.get("/test")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["role"] == "MANAGER"

    async def test_異なるロールで403エラーが返ること(self, db_session: AsyncSession):
        user = await _create_user(db_session, role=UserRole.SALES)
        token = create_access_token(user_id=user.id)

        app = _build_app(db_session, endpoint_dependency=require_role(UserRole.MANAGER))
        async with _build_client(app, token=token) as client:
            response = await client.get("/test")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_未認証で401エラーが返ること(self, db_session: AsyncSession):
        app = _build_app(db_session, endpoint_dependency=require_role(UserRole.MANAGER))
        async with _build_client(app) as client:
            response = await client.get("/test")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
