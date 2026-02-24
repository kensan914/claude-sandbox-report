"""カスタム例外クラスのテスト。"""

import pytest

from app.core.exceptions import (
    AppError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


class TestAppError:
    """AppError基底クラスのテスト。"""

    def test_デフォルトメッセージで例外を生成できること(self):
        error = AppError()
        assert error.status_code == 500
        assert error.error_code == "INTERNAL_SERVER_ERROR"
        assert error.message == "サーバー内部エラーが発生しました"
        assert error.details is None

    def test_カスタムメッセージで例外を生成できること(self):
        error = AppError(message="カスタムエラー")
        assert error.message == "カスタムエラー"

    def test_詳細情報付きで例外を生成できること(self):
        details = [{"field": "email", "message": "メール形式で入力してください"}]
        error = AppError(details=details)
        assert error.details == details


class TestValidationError:
    """ValidationErrorのテスト。"""

    def test_ステータスコード400とエラーコードが正しいこと(self):
        error = ValidationError()
        assert error.status_code == 400
        assert error.error_code == "VALIDATION_ERROR"
        assert error.message == "入力内容に誤りがあります"

    def test_詳細情報付きバリデーションエラーを生成できること(self):
        details = [
            {"field": "email", "message": "メール形式で入力してください"},
            {"field": "password", "message": "1文字以上入力してください"},
        ]
        error = ValidationError(details=details)
        assert error.details == details
        assert len(error.details) == 2

    def test_AppErrorのサブクラスであること(self):
        error = ValidationError()
        assert isinstance(error, AppError)


class TestUnauthorizedError:
    """UnauthorizedErrorのテスト。"""

    def test_ステータスコード401とエラーコードが正しいこと(self):
        error = UnauthorizedError()
        assert error.status_code == 401
        assert error.error_code == "UNAUTHORIZED"
        assert error.message == "認証が必要です"


class TestForbiddenError:
    """ForbiddenErrorのテスト。"""

    def test_ステータスコード403とエラーコードが正しいこと(self):
        error = ForbiddenError()
        assert error.status_code == 403
        assert error.error_code == "FORBIDDEN"
        assert error.message == "この操作を行う権限がありません"


class TestNotFoundError:
    """NotFoundErrorのテスト。"""

    def test_ステータスコード404とエラーコードが正しいこと(self):
        error = NotFoundError()
        assert error.status_code == 404
        assert error.error_code == "NOT_FOUND"
        assert error.message == "リソースが見つかりません"


class TestConflictError:
    """ConflictErrorのテスト。"""

    def test_ステータスコード409とエラーコードが正しいこと(self):
        error = ConflictError()
        assert error.status_code == 409
        assert error.error_code == "CONFLICT"
        assert error.message == "リソースが競合しています"

    def test_カスタムメッセージで競合エラーを生成できること(self):
        error = ConflictError(message="指定された日付の日報は既に存在します")
        assert error.message == "指定された日付の日報は既に存在します"


class TestExceptionInheritance:
    """例外クラスの継承関係のテスト。"""

    @pytest.mark.parametrize(
        ("exception_class", "expected_status"),
        [
            (ValidationError, 400),
            (UnauthorizedError, 401),
            (ForbiddenError, 403),
            (NotFoundError, 404),
            (ConflictError, 409),
        ],
    )
    def test_全例外クラスがAppErrorを継承していること(
        self, exception_class, expected_status
    ):
        error = exception_class()
        assert isinstance(error, AppError)
        assert isinstance(error, Exception)
        assert error.status_code == expected_status
