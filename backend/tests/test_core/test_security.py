import time

from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestHashPassword:
    async def test_ハッシュ値が平文と異なること(self):
        plain = "password123"
        hashed = hash_password(plain)
        assert hashed != plain

    async def test_同じ平文でも毎回異なるハッシュが生成されること(self):
        """bcryptのソルトにより同一入力でも異なるハッシュになる。"""
        plain = "password123"
        hash1 = hash_password(plain)
        hash2 = hash_password(plain)
        assert hash1 != hash2

    async def test_ハッシュ値がbcrypt形式であること(self):
        hashed = hash_password("test")
        assert hashed.startswith("$2b$")


class TestVerifyPassword:
    async def test_正しいパスワードで検証が成功すること(self):
        plain = "password123"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    async def test_誤ったパスワードで検証が失敗すること(self):
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    async def test_空文字パスワードのハッシュ化と検証ができること(self):
        plain = ""
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True
        assert verify_password("notempty", hashed) is False


class TestCreateAccessToken:
    async def test_トークンが文字列で返されること(self):
        token = create_access_token(user_id=1)
        assert isinstance(token, str)
        assert len(token) > 0

    async def test_トークンにユーザーIDが含まれること(self):
        token = create_access_token(user_id=42)
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert payload["sub"] == "42"

    async def test_トークンに有効期限が含まれること(self):
        token = create_access_token(user_id=1)
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert "exp" in payload


class TestDecodeAccessToken:
    async def test_正常なトークンからユーザーIDが取得できること(self):
        token = create_access_token(user_id=99)
        user_id = decode_access_token(token)
        assert user_id == 99

    async def test_不正なトークンでNoneが返ること(self):
        assert decode_access_token("invalid.token.string") is None

    async def test_異なるsecretで署名されたトークンでNoneが返ること(self):
        token = jwt.encode(
            {"sub": "1", "exp": time.time() + 3600},
            "different-secret",
            algorithm="HS256",
        )
        assert decode_access_token(token) is None

    async def test_subクレームがないトークンでNoneが返ること(self):
        token = jwt.encode(
            {"exp": time.time() + 3600},
            settings.secret_key,
            algorithm=settings.algorithm,
        )
        assert decode_access_token(token) is None

    async def test_期限切れトークンでNoneが返ること(self):
        token = jwt.encode(
            {"sub": "1", "exp": time.time() - 1},
            settings.secret_key,
            algorithm=settings.algorithm,
        )
        assert decode_access_token(token) is None
