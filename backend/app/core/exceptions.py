"""API仕様書に準拠したカスタム例外クラス。

各HTTPステータスコード（400, 401, 403, 404, 409）に対応した例外を定義する。
"""


class AppError(Exception):
    """アプリケーション共通の基底例外。"""

    status_code: int = 500
    error_code: str = "INTERNAL_SERVER_ERROR"
    message: str = "サーバー内部エラーが発生しました"

    def __init__(
        self,
        message: str | None = None,
        details: list[dict[str, str]] | None = None,
    ):
        if message is not None:
            self.message = message
        self.details = details
        super().__init__(self.message)


class ValidationError(AppError):
    """バリデーションエラー（400 Bad Request）。"""

    status_code = 400
    error_code = "VALIDATION_ERROR"
    message = "入力内容に誤りがあります"


class UnauthorizedError(AppError):
    """未認証エラー（401 Unauthorized）。"""

    status_code = 401
    error_code = "UNAUTHORIZED"
    message = "認証が必要です"


class ForbiddenError(AppError):
    """アクセス権限エラー（403 Forbidden）。"""

    status_code = 403
    error_code = "FORBIDDEN"
    message = "この操作を行う権限がありません"


class NotFoundError(AppError):
    """リソース未検出エラー（404 Not Found）。"""

    status_code = 404
    error_code = "NOT_FOUND"
    message = "リソースが見つかりません"


class ConflictError(AppError):
    """リソース競合エラー（409 Conflict）。"""

    status_code = 409
    error_code = "CONFLICT"
    message = "リソースが競合しています"
