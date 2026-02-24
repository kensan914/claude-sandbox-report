"""例外ハンドラーの統合テスト。

FastAPIアプリケーションに登録された例外ハンドラーが、
各カスタム例外をAPI仕様書形式のJSONレスポンスに正しく変換することを検証する。
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from app.main import app


@pytest.fixture
def test_client():
    """テスト用HTTPクライアントを返す。"""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestAppErrorHandler:
    """カスタム例外ハンドラーのテスト。"""

    async def test_ValidationErrorが400でAPI仕様書形式のレスポンスを返すこと(
        self, test_client
    ):
        @app.get("/test/validation-error")
        async def _():
            raise ValidationError(
                details=[
                    {"field": "email", "message": "メール形式で入力してください"}
                ]
            )

        async with test_client as client:
            response = await client.get("/test/validation-error")

        assert response.status_code == 400
        body = response.json()
        assert body["error"]["code"] == "VALIDATION_ERROR"
        assert body["error"]["message"] == "入力内容に誤りがあります"
        assert body["error"]["details"][0]["field"] == "email"

    async def test_UnauthorizedErrorが401でAPI仕様書形式のレスポンスを返すこと(
        self, test_client
    ):
        @app.get("/test/unauthorized-error")
        async def _():
            raise UnauthorizedError()

        async with test_client as client:
            response = await client.get("/test/unauthorized-error")

        assert response.status_code == 401
        body = response.json()
        assert body["error"]["code"] == "UNAUTHORIZED"
        assert body["error"]["message"] == "認証が必要です"
        assert "details" not in body["error"]

    async def test_ForbiddenErrorが403でAPI仕様書形式のレスポンスを返すこと(
        self, test_client
    ):
        @app.get("/test/forbidden-error")
        async def _():
            raise ForbiddenError()

        async with test_client as client:
            response = await client.get("/test/forbidden-error")

        assert response.status_code == 403
        body = response.json()
        assert body["error"]["code"] == "FORBIDDEN"
        assert body["error"]["message"] == "この操作を行う権限がありません"

    async def test_NotFoundErrorが404でAPI仕様書形式のレスポンスを返すこと(
        self, test_client
    ):
        @app.get("/test/not-found-error")
        async def _():
            raise NotFoundError()

        async with test_client as client:
            response = await client.get("/test/not-found-error")

        assert response.status_code == 404
        body = response.json()
        assert body["error"]["code"] == "NOT_FOUND"
        assert body["error"]["message"] == "リソースが見つかりません"

    async def test_ConflictErrorが409でAPI仕様書形式のレスポンスを返すこと(
        self, test_client
    ):
        @app.get("/test/conflict-error")
        async def _():
            raise ConflictError(message="指定された日付の日報は既に存在します")

        async with test_client as client:
            response = await client.get("/test/conflict-error")

        assert response.status_code == 409
        body = response.json()
        assert body["error"]["code"] == "CONFLICT"
        assert body["error"]["message"] == "指定された日付の日報は既に存在します"

    async def test_カスタムメッセージがレスポンスに反映されること(self, test_client):
        @app.get("/test/custom-message-error")
        async def _():
            raise ForbiddenError(message="自分の日報のみ編集できます")

        async with test_client as client:
            response = await client.get("/test/custom-message-error")

        assert response.status_code == 403
        body = response.json()
        assert body["error"]["message"] == "自分の日報のみ編集できます"


class TestUnhandledExceptionHandler:
    """予期しない例外ハンドラーのテスト。"""

    async def test_予期しない例外が500でAPI仕様書形式のレスポンスを返すこと(
        self, test_client
    ):
        @app.get("/test/unhandled-error")
        async def _():
            raise RuntimeError("予期しないエラー")

        async with test_client as client:
            response = await client.get("/test/unhandled-error")

        assert response.status_code == 500
        body = response.json()
        assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert body["error"]["message"] == "サーバー内部エラーが発生しました"
        assert "details" not in body["error"]
