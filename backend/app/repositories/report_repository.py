"""日報のデータアクセス層。"""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.daily_report import DailyReport, ReportStatus
from app.models.visit_record import VisitRecord


class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_list(
        self,
        *,
        salesperson_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        status: ReportStatus | None = None,
        sort: str = "report_date",
        order: str = "desc",
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[DailyReport], int]:
        """検索条件に基づいて日報一覧を取得する。"""
        query = select(DailyReport).options(
            joinedload(DailyReport.salesperson),
            joinedload(DailyReport.visit_records),
        )

        # 検索条件の適用
        if salesperson_id is not None:
            query = query.where(DailyReport.salesperson_id == salesperson_id)
        if date_from is not None:
            query = query.where(DailyReport.report_date >= date_from)
        if date_to is not None:
            query = query.where(DailyReport.report_date <= date_to)
        if status is not None:
            query = query.where(DailyReport.status == status)

        # 件数取得
        count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await self.db.execute(count_query)
        total_count = total_count_result.scalar_one()

        # ソート
        sort_column = self._get_sort_column(sort)
        if order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # ページネーション
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        result = await self.db.execute(query)
        reports = result.unique().scalars().all()
        return list(reports), total_count

    def _get_sort_column(self, sort: str):
        """ソート項目名から対応するカラムを返す。"""
        sort_map = {
            "report_date": DailyReport.report_date,
            "status": DailyReport.status,
            "submitted_at": DailyReport.submitted_at,
        }
        return sort_map.get(sort, DailyReport.report_date)

    async def find_by_id(self, report_id: int) -> DailyReport | None:
        """IDで日報を取得する（リレーション含む）。"""
        query = (
            select(DailyReport)
            .options(
                joinedload(DailyReport.salesperson),
                joinedload(DailyReport.visit_records).joinedload(VisitRecord.customer),
                joinedload(DailyReport.comments),
            )
            .where(DailyReport.id == report_id)
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()

    async def find_by_salesperson_and_date(
        self, salesperson_id: int, report_date: date
    ) -> DailyReport | None:
        """担当者IDと報告日で日報を取得する（重複チェック用）。"""
        result = await self.db.execute(
            select(DailyReport).where(
                DailyReport.salesperson_id == salesperson_id,
                DailyReport.report_date == report_date,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, report: DailyReport) -> DailyReport:
        """日報を作成する。"""
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def update(self, report: DailyReport) -> DailyReport:
        """日報を更新する。"""
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def delete(self, report: DailyReport) -> None:
        """日報を削除する。"""
        await self.db.delete(report)
        await self.db.commit()
