import enum
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.user import User
    from app.models.visit_record import VisitRecord


class ReportStatus(enum.StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    REVIEWED = "REVIEWED"


class DailyReport(Base):
    __tablename__ = "daily_reports"
    __table_args__ = (
        # 担当者 × 報告日のユニーク制約
        UniqueConstraint("salesperson_id", "report_date", name="uq_salesperson_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    salesperson_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    problem: Mapped[str | None] = mapped_column(Text, nullable=True)
    plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ReportStatus] = mapped_column(
        nullable=False, default=ReportStatus.DRAFT
    )
    submitted_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    # リレーションシップ
    salesperson: Mapped[User] = relationship(back_populates="daily_reports")
    visit_records: Mapped[list[VisitRecord]] = relationship(
        back_populates="daily_report", cascade="all, delete-orphan"
    )
    comments: Mapped[list[Comment]] = relationship(
        back_populates="daily_report", cascade="all, delete-orphan"
    )
