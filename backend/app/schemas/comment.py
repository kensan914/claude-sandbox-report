"""コメントAPIのリクエスト/レスポンススキーマ。"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.report import SalespersonResponse


class CommentCreateRequest(BaseModel):
    """コメント投稿リクエスト。"""

    target: str = Field(description="コメント対象（PROBLEM / PLAN）")
    content: str = Field(
        min_length=1, max_length=1000, description="コメント内容"
    )


class CommentCreateResponse(BaseModel):
    """コメント投稿レスポンス。"""

    id: int
    target: str
    manager: SalespersonResponse
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
