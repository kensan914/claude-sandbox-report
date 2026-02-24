import datetime

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# Cookie 設定の定数
COOKIE_NAME = "access_token"
COOKIE_PATH = "/api"
COOKIE_SAMESITE = "lax"


def hash_password(password: str) -> str:
    """平文パスワードをbcryptでハッシュ化する。"""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """平文パスワードとハッシュ値を照合する。"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(user_id: int) -> str:
    """ユーザーIDを含むJWTアクセストークンを生成する。"""
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> int | None:
    """JWTトークンをデコードし、ユーザーIDを返す。無効な場合はNoneを返す。"""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            return None
        return int(user_id_str)
    except JWTError, ValueError:
        return None
