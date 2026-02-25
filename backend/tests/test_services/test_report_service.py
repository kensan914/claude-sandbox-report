from datetime import date, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.core.security import hash_password
from app.models.customer import Customer
from app.models.daily_report import DailyReport, ReportStatus
from app.models.user import User, UserRole
from app.repositories.report_repository import ReportRepository
from app.repositories.visit_record_repository import (
    VisitRecordRepository,
)
from app.schemas.report import (
    ReportCreateRequest,
    ReportUpdateRequest,
    VisitRecordRequest,
)
from app.services.report_service import ReportService


async def _create_user(
    db: AsyncSession,
    *,
    email: str = "tanaka@example.com",
    role: UserRole = UserRole.SALES,
    name: str = "田中太郎",
) -> User:
    user = User(
        name=name,
        email=email,
        password_hash=hash_password("password123"),
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _create_customer(
    db: AsyncSession,
    *,
    company_name: str = "テスト株式会社",
) -> Customer:
    customer = Customer(
        company_name=company_name,
        contact_name="テスト担当",
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer


async def _create_report(
    db: AsyncSession,
    user: User,
    *,
    report_date: date | None = None,
    status: ReportStatus = ReportStatus.DRAFT,
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


def _build_service(db: AsyncSession) -> ReportService:
    return ReportService(ReportRepository(db), VisitRecordRepository(db))


class TestGetList:
    async def test_SALESは自分の日報のみ取得できること(self, db_session: AsyncSession):
        user1 = await _create_user(db_session)
        user2 = await _create_user(db_session, email="other@example.com", name="他人")
        await _create_report(db_session, user1)
        await _create_report(
            db_session,
            user2,
            report_date=date.today() - timedelta(days=1),
        )
        service = _build_service(db_session)

        reports, total = await service.get_list(user1)

        assert total == 1
        assert len(reports) == 1
        assert reports[0].salesperson_id == user1.id

    async def test_MANAGERは全件取得できること(self, db_session: AsyncSession):
        user1 = await _create_user(db_session)
        user2 = await _create_user(db_session, email="other@example.com", name="他人")
        manager = await _create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        await _create_report(db_session, user1)
        await _create_report(
            db_session,
            user2,
            report_date=date.today() - timedelta(days=1),
        )
        service = _build_service(db_session)

        reports, total = await service.get_list(manager)

        assert total == 2

    async def test_ステータスで絞り込めること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        await _create_report(db_session, user)
        await _create_report(
            db_session,
            user,
            report_date=date.today() - timedelta(days=1),
            status=ReportStatus.SUBMITTED,
        )
        service = _build_service(db_session)

        reports, total = await service.get_list(user, status="SUBMITTED")

        assert total == 1
        assert reports[0].status == ReportStatus.SUBMITTED


class TestCreate:
    async def test_下書き保存で日報が作成されること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        service = _build_service(db_session)
        request = ReportCreateRequest(
            report_date=date.today(),
            problem="課題テスト",
            plan="計画テスト",
            status="DRAFT",
        )

        report = await service.create(request, user)

        assert report.salesperson_id == user.id
        assert report.status == ReportStatus.DRAFT
        assert report.submitted_at is None

    async def test_提出で日報が作成されsubmitted_atが設定されること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        service = _build_service(db_session)
        request = ReportCreateRequest(
            report_date=date.today(),
            status="SUBMITTED",
        )

        report = await service.create(request, user)

        assert report.status == ReportStatus.SUBMITTED
        assert report.submitted_at is not None

    async def test_訪問記録付きで日報が作成されること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        customer = await _create_customer(db_session)
        service = _build_service(db_session)
        request = ReportCreateRequest(
            report_date=date.today(),
            status="DRAFT",
            visit_records=[
                VisitRecordRequest(
                    customer_id=customer.id,
                    visit_content="打合せ",
                    visited_at="10:00",
                ),
            ],
        )

        report = await service.create(request, user)

        assert len(report.visit_records) == 1
        assert report.visit_records[0].visit_order == 1

    async def test_未来日でValidationErrorが発生すること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        service = _build_service(db_session)
        request = ReportCreateRequest(
            report_date=date.today() + timedelta(days=1),
            status="DRAFT",
        )

        with pytest.raises(ValidationError) as exc_info:
            await service.create(request, user)

        assert exc_info.value.details[0]["field"] == "report_date"

    async def test_同日重複でConflictErrorが発生すること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        await _create_report(db_session, user)
        service = _build_service(db_session)
        request = ReportCreateRequest(
            report_date=date.today(),
            status="DRAFT",
        )

        with pytest.raises(ConflictError):
            await service.create(request, user)


class TestGetDetail:
    async def test_SALESが自分の日報を取得できること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        report = await _create_report(db_session, user)
        service = _build_service(db_session)

        result = await service.get_detail(report.id, user)

        assert result.id == report.id

    async def test_SALESが他人の日報を取得するとForbiddenErrorが発生すること(
        self, db_session: AsyncSession
    ):
        user1 = await _create_user(db_session)
        user2 = await _create_user(db_session, email="other@example.com", name="他人")
        report = await _create_report(db_session, user1)
        service = _build_service(db_session)

        with pytest.raises(ForbiddenError):
            await service.get_detail(report.id, user2)

    async def test_MANAGERは他人の日報を取得できること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        manager = await _create_user(
            db_session,
            email="manager@example.com",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user)
        service = _build_service(db_session)

        result = await service.get_detail(report.id, manager)

        assert result.id == report.id

    async def test_存在しないIDでNotFoundErrorが発生すること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        service = _build_service(db_session)

        with pytest.raises(NotFoundError):
            await service.get_detail(99999, user)


class TestUpdate:
    async def test_DRAFT日報を更新できること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        report = await _create_report(db_session, user)
        service = _build_service(db_session)
        request = ReportUpdateRequest(
            report_date=report.report_date,
            problem="更新後の課題",
            plan="更新後の計画",
            status="DRAFT",
        )

        result = await service.update(report.id, request, user)

        assert result.problem == "更新後の課題"
        assert result.plan == "更新後の計画"

    async def test_SUBMITTED日報は更新できないこと(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        report = await _create_report(db_session, user, status=ReportStatus.SUBMITTED)
        service = _build_service(db_session)
        request = ReportUpdateRequest(
            report_date=report.report_date,
            status="DRAFT",
        )

        with pytest.raises(ForbiddenError) as exc_info:
            await service.update(report.id, request, user)

        assert "提出済み" in exc_info.value.message

    async def test_他人の日報は更新できないこと(self, db_session: AsyncSession):
        user1 = await _create_user(db_session)
        user2 = await _create_user(db_session, email="other@example.com", name="他人")
        report = await _create_report(db_session, user1)
        service = _build_service(db_session)
        request = ReportUpdateRequest(
            report_date=report.report_date,
            status="DRAFT",
        )

        with pytest.raises(ForbiddenError) as exc_info:
            await service.update(report.id, request, user2)

        assert "自分の日報" in exc_info.value.message


class TestDelete:
    async def test_DRAFT日報を削除できること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        report = await _create_report(db_session, user)
        service = _build_service(db_session)

        await service.delete(report.id, user)

        # 削除されていることを確認
        from app.repositories.report_repository import (
            ReportRepository,
        )

        repo = ReportRepository(db_session)
        result = await repo.find_by_id(report.id)
        assert result is None

    async def test_SUBMITTED日報は削除できないこと(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        report = await _create_report(db_session, user, status=ReportStatus.SUBMITTED)
        service = _build_service(db_session)

        with pytest.raises(ForbiddenError):
            await service.delete(report.id, user)

    async def test_他人の日報は削除できないこと(self, db_session: AsyncSession):
        user1 = await _create_user(db_session)
        user2 = await _create_user(db_session, email="other@example.com", name="他人")
        report = await _create_report(db_session, user1)
        service = _build_service(db_session)

        with pytest.raises(ForbiddenError):
            await service.delete(report.id, user2)


class TestSubmit:
    async def test_DRAFT日報を提出できること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        report = await _create_report(db_session, user)
        service = _build_service(db_session)

        result = await service.submit(report.id, user)

        assert result.status == ReportStatus.SUBMITTED
        assert result.submitted_at is not None

    async def test_SUBMITTED日報を提出するとConflictErrorが発生すること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        report = await _create_report(db_session, user, status=ReportStatus.SUBMITTED)
        service = _build_service(db_session)

        with pytest.raises(ConflictError) as exc_info:
            await service.submit(report.id, user)

        assert "下書き" in exc_info.value.message

    async def test_他人の日報を提出するとForbiddenErrorが発生すること(
        self, db_session: AsyncSession
    ):
        user1 = await _create_user(db_session)
        user2 = await _create_user(db_session, email="other@example.com", name="他人")
        report = await _create_report(db_session, user1)
        service = _build_service(db_session)

        with pytest.raises(ForbiddenError) as exc_info:
            await service.submit(report.id, user2)

        assert "自分の日報" in exc_info.value.message

    async def test_存在しないIDでNotFoundErrorが発生すること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        service = _build_service(db_session)

        with pytest.raises(NotFoundError):
            await service.submit(99999, user)


class TestReview:
    async def test_MANAGERがSUBMITTED日報を確認済みにできること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        manager = await _create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user, status=ReportStatus.SUBMITTED)
        service = _build_service(db_session)

        result = await service.review(report.id, manager)

        assert result.status == ReportStatus.REVIEWED

    async def test_DRAFT日報を確認済みにするとConflictErrorが発生すること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        manager = await _create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user)
        service = _build_service(db_session)

        with pytest.raises(ConflictError) as exc_info:
            await service.review(report.id, manager)

        assert "提出済み" in exc_info.value.message

    async def test_SALESが確認済みにするとForbiddenErrorが発生すること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        report = await _create_report(db_session, user, status=ReportStatus.SUBMITTED)
        service = _build_service(db_session)

        with pytest.raises(ForbiddenError) as exc_info:
            await service.review(report.id, user)

        assert "上長のみ" in exc_info.value.message

    async def test_存在しないIDでNotFoundErrorが発生すること(
        self, db_session: AsyncSession
    ):
        manager = await _create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        service = _build_service(db_session)

        with pytest.raises(NotFoundError):
            await service.review(99999, manager)
