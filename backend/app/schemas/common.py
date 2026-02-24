"""API仕様書に準拠した共通レスポンスモデル。

成功時: {"data": {...}}
一覧時: {"data": [...], "pagination": {...}}
エラー時: {"error": {"code": "...", "message": "...", "details": [...]}}
"""

import math
from typing import Any

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    """ページネーション情報。"""

    current_page: int = Field(description="現在のページ番号")
    per_page: int = Field(description="1ページあたりの件数")
    total_count: int = Field(description="全件数")
    total_pages: int = Field(description="全ページ数")


class DataResponse[T](BaseModel):
    """単一リソースの成功レスポンス。"""

    data: T


class PaginatedResponse[T](BaseModel):
    """一覧取得の成功レスポンス（ページネーション付き）。"""

    data: list[T]
    pagination: Pagination


class ErrorDetail(BaseModel):
    """バリデーションエラーの詳細情報。"""

    field: str = Field(description="エラー対象のフィールド名")
    message: str = Field(description="エラーメッセージ")


class ErrorBody(BaseModel):
    """エラーレスポンスの本体。"""

    code: str = Field(description="エラーコード")
    message: str = Field(description="エラーメッセージ")
    details: list[ErrorDetail] | None = Field(
        default=None, description="バリデーションエラーの詳細"
    )


class ErrorResponse(BaseModel):
    """エラーレスポンス。"""

    error: ErrorBody


def create_pagination(*, total_count: int, page: int, per_page: int) -> Pagination:
    """ページネーション情報を生成するヘルパー関数。"""
    total_pages = max(1, math.ceil(total_count / per_page))
    return Pagination(
        current_page=page,
        per_page=per_page,
        total_count=total_count,
        total_pages=total_pages,
    )


def create_paginated_response(
    *, data: list[Any], total_count: int, page: int, per_page: int
) -> dict[str, Any]:
    """ページネーション付きレスポンスを生成するヘルパー関数。"""
    pagination = create_pagination(
        total_count=total_count, page=page, per_page=per_page
    )
    return {
        "data": data,
        "pagination": pagination.model_dump(),
    }
