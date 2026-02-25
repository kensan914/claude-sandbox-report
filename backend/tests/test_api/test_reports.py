from datetime import date, timedelta

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.daily_report import ReportStatus
from app.models.user import UserRole
from tests.helpers import (
    build_client,
    create_customer,
    create_report,
    create_user,
    create_visit_record,
)


class TestGetReports:
    async def test_SALESが自分の日報一覧を取得できること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        await create_report(db_session, user)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/reports")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["pagination"]["total_count"] == 1

    async def test_SALESが他人の日報を取得しないこと(self, db_session: AsyncSession):
        user1 = await create_user(db_session)
        user2 = await create_user(
            db_session,
            email="other@example.com",
            name="他人",
        )
        await create_report(db_session, user2)
        token = create_access_token(user1.id)

        async with build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/reports")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pagination"]["total_count"] == 0

    async def test_MANAGERが全件取得できること(self, db_session: AsyncSession):
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        await create_report(db_session, user)
        token = create_access_token(manager.id)

        async with build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/reports")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pagination"]["total_count"] == 1

    async def test_ステータスで絞り込みできること(self, db_session: AsyncSession):
        user = await create_user(db_session)
        await create_report(db_session, user)
        await create_report(
            db_session,
            user,
            report_date=date.today() - timedelta(days=1),
            status=ReportStatus.SUBMITTED,
        )
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/reports?status=SUBMITTED")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pagination"]["total_count"] == 1

    async def test_未認証で401エラーが返ること(self, db_session: AsyncSession):
        async with build_client(db_session) as client:
            response = await client.get("/api/v1/reports")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_レスポンスにvisit_countが含まれること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        customer = await create_customer(db_session)
        report = await create_report(db_session, user)
        await create_visit_record(db_session, report, customer)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/reports")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"][0]
        assert data["visit_count"] == 1


class TestCreateReport:
    async def test_下書き保存で日報が作成されること(self, db_session: AsyncSession):
        user = await create_user(db_session)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.post(
                "/api/v1/reports",
                json={
                    "report_date": str(date.today()),
                    "problem": "課題テスト",
                    "plan": "計画テスト",
                    "status": "DRAFT",
                },
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()["data"]
        assert data["status"] == "DRAFT"
        assert data["submitted_at"] is None
        assert data["salesperson"]["id"] == user.id

    async def test_提出でsubmitted_atが設定されること(self, db_session: AsyncSession):
        user = await create_user(db_session)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.post(
                "/api/v1/reports",
                json={
                    "report_date": str(date.today()),
                    "status": "SUBMITTED",
                },
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()["data"]
        assert data["status"] == "SUBMITTED"
        assert data["submitted_at"] is not None

    async def test_訪問記録付きで日報が作成されること(self, db_session: AsyncSession):
        user = await create_user(db_session)
        customer = await create_customer(db_session)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.post(
                "/api/v1/reports",
                json={
                    "report_date": str(date.today()),
                    "status": "DRAFT",
                    "visit_records": [
                        {
                            "customer_id": customer.id,
                            "visit_content": "打合せ",
                            "visited_at": "10:00",
                        }
                    ],
                },
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()["data"]
        assert len(data["visit_records"]) == 1
        assert data["visit_records"][0]["customer"]["company_name"] == "テスト株式会社"

    async def test_未来日でバリデーションエラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        token = create_access_token(user.id)
        future_date = date.today() + timedelta(days=1)

        async with build_client(db_session, token=token) as client:
            response = await client.post(
                "/api/v1/reports",
                json={
                    "report_date": str(future_date),
                    "status": "DRAFT",
                },
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()["error"]
        assert error["code"] == "VALIDATION_ERROR"

    async def test_同日重複で409エラーが返ること(self, db_session: AsyncSession):
        user = await create_user(db_session)
        await create_report(db_session, user)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.post(
                "/api/v1/reports",
                json={
                    "report_date": str(date.today()),
                    "status": "DRAFT",
                },
            )

        assert response.status_code == status.HTTP_409_CONFLICT
        error = response.json()["error"]
        assert error["code"] == "CONFLICT"


    async def test_MANAGERが日報を作成すると403エラーが返ること(
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
                "/api/v1/reports",
                json={
                    "report_date": str(date.today()),
                    "status": "DRAFT",
                },
            )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_problem文字数超過で422エラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.post(
                "/api/v1/reports",
                json={
                    "report_date": str(date.today()),
                    "problem": "あ" * 2001,
                    "status": "DRAFT",
                },
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_plan文字数超過で422エラーが返ること(self, db_session: AsyncSession):
        user = await create_user(db_session)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.post(
                "/api/v1/reports",
                json={
                    "report_date": str(date.today()),
                    "plan": "あ" * 2001,
                    "status": "DRAFT",
                },
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_visit_content文字数超過で422エラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        customer = await create_customer(db_session)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.post(
                "/api/v1/reports",
                json={
                    "report_date": str(date.today()),
                    "status": "DRAFT",
                    "visit_records": [
                        {
                            "customer_id": customer.id,
                            "visit_content": "あ" * 1001,
                            "visited_at": "10:00",
                        }
                    ],
                },
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetReportDetail:
    async def test_SALESが自分の日報詳細を取得できること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        customer = await create_customer(db_session)
        report = await create_report(db_session, user)
        await create_visit_record(db_session, report, customer)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.get(f"/api/v1/reports/{report.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["id"] == report.id
        assert data["problem"] == "テスト課題"
        assert len(data["visit_records"]) == 1
        assert "contact_name" in data["visit_records"][0]["customer"]

    async def test_SALESが他人の日報を取得すると403エラーが返ること(
        self, db_session: AsyncSession
    ):
        user1 = await create_user(db_session)
        user2 = await create_user(
            db_session,
            email="other@example.com",
            name="他人",
        )
        report = await create_report(db_session, user1)
        token = create_access_token(user2.id)

        async with build_client(db_session, token=token) as client:
            response = await client.get(f"/api/v1/reports/{report.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_MANAGERが他人の日報を取得できること(self, db_session: AsyncSession):
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await create_report(db_session, user)
        token = create_access_token(manager.id)

        async with build_client(db_session, token=token) as client:
            response = await client.get(f"/api/v1/reports/{report.id}")

        assert response.status_code == status.HTTP_200_OK

    async def test_存在しないIDで404エラーが返ること(self, db_session: AsyncSession):
        user = await create_user(db_session)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/reports/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateReport:
    async def test_DRAFT日報を更新できること(self, db_session: AsyncSession):
        user = await create_user(db_session)
        report = await create_report(db_session, user)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.put(
                f"/api/v1/reports/{report.id}",
                json={
                    "report_date": str(report.report_date),
                    "problem": "更新後の課題",
                    "plan": "更新後の計画",
                    "status": "DRAFT",
                },
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["problem"] == "更新後の課題"
        assert data["plan"] == "更新後の計画"

    async def test_SUBMITTED日報は更新できないこと(self, db_session: AsyncSession):
        user = await create_user(db_session)
        report = await create_report(db_session, user, status=ReportStatus.SUBMITTED)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.put(
                f"/api/v1/reports/{report.id}",
                json={
                    "report_date": str(report.report_date),
                    "status": "DRAFT",
                },
            )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_他人の日報は更新できないこと(self, db_session: AsyncSession):
        user1 = await create_user(db_session)
        user2 = await create_user(
            db_session,
            email="other@example.com",
            name="他人",
        )
        report = await create_report(db_session, user1)
        token = create_access_token(user2.id)

        async with build_client(db_session, token=token) as client:
            response = await client.put(
                f"/api/v1/reports/{report.id}",
                json={
                    "report_date": str(report.report_date),
                    "status": "DRAFT",
                },
            )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_MANAGERが日報を更新すると403エラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await create_report(db_session, user)
        token = create_access_token(manager.id)

        async with build_client(db_session, token=token) as client:
            response = await client.put(
                f"/api/v1/reports/{report.id}",
                json={
                    "report_date": str(report.report_date),
                    "status": "DRAFT",
                },
            )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDeleteReport:
    async def test_DRAFT日報を削除できること(self, db_session: AsyncSession):
        user = await create_user(db_session)
        report = await create_report(db_session, user)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.delete(f"/api/v1/reports/{report.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_SUBMITTED日報は削除できないこと(self, db_session: AsyncSession):
        user = await create_user(db_session)
        report = await create_report(db_session, user, status=ReportStatus.SUBMITTED)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.delete(f"/api/v1/reports/{report.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_他人の日報は削除できないこと(self, db_session: AsyncSession):
        user1 = await create_user(db_session)
        user2 = await create_user(
            db_session,
            email="other@example.com",
            name="他人",
        )
        report = await create_report(db_session, user1)
        token = create_access_token(user2.id)

        async with build_client(db_session, token=token) as client:
            response = await client.delete(f"/api/v1/reports/{report.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_MANAGERが日報を削除すると403エラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await create_report(db_session, user)
        token = create_access_token(manager.id)

        async with build_client(db_session, token=token) as client:
            response = await client.delete(f"/api/v1/reports/{report.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_存在しないIDで404エラーが返ること(self, db_session: AsyncSession):
        user = await create_user(db_session)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.delete("/api/v1/reports/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestSubmitReport:
    async def test_DRAFT日報を提出できること(self, db_session: AsyncSession):
        user = await create_user(db_session)
        report = await create_report(db_session, user)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.patch(f"/api/v1/reports/{report.id}/submit")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["id"] == report.id
        assert data["status"] == "SUBMITTED"
        assert data["submitted_at"] is not None

    async def test_SUBMITTED日報を提出すると409エラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        report = await create_report(db_session, user, status=ReportStatus.SUBMITTED)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.patch(f"/api/v1/reports/{report.id}/submit")

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["error"]["code"] == "CONFLICT"

    async def test_他人の日報を提出すると403エラーが返ること(
        self, db_session: AsyncSession
    ):
        user1 = await create_user(db_session)
        user2 = await create_user(db_session, email="other@example.com", name="他人")
        report = await create_report(db_session, user1)
        token = create_access_token(user2.id)

        async with build_client(db_session, token=token) as client:
            response = await client.patch(f"/api/v1/reports/{report.id}/submit")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_存在しないIDで404エラーが返ること(self, db_session: AsyncSession):
        user = await create_user(db_session)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.patch("/api/v1/reports/99999/submit")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestReviewReport:
    async def test_MANAGERがSUBMITTED日報を確認済みにできること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await create_report(db_session, user, status=ReportStatus.SUBMITTED)
        token = create_access_token(manager.id)

        async with build_client(db_session, token=token) as client:
            response = await client.patch(f"/api/v1/reports/{report.id}/review")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["id"] == report.id
        assert data["status"] == "REVIEWED"

    async def test_DRAFT日報を確認済みにすると409エラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        report = await create_report(db_session, user)
        token = create_access_token(manager.id)

        async with build_client(db_session, token=token) as client:
            response = await client.patch(f"/api/v1/reports/{report.id}/review")

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["error"]["code"] == "CONFLICT"

    async def test_SALESが確認済みにしようとすると403エラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await create_user(db_session)
        report = await create_report(db_session, user, status=ReportStatus.SUBMITTED)
        token = create_access_token(user.id)

        async with build_client(db_session, token=token) as client:
            response = await client.patch(f"/api/v1/reports/{report.id}/review")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_存在しないIDで404エラーが返ること(self, db_session: AsyncSession):
        manager = await create_user(
            db_session,
            email="manager@example.com",
            name="部長",
            role=UserRole.MANAGER,
        )
        token = create_access_token(manager.id)

        async with build_client(db_session, token=token) as client:
            response = await client.patch("/api/v1/reports/99999/review")

        assert response.status_code == status.HTTP_404_NOT_FOUND
