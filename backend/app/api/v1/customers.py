"""顧客エンドポイント（CRUD）。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.customer_repository import CustomerRepository
from app.schemas.common import DataResponse, create_paginated_response
from app.schemas.customer import (
    CustomerCreateRequest,
    CustomerListItemResponse,
    CustomerResponse,
    CustomerUpdateRequest,
)
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["顧客"])


def _get_customer_service(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> CustomerService:
    """顧客サービスの依存注入。"""
    return CustomerService(CustomerRepository(db))


@router.get("")
async def get_customers(
    company_name: str | None = Query(default=None),  # noqa: B008
    contact_name: str | None = Query(default=None),  # noqa: B008
    sort: str = Query(default="company_name"),
    order: str = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    service: CustomerService = Depends(_get_customer_service),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    """顧客一覧を取得する。"""
    customers, total_count = await service.get_list(
        company_name=company_name,
        contact_name=contact_name,
        sort=sort,
        order=order,
        page=page,
        per_page=per_page,
    )

    data = [
        CustomerListItemResponse.model_validate(c).model_dump(mode="json")
        for c in customers
    ]
    return create_paginated_response(
        data=data,
        total_count=total_count,
        page=page,
        per_page=per_page,
    )


@router.post(
    "",
    status_code=201,
    response_model=DataResponse[CustomerResponse],
)
async def create_customer(
    request: CustomerCreateRequest,
    service: CustomerService = Depends(_get_customer_service),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    """顧客を登録する。"""
    customer = await service.create(request)
    return DataResponse(data=CustomerResponse.model_validate(customer))


@router.get(
    "/{customer_id}",
    response_model=DataResponse[CustomerResponse],
)
async def get_customer(
    customer_id: int,
    service: CustomerService = Depends(_get_customer_service),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    """顧客詳細を取得する。"""
    customer = await service.get_detail(customer_id)
    return DataResponse(data=CustomerResponse.model_validate(customer))


@router.put(
    "/{customer_id}",
    response_model=DataResponse[CustomerResponse],
)
async def update_customer(
    customer_id: int,
    request: CustomerUpdateRequest,
    service: CustomerService = Depends(_get_customer_service),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    """顧客を更新する。"""
    customer = await service.update(customer_id, request)
    return DataResponse(data=CustomerResponse.model_validate(customer))


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: int,
    service: CustomerService = Depends(_get_customer_service),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    """顧客を削除する。"""
    await service.delete(customer_id)
