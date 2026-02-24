import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.daily_report import DailyReport
    from app.models.user import User


class CommentTarget(enum.StrEnum):
    PROBLEM = "PROBLEM"
    PLAN = "PLAN"


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    daily_report_id: Mapped[int] = mapped_column(
        ForeignKey("daily_reports.id", ondelete="CASCADE"), nullable=False
    )
    manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    target: Mapped[CommentTarget] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    # リレーションシップ
    daily_report: Mapped[DailyReport] = relationship(back_populates="comments")
    manager: Mapped[User] = relationship(back_populates="comments")
