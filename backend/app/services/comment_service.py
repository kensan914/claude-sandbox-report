"""コメントのビジネスロジック層。"""

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.comment import Comment, CommentTarget
from app.models.daily_report import ReportStatus
from app.models.user import User, UserRole
from app.repositories.comment_repository import CommentRepository
from app.repositories.report_repository import ReportRepository
from app.schemas.comment import CommentCreateRequest


class CommentService:
    def __init__(
        self,
        comment_repository: CommentRepository,
        report_repository: ReportRepository,
    ):
        self.comment_repository = comment_repository
        self.report_repository = report_repository

    async def create(
        self,
        report_id: int,
        request: CommentCreateRequest,
        current_user: User,
    ) -> Comment:
        """コメントを投稿する。"""
        # MANAGERロールチェック
        if current_user.role != UserRole.MANAGER:
            raise ForbiddenError(message="上長のみコメントを投稿できます")

        # 日報の存在チェック
        report = await self.report_repository.find_by_id(report_id)
        if report is None:
            raise NotFoundError(message="日報が見つかりません")

        # DRAFT日報へのコメント禁止
        if report.status == ReportStatus.DRAFT:
            raise ForbiddenError(message="下書きの日報にはコメントできません")

        # targetのバリデーション
        try:
            target = CommentTarget(request.target)
        except ValueError as err:
            raise ValidationError(
                message="入力内容に誤りがあります",
                details=[
                    {
                        "field": "target",
                        "message": "targetはPROBLEMまたはPLANを指定してください",
                    }
                ],
            ) from err

        comment = Comment(
            daily_report_id=report_id,
            manager_id=current_user.id,
            target=target,
            content=request.content,
        )
        return await self.comment_repository.create(comment)
