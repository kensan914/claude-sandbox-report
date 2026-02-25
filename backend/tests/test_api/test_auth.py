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
    password: str = "password123",
    role: UserRole = UserRole.SALES,
    name: str = "田中太郎",
) -> User:
    """テスト用ユーザーを作成するヘルパー。"""
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def _build_client(
    db_session: AsyncSession, *, token: str | None = None
) -> httpx.AsyncClient:
    """テスト用の非同期HTTPクライアントを構築するヘルパー。"""

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


class TestLogin:
    async def test_正しいメールとパスワードでログインが成功すること(
        self, db_session: AsyncSession
    ):
        await _create_user(db_session)

        async with _build_client(db_session) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "tanaka@example.com", "password": "password123"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["user"]["email"] == "tanaka@example.com"
        assert data["user"]["name"] == "田中太郎"
        assert data["user"]["role"] == "SALES"

    async def test_ログイン成功時にhttpOnly_Cookieが設定されること(
        self, db_session: AsyncSession
    ):
        await _create_user(db_session)

        async with _build_client(db_session) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "tanaka@example.com", "password": "password123"},
            )

        assert response.status_code == status.HTTP_200_OK
        # Set-CookieヘッダーにCookie名が含まれることを確認
        set_cookie = response.headers.get("set-cookie", "")
        assert COOKIE_NAME in set_cookie
        assert "httponly" in set_cookie.lower()

    async def test_MANAGERロールでログインが成功すること(
        self, db_session: AsyncSession
    ):
        await _create_user(
            db_session,
            email="yamada@example.com",
            name="山田部長",
            role=UserRole.MANAGER,
        )

        async with _build_client(db_session) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "yamada@example.com", "password": "password123"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["user"]["role"] == "MANAGER"

    async def test_誤ったパスワードで401エラーが返ること(
        self, db_session: AsyncSession
    ):
        await _create_user(db_session)

        async with _build_client(db_session) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "tanaka@example.com", "password": "wrongpassword"},
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error = response.json()["error"]
        assert error["code"] == "UNAUTHORIZED"
        assert error["message"] == "メールアドレスまたはパスワードが正しくありません"

    async def test_存在しないメールアドレスで401エラーが返ること(
        self, db_session: AsyncSession
    ):
        async with _build_client(db_session) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "notexist@example.com", "password": "password123"},
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error = response.json()["error"]
        assert error["code"] == "UNAUTHORIZED"

    async def test_メールアドレス未入力で422エラーが返ること(
        self, db_session: AsyncSession
    ):
        async with _build_client(db_session) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"password": "password123"},
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_パスワード未入力で422エラーが返ること(
        self, db_session: AsyncSession
    ):
        async with _build_client(db_session) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "tanaka@example.com"},
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_不正なメール形式で422エラーが返ること(
        self, db_session: AsyncSession
    ):
        async with _build_client(db_session) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "invalid-email", "password": "password123"},
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogout:
    async def test_ログアウトで204が返りCookieが削除されること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.post("/api/v1/auth/logout")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Cookieの削除指示が含まれていることを確認
        set_cookie = response.headers.get("set-cookie", "")
        assert COOKIE_NAME in set_cookie

    async def test_未認証でログアウトすると401エラーが返ること(
        self, db_session: AsyncSession
    ):
        async with _build_client(db_session) as client:
            response = await client.post("/api/v1/auth/logout")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetMe:
    async def test_認証済みユーザーの情報が返ること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["id"] == user.id
        assert data["name"] == "田中太郎"
        assert data["email"] == "tanaka@example.com"
        assert data["role"] == "SALES"

    async def test_未認証で401エラーが返ること(self, db_session: AsyncSession):
        async with _build_client(db_session) as client:
            response = await client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_不正なトークンで401エラーが返ること(self, db_session: AsyncSession):
        async with _build_client(db_session, token="invalid-token") as client:
            response = await client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
