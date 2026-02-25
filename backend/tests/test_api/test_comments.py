from datetime import date

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    COOKIE_NAME,
    create_access_token,
    hash_password,
)
from app.main import app
from app.models.daily_report import DailyReport, ReportStatus
from app.models.user import User, UserRole


async def _create_user(
    db: AsyncSession,
    *,
    email: str = "tanaka@example.com",
    role: UserRole = UserRole.SALES,
    name: str = "田中太郎",
) -> User:
    user = User(
        name=name,
        email=email,
        password_hash=hash_password("password123"),
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _create_report(
    db: AsyncSession,
    user: User,
    *,
    report_date: date | None = None,
    status_val: ReportStatus = ReportStatus.SUBMITTED,
) -> DailyReport:
    if report_date is None:
        report_date = date.today()
    report = DailyReport(
        salesperson_id=user.id,
        report_date=report_date,
        problem="テスト課題",
        plan="テスト計画",
        status=status_val,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


def _build_client(
    db_session: AsyncSession, *, token: str | None = None
) -> httpx.AsyncClient:
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


class TestCreateComment:
    async def test_MANAGERがPROBLEMコメントを投稿できること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        manager = await _create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user)
        token = create_access_token(manager.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.post(
                f"/api/v1/reports/{report.id}/comments",
                json={"target": "PROBLEM", "content": "確認しました"},
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()["data"]
        assert data["target"] == "PROBLEM"
        assert data["content"] == "確認しました"
        assert data["manager"]["id"] == manager.id
        assert data["manager"]["name"] == "部長"
        assert data["created_at"] is not None

    async def test_MANAGERがPLANコメントを投稿できること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        manager = await _create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user)
        token = create_access_token(manager.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.post(
                f"/api/v1/reports/{report.id}/comments",
                json={"target": "PLAN", "content": "了解です"},
            )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["target"] == "PLAN"

    async def test_SALESがコメントを投稿すると403エラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        report = await _create_report(db_session, user)
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.post(
                f"/api/v1/reports/{report.id}/comments",
                json={"target": "PROBLEM", "content": "テスト"},
            )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_DRAFT日報にコメントすると403エラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        manager = await _create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(
            db_session, user, status_val=ReportStatus.DRAFT
        )
        token = create_access_token(manager.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.post(
                f"/api/v1/reports/{report.id}/comments",
                json={"target": "PROBLEM", "content": "テスト"},
            )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_不正なtargetで400エラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        manager = await _create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user)
        token = create_access_token(manager.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.post(
                f"/api/v1/reports/{report.id}/comments",
                json={"target": "INVALID", "content": "テスト"},
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_存在しない日報IDで404エラーが返ること(
        self, db_session: AsyncSession
    ):
        manager = await _create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        token = create_access_token(manager.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.post(
                "/api/v1/reports/99999/comments",
                json={"target": "PROBLEM", "content": "テスト"},
            )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_content未入力で422エラーが返ること(
        self, db_session: AsyncSession
    ):
        manager = await _create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        token = create_access_token(manager.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.post(
                "/api/v1/reports/1/comments",
                json={"target": "PROBLEM", "content": ""},
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_未認証で401エラーが返ること(self, db_session: AsyncSession):
        async with _build_client(db_session) as client:
            response = await client.post(
                "/api/v1/reports/1/comments",
                json={"target": "PROBLEM", "content": "テスト"},
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
