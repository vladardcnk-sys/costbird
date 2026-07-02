import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, redirect, session

SECRET = os.getenv("SECRET_KEY", "change-me-in-production-min-32-chars")
ALGO   = "HS256"
TTL    = 60 * 24 * 7  # 7 дней в минутах


def create_token(user_id: int, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=TTL),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGO])
    except jwt.PyJWTError:
        return None


def current_user_id() -> int | None:
    token = session.get("token") or request.cookies.get("token")
    if not token:
        return None
    payload = decode_token(token)
    return payload["sub"] if payload else None


def login_required(f):
    """Декоратор — перенаправляет на /auth/login если не авторизован."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user_id():
            return redirect("/auth/login")
        return f(*args, **kwargs)
    return wrapper
