"""日報APIのリクエスト/レスポンススキーマ。"""

from datetime import date, datetime

from pydantic import BaseModel, Field

# --- リクエスト ---


class VisitRecordRequest(BaseModel):
    """訪問記録のリクエスト。"""

    customer_id: int = Field(description="顧客ID")
    visit_content: str = Field(min_length=1, max_length=1000, description="訪問内容")
    visited_at: str = Field(pattern=r"^\d{2}:\d{2}$", description="訪問時刻（HH:mm）")


class ReportCreateRequest(BaseModel):
    """日報作成リクエスト。"""

    report_date: date = Field(description="報告日")
    problem: str | None = Field(default=None, max_length=2000, description="課題・相談")
    plan: str | None = Field(default=None, max_length=2000, description="明日やること")
    status: str = Field(description="ステータス（DRAFT / SUBMITTED）")
    visit_records: list[VisitRecordRequest] = Field(
        default_factory=list, description="訪問記録"
    )


class ReportUpdateRequest(BaseModel):
    """日報更新リクエスト。"""

    report_date: date = Field(description="報告日")
    problem: str | None = Field(default=None, max_length=2000, description="課題・相談")
    plan: str | None = Field(default=None, max_length=2000, description="明日やること")
    status: str = Field(description="ステータス（DRAFT / SUBMITTED）")
    visit_records: list[VisitRecordRequest] = Field(
        default_factory=list, description="訪問記録"
    )


# --- レスポンス ---


class SalespersonResponse(BaseModel):
    """担当者の簡易レスポンス。"""

    id: int
    name: str

    model_config = {"from_attributes": True}


class CustomerSummaryResponse(BaseModel):
    """顧客の簡易レスポンス（一覧用）。"""

    id: int
    company_name: str

    model_config = {"from_attributes": True}


class CustomerDetailResponse(BaseModel):
    """顧客の詳細レスポンス（詳細用）。"""

    id: int
    company_name: str
    contact_name: str

    model_config = {"from_attributes": True}


class VisitRecordSummaryResponse(BaseModel):
    """訪問記録レスポンス（作成・更新時）。"""

    id: int
    customer: CustomerSummaryResponse
    visit_content: str
    visited_at: str = Field(description="訪問時刻（HH:mm）")
    visit_order: int

    model_config = {"from_attributes": True}


class VisitRecordDetailResponse(BaseModel):
    """訪問記録レスポンス（詳細取得時）。"""

    id: int
    customer: CustomerDetailResponse
    visit_content: str
    visited_at: str = Field(description="訪問時刻（HH:mm）")
    visit_order: int

    model_config = {"from_attributes": True}


class CommentResponse(BaseModel):
    """コメントレスポンス。"""

    id: int
    target: str
    manager: SalespersonResponse
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportListItemResponse(BaseModel):
    """日報一覧の1件分のレスポンス。"""

    id: int
    report_date: date
    salesperson: SalespersonResponse
    visit_count: int
    status: str
    submitted_at: datetime | None

    model_config = {"from_attributes": True}


class ReportDetailResponse(BaseModel):
    """日報詳細レスポンス。"""

    id: int
    report_date: date
    salesperson: SalespersonResponse
    problem: str | None
    plan: str | None
    status: str
    submitted_at: datetime | None
    visit_records: list[VisitRecordDetailResponse]
    comments: list[CommentResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReportSubmitResponse(BaseModel):
    """日報提出レスポンス。"""

    id: int
    status: str
    submitted_at: datetime

    model_config = {"from_attributes": True}


class ReportReviewResponse(BaseModel):
    """日報確認済みレスポンス。"""

    id: int
    status: str

    model_config = {"from_attributes": True}


class ReportCreateUpdateResponse(BaseModel):
    """日報作成・更新レスポンス。"""

    id: int
    report_date: date
    salesperson: SalespersonResponse
    problem: str | None
    plan: str | None
    status: str
    submitted_at: datetime | None
    visit_records: list[VisitRecordSummaryResponse]
    comments: list[CommentResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
