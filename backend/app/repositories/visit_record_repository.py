"""訪問記録のデータアクセス層。"""

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.visit_record import VisitRecord


class VisitRecordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def delete_by_report_id(self, daily_report_id: int) -> None:
        """日報IDに紐づく訪問記録を全件削除する（洗い替え用）。"""
        await self.db.execute(
            delete(VisitRecord).where(VisitRecord.daily_report_id == daily_report_id)
        )

    async def bulk_create(self, records: list[VisitRecord]) -> list[VisitRecord]:
        """訪問記録を一括作成する。"""
        self.db.add_all(records)
        await self.db.commit()
        return records
