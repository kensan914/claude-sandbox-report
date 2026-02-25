"""顧客のデータアクセス層。"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.models.visit_record import VisitRecord


class CustomerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_list(
        self,
        *,
        company_name: str | None = None,
        contact_name: str | None = None,
        sort: str = "company_name",
        order: str = "asc",
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Customer], int]:
        """検索条件に基づいて顧客一覧を取得する。"""
        query = select(Customer)

        # 部分一致検索
        if company_name is not None:
            query = query.where(Customer.company_name.ilike(f"%{company_name}%"))
        if contact_name is not None:
            query = query.where(Customer.contact_name.ilike(f"%{contact_name}%"))

        # 件数取得
        count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await self.db.execute(count_query)
        total_count = total_count_result.scalar_one()

        # ソート
        sort_column = self._get_sort_column(sort)
        if order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # ページネーション
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        result = await self.db.execute(query)
        customers = result.scalars().all()
        return list(customers), total_count

    def _get_sort_column(self, sort: str):
        """ソート項目名から対応するカラムを返す。"""
        sort_map = {
            "company_name": Customer.company_name,
            "contact_name": Customer.contact_name,
        }
        return sort_map.get(sort, Customer.company_name)

    async def find_by_id(self, customer_id: int) -> Customer | None:
        """IDで顧客を取得する。"""
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()

    async def has_visit_records(self, customer_id: int) -> bool:
        """顧客が訪問記録で使用されているか確認する。"""
        result = await self.db.execute(
            select(func.count())
            .select_from(VisitRecord)
            .where(VisitRecord.customer_id == customer_id)
        )
        return result.scalar_one() > 0

    async def create(self, customer: Customer) -> Customer:
        """顧客を作成する。"""
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def update(self, customer: Customer) -> Customer:
        """顧客を更新する。"""
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def delete(self, customer: Customer) -> None:
        """顧客を削除する。"""
        await self.db.delete(customer)
        await self.db.commit()
