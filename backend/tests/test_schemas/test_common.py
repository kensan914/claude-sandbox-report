"""共通レスポンスモデルとページネーションヘルパーのテスト。"""

from app.schemas.common import (
    DataResponse,
    ErrorBody,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    Pagination,
    create_paginated_response,
    create_pagination,
)


class TestPagination:
    """Paginationモデルのテスト。"""

    def test_ページネーション情報を生成できること(self):
        pagination = Pagination(
            current_page=1, per_page=20, total_count=100, total_pages=5
        )
        assert pagination.current_page == 1
        assert pagination.per_page == 20
        assert pagination.total_count == 100
        assert pagination.total_pages == 5


class TestCreatePagination:
    """create_pagination ヘルパー関数のテスト。"""

    def test_通常のページネーション計算が正しいこと(self):
        pagination = create_pagination(total_count=100, page=1, per_page=20)
        assert pagination.current_page == 1
        assert pagination.per_page == 20
        assert pagination.total_count == 100
        assert pagination.total_pages == 5

    def test_端数があるとき切り上げされること(self):
        pagination = create_pagination(total_count=21, page=1, per_page=20)
        assert pagination.total_pages == 2

    def test_件数0のとき全ページ数が1になること(self):
        pagination = create_pagination(total_count=0, page=1, per_page=20)
        assert pagination.total_pages == 1
        assert pagination.total_count == 0

    def test_ちょうど割り切れるとき正しいページ数になること(self):
        pagination = create_pagination(total_count=40, page=2, per_page=20)
        assert pagination.total_pages == 2
        assert pagination.current_page == 2

    def test_1件のとき全ページ数が1になること(self):
        pagination = create_pagination(total_count=1, page=1, per_page=20)
        assert pagination.total_pages == 1


class TestCreatePaginatedResponse:
    """create_paginated_response ヘルパー関数のテスト。"""

    def test_ページネーション付きレスポンスを生成できること(self):
        data = [{"id": 1, "name": "テスト"}]
        result = create_paginated_response(
            data=data, total_count=1, page=1, per_page=20
        )
        assert result["data"] == data
        assert result["pagination"]["current_page"] == 1
        assert result["pagination"]["per_page"] == 20
        assert result["pagination"]["total_count"] == 1
        assert result["pagination"]["total_pages"] == 1

    def test_空リストでもレスポンスを生成できること(self):
        result = create_paginated_response(data=[], total_count=0, page=1, per_page=20)
        assert result["data"] == []
        assert result["pagination"]["total_count"] == 0


class TestDataResponse:
    """DataResponseモデルのテスト。"""

    def test_単一データのレスポンスを生成できること(self):
        response = DataResponse(data={"id": 1, "name": "テスト"})
        dumped = response.model_dump()
        assert dumped["data"] == {"id": 1, "name": "テスト"}

    def test_リストデータのレスポンスを生成できること(self):
        response = DataResponse(data=[{"id": 1}, {"id": 2}])
        dumped = response.model_dump()
        assert len(dumped["data"]) == 2


class TestPaginatedResponse:
    """PaginatedResponseモデルのテスト。"""

    def test_ページネーション付きレスポンスモデルを生成できること(self):
        pagination = Pagination(
            current_page=1, per_page=20, total_count=50, total_pages=3
        )
        response = PaginatedResponse(data=[{"id": 1}, {"id": 2}], pagination=pagination)
        dumped = response.model_dump()
        assert len(dumped["data"]) == 2
        assert dumped["pagination"]["total_count"] == 50


class TestErrorResponse:
    """ErrorResponseモデルのテスト。"""

    def test_エラーレスポンスを生成できること(self):
        response = ErrorResponse(
            error=ErrorBody(
                code="VALIDATION_ERROR",
                message="入力内容に誤りがあります",
            )
        )
        dumped = response.model_dump(exclude_none=True)
        assert dumped["error"]["code"] == "VALIDATION_ERROR"
        assert dumped["error"]["message"] == "入力内容に誤りがあります"
        assert "details" not in dumped["error"]

    def test_詳細情報付きエラーレスポンスを生成できること(self):
        response = ErrorResponse(
            error=ErrorBody(
                code="VALIDATION_ERROR",
                message="入力内容に誤りがあります",
                details=[
                    ErrorDetail(field="email", message="メール形式で入力してください")
                ],
            )
        )
        dumped = response.model_dump(exclude_none=True)
        assert len(dumped["error"]["details"]) == 1
        assert dumped["error"]["details"][0]["field"] == "email"

    def test_API仕様書のエラーレスポンス形式に準拠していること(self):
        """API仕様書で定義されたJSON構造を検証する。"""
        response = ErrorResponse(
            error=ErrorBody(
                code="NOT_FOUND",
                message="リソースが見つかりません",
            )
        )
        dumped = response.model_dump(exclude_none=True)
        # トップレベルに"error"キーが存在すること
        assert "error" in dumped
        # errorオブジェクトに"code"と"message"が存在すること
        assert "code" in dumped["error"]
        assert "message" in dumped["error"]
