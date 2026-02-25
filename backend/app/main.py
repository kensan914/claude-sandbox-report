import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.auth import router as auth_router
from app.api.v1.customers import router as customers_router
from app.api.v1.reports import router as reports_router
from app.api.v1.users import router as users_router
from app.core.config import settings
from app.core.exceptions import AppError
from app.schemas.common import ErrorBody, ErrorResponse

logger = logging.getLogger(__name__)

app = FastAPI(
    title="営業日報システム API",
    description="営業日報の作成・管理を行うREST API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """カスタム例外をAPI仕様書形式のJSONレスポンスに変換する。"""
    details = None
    if exc.details:
        details = [{"field": d["field"], "message": d["message"]} for d in exc.details]

    error_response = ErrorResponse(
        error=ErrorBody(
            code=exc.error_code,
            message=exc.message,
            details=details,
        )
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(exclude_none=True),
    )


@app.middleware("http")
async def catch_unhandled_exceptions(request: Request, call_next):
    """予期しない例外を500エラーとして返すミドルウェア。"""
    try:
        return await call_next(request)
    except Exception:
        logger.exception("予期しない例外が発生しました")
        error_response = ErrorResponse(
            error=ErrorBody(
                code="INTERNAL_SERVER_ERROR",
                message="サーバー内部エラーが発生しました",
            )
        )
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump(exclude_none=True),
        )


app.include_router(auth_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(customers_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
