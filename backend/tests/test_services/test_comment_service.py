from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.daily_report import DailyReport, ReportStatus
from app.models.user import UserRole
from app.repositories.comment_repository import CommentRepository
from app.repositories.report_repository import ReportRepository
from app.schemas.comment import CommentCreateRequest
from app.services.comment_service import CommentService
from tests.helpers import create_user


async def _create_report(
    db: AsyncSession,
    user,
    *,
    report_date: date | None = None,
    status: ReportStatus = ReportStatus.SUBMITTED,
) -> DailyReport:
    if report_date is None:
        report_date = date.today()
    report = DailyReport(
        salesperson_id=user.id,
        report_date=report_date,
        problem="テスト課題",
        plan="テスト計画",
        status=status,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


def _build_service(db: AsyncSession) -> CommentService:
    return CommentService(CommentRepository(db), ReportRepository(db))


class TestCreateComment:
    async def test_MANAGERがSUBMITTED日報にPROBLEMコメントを投稿できること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user)
        service = _build_service(db_session)
        request = CommentCreateRequest(target="PROBLEM", content="確認しました")

        result = await service.create(report.id, request, manager)

        assert result.target.value == "PROBLEM"
        assert result.content == "確認しました"
        assert result.manager_id == manager.id
        assert result.daily_report_id == report.id

    async def test_MANAGERがSUBMITTED日報にPLANコメントを投稿できること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user)
        service = _build_service(db_session)
        request = CommentCreateRequest(target="PLAN", content="了解です")

        result = await service.create(report.id, request, manager)

        assert result.target.value == "PLAN"
        assert result.content == "了解です"

    async def test_MANAGERがREVIEWED日報にコメントを投稿できること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user, status=ReportStatus.REVIEWED)
        service = _build_service(db_session)
        request = CommentCreateRequest(target="PROBLEM", content="追加コメント")

        result = await service.create(report.id, request, manager)

        assert result.content == "追加コメント"

    async def test_SALESがコメントを投稿するとForbiddenErrorが発生すること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        report = await _create_report(db_session, user)
        service = _build_service(db_session)
        request = CommentCreateRequest(target="PROBLEM", content="テスト")

        with pytest.raises(ForbiddenError) as exc_info:
            await service.create(report.id, request, user)

        assert "上長のみ" in exc_info.value.message

    async def test_DRAFT日報にコメントするとForbiddenErrorが発生すること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user, status=ReportStatus.DRAFT)
        service = _build_service(db_session)
        request = CommentCreateRequest(target="PROBLEM", content="テスト")

        with pytest.raises(ForbiddenError) as exc_info:
            await service.create(report.id, request, manager)

        assert "下書き" in exc_info.value.message

    async def test_不正なtargetでValidationErrorが発生すること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user)
        service = _build_service(db_session)
        request = CommentCreateRequest(target="INVALID", content="テスト")

        with pytest.raises(ValidationError) as exc_info:
            await service.create(report.id, request, manager)

        assert exc_info.value.details[0]["field"] == "target"

    async def test_存在しない日報IDでNotFoundErrorが発生すること(
        self, db_session: AsyncSession
    ):
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        service = _build_service(db_session)
        request = CommentCreateRequest(target="PROBLEM", content="テスト")

        with pytest.raises(NotFoundError):
            await service.create(99999, request, manager)
