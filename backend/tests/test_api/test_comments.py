from datetime import date

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.daily_report import DailyReport, ReportStatus
from app.models.user import UserRole
from tests.helpers import build_client, create_user


async def _create_report(
    db: AsyncSession,
    user,
    *,
    report_date: date | None = None,
    status_val: ReportStatus = ReportStatus.SUBMITTED,
) -> DailyReport:
    """コメントテスト用の日報を作成する。"""
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


class TestCreateComment:
    async def test_MANAGERがPROBLEMコメントを投稿できること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user)
        token = create_access_token(manager.id)

        async with build_client(db_session, token=token) as client:
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
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user)
        token = create_access_token(manager.id)

        async with build_client(db_session, token=token) as client:
            response = await client.post(
                f"/api/v1/reports/{report.id}/comments",
                json={"target": "PLAN", "content": "了解です"},
            )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["target"] == "PLAN"

    async def test_SALESがコメントを投稿すると403エラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        report = await _create_report(db_session, user)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.post(
                f"/api/v1/reports/{report.id}/comments",
                json={"target": "PROBLEM", "content": "テスト"},
            )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_DRAFT日報にコメントすると403エラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user, status_val=ReportStatus.DRAFT)
        token = create_access_token(manager.id)

        async with build_client(db_session, token=token) as client:
            response = await client.post(
                f"/api/v1/reports/{report.id}/comments",
                json={"target": "PROBLEM", "content": "テスト"},
            )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_不正なtargetで400エラーが返ること(self, db_session: AsyncSession):
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user)
        token = create_access_token(manager.id)

        async with build_client(db_session, token=token) as client:
            response = await client.post(
                f"/api/v1/reports/{report.id}/comments",
                json={"target": "INVALID", "content": "テスト"},
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_存在しない日報IDで404エラーが返ること(
        self, db_session: AsyncSession
    ):
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        token = create_access_token(manager.id)

        async with build_client(db_session, token=token) as client:
            response = await client.post(
                "/api/v1/reports/99999/comments",
                json={"target": "PROBLEM", "content": "テスト"},
            )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_content未入力で422エラーが返ること(self, db_session: AsyncSession):
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        token = create_access_token(manager.id)

        async with build_client(db_session, token=token) as client:
            response = await client.post(
                "/api/v1/reports/1/comments",
                json={"target": "PROBLEM", "content": ""},
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_content文字数超過で422エラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await _create_report(db_session, user)
        token = create_access_token(manager.id)

        async with build_client(db_session, token=token) as client:
            response = await client.post(
                f"/api/v1/reports/{report.id}/comments",
                json={"target": "PROBLEM", "content": "あ" * 1001},
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_未認証で401エラーが返ること(self, db_session: AsyncSession):
        async with build_client(db_session) as client:
            response = await client.post(
                "/api/v1/reports/1/comments",
                json={"target": "PROBLEM", "content": "テスト"},
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
