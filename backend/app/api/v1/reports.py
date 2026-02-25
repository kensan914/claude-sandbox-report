"""日報エンドポイント（CRUD）。"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.report_repository import ReportRepository
from app.repositories.visit_record_repository import (
    VisitRecordRepository,
)
from app.schemas.common import DataResponse, create_paginated_response
from app.schemas.report import (
    CommentResponse,
    ReportCreateRequest,
    ReportCreateUpdateResponse,
    ReportDetailResponse,
    ReportListItemResponse,
    ReportUpdateRequest,
    SalespersonResponse,
    VisitRecordDetailResponse,
    VisitRecordSummaryResponse,
)
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["日報"])


def _get_report_service(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> ReportService:
    """日報サービスの依存注入。"""
    return ReportService(ReportRepository(db), VisitRecordRepository(db))


def _format_visited_at(visited_at) -> str:
    """visited_at を HH:mm 形式の文字列に変換する。"""
    return visited_at.strftime("%H:%M")


def _build_list_item(report) -> dict:
    """日報一覧の1件分のレスポンスを構築する。"""
    return ReportListItemResponse(
        id=report.id,
        report_date=report.report_date,
        salesperson=SalespersonResponse.model_validate(report.salesperson),
        visit_count=len(report.visit_records),
        status=report.status.value,
        submitted_at=report.submitted_at,
    ).model_dump(mode="json")


def _build_detail_response(report) -> ReportDetailResponse:
    """日報詳細レスポンスを構築する。"""
    visit_records = [
        VisitRecordDetailResponse(
            id=vr.id,
            customer=vr.customer,
            visit_content=vr.visit_content,
            visited_at=_format_visited_at(vr.visited_at),
            visit_order=vr.visit_order,
        )
        for vr in sorted(report.visit_records, key=lambda v: v.visit_order)
    ]

    comments = [
        CommentResponse(
            id=c.id,
            target=c.target.value,
            manager=SalespersonResponse.model_validate(c.manager),
            content=c.content,
            created_at=c.created_at,
        )
        for c in sorted(report.comments, key=lambda c: c.created_at)
    ]

    return ReportDetailResponse(
        id=report.id,
        report_date=report.report_date,
        salesperson=SalespersonResponse.model_validate(report.salesperson),
        problem=report.problem,
        plan=report.plan,
        status=report.status.value,
        submitted_at=report.submitted_at,
        visit_records=visit_records,
        comments=comments,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


def _build_create_update_response(
    report,
) -> ReportCreateUpdateResponse:
    """日報作成・更新レスポンスを構築する。"""
    visit_records = [
        VisitRecordSummaryResponse(
            id=vr.id,
            customer=vr.customer,
            visit_content=vr.visit_content,
            visited_at=_format_visited_at(vr.visited_at),
            visit_order=vr.visit_order,
        )
        for vr in sorted(report.visit_records, key=lambda v: v.visit_order)
    ]

    comments = [
        CommentResponse(
            id=c.id,
            target=c.target.value,
            manager=SalespersonResponse.model_validate(c.manager),
            content=c.content,
            created_at=c.created_at,
        )
        for c in sorted(report.comments, key=lambda c: c.created_at)
    ]

    return ReportCreateUpdateResponse(
        id=report.id,
        report_date=report.report_date,
        salesperson=SalespersonResponse.model_validate(report.salesperson),
        problem=report.problem,
        plan=report.plan,
        status=report.status.value,
        submitted_at=report.submitted_at,
        visit_records=visit_records,
        comments=comments,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


@router.get("")
async def get_reports(
    date_from: date | None = Query(default=None),  # noqa: B008
    date_to: date | None = Query(default=None),  # noqa: B008
    salesperson_id: int | None = Query(default=None),  # noqa: B008
    status: str | None = Query(default=None),  # noqa: B008
    sort: str = Query(default="report_date"),
    order: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    service: ReportService = Depends(_get_report_service),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    """日報一覧を取得する。"""
    reports, total_count = await service.get_list(
        current_user,
        date_from=date_from,
        date_to=date_to,
        salesperson_id=salesperson_id,
        status=status,
        sort=sort,
        order=order,
        page=page,
        per_page=per_page,
    )

    data = [_build_list_item(r) for r in reports]
    return create_paginated_response(
        data=data,
        total_count=total_count,
        page=page,
        per_page=per_page,
    )


@router.post(
    "",
    status_code=201,
    response_model=DataResponse[ReportCreateUpdateResponse],
)
async def create_report(
    request: ReportCreateRequest,
    service: ReportService = Depends(_get_report_service),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    """日報を作成する。"""
    report = await service.create(request, current_user)
    return DataResponse(data=_build_create_update_response(report))


@router.get(
    "/{report_id}",
    response_model=DataResponse[ReportDetailResponse],
)
async def get_report(
    report_id: int,
    service: ReportService = Depends(_get_report_service),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    """日報詳細を取得する。"""
    report = await service.get_detail(report_id, current_user)
    return DataResponse(data=_build_detail_response(report))


@router.put(
    "/{report_id}",
    response_model=DataResponse[ReportCreateUpdateResponse],
)
async def update_report(
    report_id: int,
    request: ReportUpdateRequest,
    service: ReportService = Depends(_get_report_service),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    """日報を更新する。"""
    report = await service.update(report_id, request, current_user)
    return DataResponse(data=_build_create_update_response(report))


@router.delete("/{report_id}", status_code=204)
async def delete_report(
    report_id: int,
    service: ReportService = Depends(_get_report_service),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    """日報を削除する。"""
    await service.delete(report_id, current_user)
