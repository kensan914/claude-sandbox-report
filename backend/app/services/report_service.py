"""日報のビジネスロジック層。"""

from datetime import UTC, date, datetime

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.models.daily_report import DailyReport, ReportStatus
from app.models.user import User, UserRole
from app.models.visit_record import VisitRecord
from app.repositories.report_repository import ReportRepository
from app.repositories.visit_record_repository import VisitRecordRepository
from app.schemas.report import ReportCreateRequest, ReportUpdateRequest


class ReportService:
    def __init__(
        self,
        report_repository: ReportRepository,
        visit_record_repository: VisitRecordRepository,
    ):
        self.report_repository = report_repository
        self.visit_record_repository = visit_record_repository

    async def get_list(
        self,
        current_user: User,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        salesperson_id: int | None = None,
        status: str | None = None,
        sort: str = "report_date",
        order: str = "desc",
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[DailyReport], int]:
        """日報一覧を取得する。SALESは自分の日報のみ。"""
        # SALESは自分の日報のみに制限
        effective_salesperson_id = salesperson_id
        if current_user.role == UserRole.SALES:
            effective_salesperson_id = current_user.id

        # ステータスをenumに変換
        status_enum = None
        if status is not None:
            try:
                status_enum = ReportStatus(status)
            except ValueError as err:
                raise ValidationError(
                    message="入力内容に誤りがあります",
                    details=[
                        {
                            "field": "status",
                            "message": "無効なステータスです",
                        }
                    ],
                ) from err

        return await self.report_repository.find_list(
            salesperson_id=effective_salesperson_id,
            date_from=date_from,
            date_to=date_to,
            status=status_enum,
            sort=sort,
            order=order,
            page=page,
            per_page=per_page,
        )

    async def get_detail(self, report_id: int, current_user: User) -> DailyReport:
        """日報詳細を取得する。"""
        report = await self.report_repository.find_by_id(report_id)
        if report is None:
            raise NotFoundError(message="日報が見つかりません")

        # SALESは自分の日報のみ閲覧可能
        if (
            current_user.role == UserRole.SALES
            and report.salesperson_id != current_user.id
        ):
            raise ForbiddenError(message="自分の日報のみ閲覧できます")

        return report

    async def create(
        self, request: ReportCreateRequest, current_user: User
    ) -> DailyReport:
        """日報を作成する。"""
        # 未来日チェック
        self._validate_report_date(request.report_date)

        # ステータスの検証
        report_status = self._validate_create_status(request.status)

        # 同日重複チェック
        existing = await self.report_repository.find_by_salesperson_and_date(
            current_user.id, request.report_date
        )
        if existing is not None:
            raise ConflictError(message="指定された日付の日報は既に存在します")

        # 日報の作成
        submitted_at = None
        if report_status == ReportStatus.SUBMITTED:
            submitted_at = datetime.now(UTC).replace(tzinfo=None)

        report = DailyReport(
            salesperson_id=current_user.id,
            report_date=request.report_date,
            problem=request.problem,
            plan=request.plan,
            status=report_status,
            submitted_at=submitted_at,
        )
        report = await self.report_repository.create(report)

        # 訪問記録の作成
        if request.visit_records:
            visit_records = self._build_visit_records(report.id, request.visit_records)
            await self.visit_record_repository.bulk_create(visit_records)

        # リレーション込みで再取得
        return await self.report_repository.find_by_id(report.id)

    async def update(
        self,
        report_id: int,
        request: ReportUpdateRequest,
        current_user: User,
    ) -> DailyReport:
        """日報を更新する。"""
        report = await self._get_editable_report(report_id, current_user)

        # 未来日チェック
        self._validate_report_date(request.report_date)

        # ステータスの検証
        report_status = self._validate_create_status(request.status)

        # 報告日変更時の重複チェック
        if request.report_date != report.report_date:
            existing = await self.report_repository.find_by_salesperson_and_date(
                current_user.id, request.report_date
            )
            if existing is not None:
                raise ConflictError(message="指定された日付の日報は既に存在します")

        # 日報の更新
        report.report_date = request.report_date
        report.problem = request.problem
        report.plan = request.plan
        report.status = report_status

        if report_status == ReportStatus.SUBMITTED and report.submitted_at is None:
            report.submitted_at = datetime.now(UTC).replace(tzinfo=None)

        # 訪問記録の洗い替え
        await self.visit_record_repository.delete_by_report_id(report.id)
        if request.visit_records:
            visit_records = self._build_visit_records(report.id, request.visit_records)
            await self.visit_record_repository.bulk_create(visit_records)

        report = await self.report_repository.update(report)

        # リレーション込みで再取得
        return await self.report_repository.find_by_id(report.id)

    async def delete(self, report_id: int, current_user: User) -> None:
        """日報を削除する。"""
        report = await self._get_editable_report(report_id, current_user)
        await self.report_repository.delete(report)

    async def submit(self, report_id: int, current_user: User) -> DailyReport:
        """日報を提出する（DRAFT → SUBMITTED）。"""
        report = await self.report_repository.find_by_id(report_id)
        if report is None:
            raise NotFoundError(message="日報が見つかりません")

        if report.salesperson_id != current_user.id:
            raise ForbiddenError(message="自分の日報のみ提出できます")

        if report.status != ReportStatus.DRAFT:
            raise ConflictError(message="下書きの日報のみ提出できます")

        report.status = ReportStatus.SUBMITTED
        report.submitted_at = datetime.now(UTC).replace(tzinfo=None)
        return await self.report_repository.update(report)

    async def review(self, report_id: int, current_user: User) -> DailyReport:
        """日報を確認済みにする（SUBMITTED → REVIEWED）。"""
        if current_user.role != UserRole.MANAGER:
            raise ForbiddenError(message="上長のみ確認済みにできます")

        report = await self.report_repository.find_by_id(report_id)
        if report is None:
            raise NotFoundError(message="日報が見つかりません")

        if report.status != ReportStatus.SUBMITTED:
            raise ConflictError(message="提出済みの日報のみ確認済みにできます")

        report.status = ReportStatus.REVIEWED
        return await self.report_repository.update(report)

    # --- プライベートメソッド ---

    async def _get_editable_report(
        self, report_id: int, current_user: User
    ) -> DailyReport:
        """編集・削除可能な日報を取得する。"""
        report = await self.report_repository.find_by_id(report_id)
        if report is None:
            raise NotFoundError(message="日報が見つかりません")

        if report.salesperson_id != current_user.id:
            raise ForbiddenError(message="自分の日報のみ編集できます")

        if report.status != ReportStatus.DRAFT:
            raise ForbiddenError(message="提出済みの日報は編集できません")

        return report

    def _validate_report_date(self, report_date: date) -> None:
        """報告日が未来日でないことを検証する。"""
        if report_date > date.today():
            raise ValidationError(
                message="入力内容に誤りがあります",
                details=[
                    {
                        "field": "report_date",
                        "message": ("報告日に未来の日付は指定できません"),
                    }
                ],
            )

    def _validate_create_status(self, status: str) -> ReportStatus:
        """作成・更新時のステータスがDRAFTまたはSUBMITTEDであることを検証する。"""
        if status not in (
            ReportStatus.DRAFT,
            ReportStatus.SUBMITTED,
        ):
            raise ValidationError(
                message="入力内容に誤りがあります",
                details=[
                    {
                        "field": "status",
                        "message": (
                            "ステータスはDRAFTまたはSUBMITTEDを指定してください"
                        ),
                    }
                ],
            )
        return ReportStatus(status)

    def _build_visit_records(self, report_id: int, records) -> list[VisitRecord]:
        """訪問記録のリクエストからORMモデルのリストを構築する。"""
        return [
            VisitRecord(
                daily_report_id=report_id,
                customer_id=record.customer_id,
                visit_content=record.visit_content,
                visited_at=datetime.strptime(record.visited_at, "%H:%M").replace(
                    year=1970, month=1, day=1
                ),
                visit_order=idx + 1,
            )
            for idx, record in enumerate(records)
        ]
