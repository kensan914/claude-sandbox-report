"""テスト用設定・フィクスチャ。

テスト専用の PostgreSQL データベース (daily_report_test) を使用し、
各テスト間でデータが干渉しないことを保証する。
"""

import os
from collections.abc import AsyncGenerator

import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base

# テスト専用DBのURL（本番DBとは異なるデータベースを使用する）
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/daily_report_test",
)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_async_session = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


def _extract_sync_params_from_url(url: str) -> dict:
    """asyncpg用のDB URLからpsycopg2用の接続パラメータを抽出する。"""
    # "postgresql+asyncpg://user:pass@host:port/dbname" 形式をパースする
    clean = url.replace("postgresql+asyncpg://", "")
    userpass, rest = clean.split("@", 1)
    user, password = userpass.split(":", 1)
    hostport, dbname = rest.split("/", 1)
    host, port = hostport.split(":", 1)
    return {
        "host": host,
        "port": int(port),
        "user": user,
        "password": password,
        "dbname": dbname,
    }


def pytest_configure(config):
    """テスト用データベースが存在しない場合に自動作成する。"""
    params = _extract_sync_params_from_url(TEST_DATABASE_URL)
    test_dbname = params.pop("dbname")

    try:
        conn = psycopg2.connect(**params, dbname="postgres")
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (test_dbname,),
        )
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {test_dbname}")
        cur.close()
        conn.close()
    except Exception:
        # DB接続できない場合は無視する（CI等で別途用意される想定）
        pass


@pytest.fixture(autouse=True)
async def setup_database():
    """テスト実行前にテーブルを作成し、終了後に削除する。"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # テスト間でコネクションプールの不整合を防ぐためにエンジンを破棄する
    await test_engine.dispose()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    """テスト用のDBセッション。各テスト後にロールバックする。"""
    async with test_async_session() as session:
        yield session
        await session.rollback()
