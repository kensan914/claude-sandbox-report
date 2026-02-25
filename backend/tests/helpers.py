"""テスト用共通ヘルパー関数。

各テストファイルから共通で使用するデータ作成・クライアント構築の関数を提供する。
テストデータ定義（docs/TEST_DEFINITION.md）のデフォルト値に準拠する。
"""

from datetime import date, datetime

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import COOKIE_NAME, hash_password
from app.main import app
from app.models.customer import Customer
from app.models.daily_report import DailyReport, ReportStatus
from app.models.user import User, UserRole
from app.models.visit_record import VisitRecord

# ============================================================
# データ作成ヘルパー
# ============================================================

DEFAULT_PASSWORD = "password123"


async def create_user(
    db: AsyncSession,
    *,
    email: str = "tanaka@example.com",
    password: str = DEFAULT_PASSWORD,
    role: UserRole = UserRole.SALES,
    name: str = "田中太郎",
) -> User:
    """テスト用ユーザーを作成する。"""
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_customer(
    db: AsyncSession,
    *,
    company_name: str = "テスト株式会社",
    contact_name: str = "テスト担当",
    address: str | None = None,
    phone: str | None = None,
    email: str | None = None,
) -> Customer:
    """テスト用顧客を作成する。"""
    customer = Customer(
        company_name=company_name,
        contact_name=contact_name,
        address=address,
        phone=phone,
        email=email,
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer


async def create_report(
    db: AsyncSession,
    user: User,
    *,
    report_date: date | None = None,
    status: ReportStatus = ReportStatus.DRAFT,
    problem: str = "テスト課題",
    plan: str = "テスト計画",
) -> DailyReport:
    """テスト用日報を作成する。"""
    if report_date is None:
        report_date = date.today()
    report = DailyReport(
        salesperson_id=user.id,
        report_date=report_date,
        problem=problem,
        plan=plan,
        status=status,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def create_visit_record(
    db: AsyncSession,
    report: DailyReport,
    customer: Customer,
    *,
    visit_content: str = "訪問テスト",
    visited_at: datetime | None = None,
    visit_order: int = 1,
) -> VisitRecord:
    """テスト用訪問記録を作成する。"""
    if visited_at is None:
        visited_at = datetime(1970, 1, 1, 10, 0)
    vr = VisitRecord(
        daily_report_id=report.id,
        customer_id=customer.id,
        visit_content=visit_content,
        visited_at=visited_at,
        visit_order=visit_order,
    )
    db.add(vr)
    await db.commit()
    await db.refresh(vr)
    return vr


# ============================================================
# テスト用HTTPクライアント
# ============================================================


def build_client(
    db_session: AsyncSession, *, token: str | None = None
) -> httpx.AsyncClient:
    """テスト用の非同期HTTPクライアントを構築する。

    db_session のオーバーライドと、オプションの認証トークン設定を行う。
    """

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    cookies = httpx.Cookies()
    if token is not None:
        cookies.set(COOKIE_NAME, token)

    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        cookies=cookies,
    )
