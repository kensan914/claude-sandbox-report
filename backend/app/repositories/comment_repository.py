"""コメントのデータアクセス層。"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.comment import Comment


class CommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, comment: Comment) -> Comment:
        """コメントを作成する。"""
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment, attribute_names=["manager"])
        return comment
