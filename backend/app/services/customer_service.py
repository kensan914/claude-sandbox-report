"""顧客のビジネスロジック層。"""

from app.core.exceptions import ConflictError, NotFoundError
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreateRequest, CustomerUpdateRequest


class CustomerService:
    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository

    async def get_list(
        self,
        *,
        company_name: str | None = None,
        contact_name: str | None = None,
        sort: str = "company_name",
        order: str = "asc",
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Customer], int]:
        """顧客一覧を取得する。"""
        return await self.customer_repository.find_list(
            company_name=company_name,
            contact_name=contact_name,
            sort=sort,
            order=order,
            page=page,
            per_page=per_page,
        )

    async def get_detail(self, customer_id: int) -> Customer:
        """顧客詳細を取得する。"""
        customer = await self.customer_repository.find_by_id(customer_id)
        if customer is None:
            raise NotFoundError(message="顧客が見つかりません")
        return customer

    async def create(self, request: CustomerCreateRequest) -> Customer:
        """顧客を作成する。"""
        customer = Customer(
            company_name=request.company_name,
            contact_name=request.contact_name,
            address=request.address,
            phone=request.phone,
            email=request.email,
        )
        return await self.customer_repository.create(customer)

    async def update(
        self, customer_id: int, request: CustomerUpdateRequest
    ) -> Customer:
        """顧客を更新する。"""
        customer = await self.customer_repository.find_by_id(customer_id)
        if customer is None:
            raise NotFoundError(message="顧客が見つかりません")

        customer.company_name = request.company_name
        customer.contact_name = request.contact_name
        customer.address = request.address
        customer.phone = request.phone
        customer.email = request.email

        return await self.customer_repository.update(customer)

    async def delete(self, customer_id: int) -> None:
        """顧客を削除する。"""
        customer = await self.customer_repository.find_by_id(customer_id)
        if customer is None:
            raise NotFoundError(message="顧客が見つかりません")

        # 訪問記録で使用中かチェック
        if await self.customer_repository.has_visit_records(customer_id):
            raise ConflictError(
                message="この顧客は訪問記録で使用されているため削除できません"
            )

        await self.customer_repository.delete(customer)
