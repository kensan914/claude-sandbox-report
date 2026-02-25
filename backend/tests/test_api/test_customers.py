from datetime import date, datetime

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import COOKIE_NAME, create_access_token, hash_password
from app.main import app
from app.models.customer import Customer
from app.models.daily_report import DailyReport, ReportStatus
from app.models.user import User, UserRole
from app.models.visit_record import VisitRecord


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


async def _create_customer(
    db: AsyncSession,
    *,
    company_name: str = "テスト株式会社",
    contact_name: str = "テスト担当",
    address: str | None = None,
    phone: str | None = None,
    email: str | None = None,
) -> Customer:
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


async def _create_visit_record_for_customer(
    db: AsyncSession,
    customer: Customer,
) -> None:
    """顧客に紐づく訪問記録を作成する（削除テスト用）。"""
    user = await _create_user(db, email="vr-user@example.com", name="訪問者")
    report = DailyReport(
        salesperson_id=user.id,
        report_date=date(2025, 1, 1),
        status=ReportStatus.DRAFT,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    vr = VisitRecord(
        daily_report_id=report.id,
        customer_id=customer.id,
        visit_content="テスト訪問",
        visited_at=datetime(1970, 1, 1, 10, 0),
        visit_order=1,
    )
    db.add(vr)
    await db.commit()


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


class TestGetCustomers:
    async def test_顧客一覧を取得できること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        await _create_customer(db_session)
        await _create_customer(
            db_session, company_name="別会社", contact_name="別担当"
        )
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/customers")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total_count"] == 2

    async def test_会社名で部分一致検索できること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        await _create_customer(db_session, company_name="○○株式会社")
        await _create_customer(
            db_session, company_name="△△商事", contact_name="別担当"
        )
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/customers?company_name=○○")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["company_name"] == "○○株式会社"

    async def test_担当者名で部分一致検索できること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        await _create_customer(db_session, contact_name="佐藤一郎")
        await _create_customer(
            db_session, company_name="別会社", contact_name="田中二郎"
        )
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/customers?contact_name=佐藤")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["contact_name"] == "佐藤一郎"

    async def test_ページネーションが動作すること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        for i in range(3):
            await _create_customer(
                db_session, company_name=f"会社{i}", contact_name=f"担当{i}"
            )
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/customers?per_page=2&page=1")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total_count"] == 3
        assert data["pagination"]["total_pages"] == 2

    async def test_未認証で401エラーが返ること(self, db_session: AsyncSession):
        async with _build_client(db_session) as client:
            response = await client.get("/api/v1/customers")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCreateCustomer:
    async def test_必須項目のみで顧客が作成されること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.post(
                "/api/v1/customers",
                json={
                    "company_name": "新規株式会社",
                    "contact_name": "新規担当",
                },
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()["data"]
        assert data["company_name"] == "新規株式会社"
        assert data["contact_name"] == "新規担当"
        assert data["address"] is None
        assert data["created_at"] is not None

    async def test_全項目入力で顧客が作成されること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.post(
                "/api/v1/customers",
                json={
                    "company_name": "新規株式会社",
                    "contact_name": "新規担当",
                    "address": "東京都千代田区1-1-1",
                    "phone": "03-1234-5678",
                    "email": "info@test.co.jp",
                },
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()["data"]
        assert data["address"] == "東京都千代田区1-1-1"
        assert data["phone"] == "03-1234-5678"
        assert data["email"] == "info@test.co.jp"

    async def test_会社名未入力でバリデーションエラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.post(
                "/api/v1/customers",
                json={
                    "contact_name": "担当者",
                },
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetCustomerDetail:
    async def test_顧客詳細を取得できること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        customer = await _create_customer(
            db_session,
            company_name="詳細テスト会社",
            address="東京都",
            phone="03-0000-0000",
        )
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.get(f"/api/v1/customers/{customer.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["id"] == customer.id
        assert data["company_name"] == "詳細テスト会社"
        assert data["address"] == "東京都"

    async def test_存在しないIDで404エラーが返ること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.get("/api/v1/customers/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateCustomer:
    async def test_顧客を更新できること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        customer = await _create_customer(db_session)
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.put(
                f"/api/v1/customers/{customer.id}",
                json={
                    "company_name": "更新後会社名",
                    "contact_name": "更新後担当",
                    "address": "大阪府",
                },
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["company_name"] == "更新後会社名"
        assert data["contact_name"] == "更新後担当"
        assert data["address"] == "大阪府"

    async def test_存在しないIDで404エラーが返ること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.put(
                "/api/v1/customers/99999",
                json={
                    "company_name": "テスト",
                    "contact_name": "テスト",
                },
            )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteCustomer:
    async def test_訪問記録で未使用の顧客を削除できること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        customer = await _create_customer(db_session)
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.delete(f"/api/v1/customers/{customer.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_訪問記録で使用中の顧客を削除すると409エラーが返ること(
        self, db_session: AsyncSession
    ):
        user = await _create_user(db_session)
        customer = await _create_customer(db_session)
        await _create_visit_record_for_customer(db_session, customer)
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.delete(f"/api/v1/customers/{customer.id}")

        assert response.status_code == status.HTTP_409_CONFLICT
        error = response.json()["error"]
        assert error["code"] == "CONFLICT"
        assert "訪問記録で使用されている" in error["message"]

    async def test_存在しないIDで404エラーが返ること(self, db_session: AsyncSession):
        user = await _create_user(db_session)
        token = create_access_token(user.id)

        async with _build_client(db_session, token=token) as client:
            response = await client.delete("/api/v1/customers/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
