"""ユーザーAPIのリクエスト/レスポンススキーマ。"""

from pydantic import BaseModel, Field


class UserListItemResponse(BaseModel):
    """ユーザー一覧の1件分のレスポンス。"""

    id: int = Field(description="ユーザーID")
    name: str = Field(description="氏名")
    email: str = Field(description="メールアドレス")
    role: str = Field(description="ロール（SALES / MANAGER）")

    model_config = {"from_attributes": True}
