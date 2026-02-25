"""認証APIのリクエスト/レスポンススキーマ。"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """ログインリクエスト。"""

    email: EmailStr = Field(description="メールアドレス")
    password: str = Field(min_length=1, description="パスワード")


class UserResponse(BaseModel):
    """ユーザー情報のレスポンス。"""

    id: int = Field(description="ユーザーID")
    name: str = Field(description="氏名")
    email: str = Field(description="メールアドレス")
    role: str = Field(description="ロール（SALES / MANAGER）")

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    """ログインレスポンス。Cookie認証のためtokenは含まない。"""

    user: UserResponse
