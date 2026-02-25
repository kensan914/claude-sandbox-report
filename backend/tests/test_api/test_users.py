import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import COOKIE_NAME, create_access_token, hash_password
from app.main import app
from app.models.user import User, UserRole


async def _create_user(
    db: AsyncSession,
    *,
    email: str = "tanaka@example.com",
    role: UserRole = UserRole.SALES,
    name: str = "田中太郎",
) -> User:
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


def _build_client(
    db_session: AsyncSession, *, token: str | None = None
) -> httpx.AsyncClient:
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    cookies = httpx.Cookies()
    if token is not None:
        cookies.set(COOKIE_NAME, token)

    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        cookies=cookies,
    )


class TestGetUsers:
    async def test_MANAGERがユーザー一覧を取得できること(
        self, db_session: AsyncSession
    ):
        manager = await _create_user(
            db_session,
            email="manager@example.com",
            role=UserRole.MANAGER,
            name="山田部長",
        )
        await _create_user(db_session, email="sales@example.com", name="田中太郎")
        token = create_access_token(manager.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/users")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert len(data) == 2

    async def test_roleパラメータでフィルタリングできること(
        self, db_session: AsyncSession
    ):
        manager = await _create_user(
            db_session,
            email="manager@example.com",
            role=UserRole.MANAGER,
            name="山田部長",
        )
        await _create_user(db_session, email="sales@example.com", name="田中太郎")
        token = create_access_token(manager.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/users?role=SALES")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["role"] == "SALES"
        assert data[0]["name"] == "田中太郎"

    async def test_SALESがアクセスすると403エラーが返ること(
        self, db_session: AsyncSession
    ):
        sales = await _create_user(db_session)
        token = create_access_token(sales.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/users")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        error = response.json()["error"]
        assert error["code"] == "FORBIDDEN"

    async def test_未認証で401エラーが返ること(self, db_session: AsyncSession):
        async with _build_client(db_session) as client:
            response = await client.get("/api/v1/users")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_レスポンスにユーザー情報が含まれること(
        self, db_session: AsyncSession
    ):
        manager = await _create_user(
            db_session,
            email="manager@example.com",
            role=UserRole.MANAGER,
            name="山田部長",
        )
        token = create_access_token(manager.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/users")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert len(data) == 1
        user_data = data[0]
        assert user_data["id"] == manager.id
        assert user_data["name"] == "山田部長"
        assert user_data["email"] == "manager@example.com"
        assert user_data["role"] == "MANAGER"
