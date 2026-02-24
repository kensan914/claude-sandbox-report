from app.core.config import Settings


class TestSettings:
    def test_デフォルト値でSettingsが生成されること(self):
        s = Settings()

        assert s.database_url == (
            "postgresql+asyncpg://postgres:postgres@localhost:5432/daily_report"
        )
        assert s.secret_key == "local-dev-secret-key"
        assert s.algorithm == "HS256"
        assert s.access_token_expire_minutes == 30
        assert s.allowed_origins == "http://localhost:3000"

    def test_環境変数でDATABASE_URLを上書きできること(self, monkeypatch):
        custom_url = "postgresql+asyncpg://user:pass@dbhost:5432/testdb"
        monkeypatch.setenv("DATABASE_URL", custom_url)

        s = Settings()

        assert s.database_url == custom_url

    def test_環境変数でSECRET_KEYを上書きできること(self, monkeypatch):
        monkeypatch.setenv("SECRET_KEY", "my-production-secret")

        s = Settings()

        assert s.secret_key == "my-production-secret"

    def test_環境変数でALLOWED_ORIGINSを上書きできること(self, monkeypatch):
        monkeypatch.setenv("ALLOWED_ORIGINS", "https://example.com")

        s = Settings()

        assert s.allowed_origins == "https://example.com"

    def test_環境変数でACCESS_TOKEN_EXPIRE_MINUTESを上書きできること(self, monkeypatch):
        monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

        s = Settings()

        assert s.access_token_expire_minutes == 60

    def test_未定義の環境変数は無視されること(self, monkeypatch):
        monkeypatch.setenv("UNKNOWN_VARIABLE", "should_be_ignored")

        # extra="ignore" により例外が発生しないこと
        s = Settings()

        assert not hasattr(s, "unknown_variable")
