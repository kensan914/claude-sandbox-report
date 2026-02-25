from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # CORS
    allowed_origins: str = "http://localhost:3000"

    # Database
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/daily_report"
    )

    # JWT
    secret_key: str = "local-dev-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Cookie
    cookie_secure: bool = False

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
