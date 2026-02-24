from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_db_session


class TestGetDb:
    async def test_get_dbジェネレータでセッションが取得できること(self):
        """FastAPI Depends 用のジェネレータが正しくセッションを返すこと。"""
        gen = get_db()
        session = await gen.__anext__()

        assert isinstance(session, AsyncSession)

        # クリーンアップ
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass

    async def test_get_db_sessionでコンテキストマネージャとして使えること(self):
        """async with get_db_session() as session でセッションが取得できること。"""
        async with get_db_session() as session:
            assert isinstance(session, AsyncSession)

            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            assert value == 1

    async def test_セッションがリクエスト単位で独立していること(self):
        """異なる get_db_session 呼び出しが異なるセッションを返すこと。"""
        async with get_db_session() as session1:
            async with get_db_session() as session2:
                assert session1 is not session2
