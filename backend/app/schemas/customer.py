"""顧客APIのリクエスト/レスポンススキーマ。"""

from datetime import datetime

from pydantic import BaseModel, Field

# --- リクエスト ---


class CustomerCreateRequest(BaseModel):
    """顧客登録リクエスト。"""

    company_name: str = Field(min_length=1, max_length=200, description="会社名")
    contact_name: str = Field(min_length=1, max_length=100, description="担当者名")
    address: str | None = Field(default=None, max_length=500, description="住所")
    phone: str | None = Field(default=None, description="電話番号")
    email: str | None = Field(default=None, description="メールアドレス")


class CustomerUpdateRequest(BaseModel):
    """顧客更新リクエスト。"""

    company_name: str = Field(min_length=1, max_length=200, description="会社名")
    contact_name: str = Field(min_length=1, max_length=100, description="担当者名")
    address: str | None = Field(default=None, max_length=500, description="住所")
    phone: str | None = Field(default=None, description="電話番号")
    email: str | None = Field(default=None, description="メールアドレス")


# --- レスポンス ---


class CustomerResponse(BaseModel):
    """顧客レスポンス。"""

    id: int
    company_name: str
    contact_name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerListItemResponse(BaseModel):
    """顧客一覧の1件分のレスポンス。"""

    id: int
    company_name: str
    contact_name: str
    phone: str | None = None
    email: str | None = None

    model_config = {"from_attributes": True}
