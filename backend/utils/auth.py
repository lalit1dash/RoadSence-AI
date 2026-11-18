"""
Authentication & JWT Security Utilities
Handles password hashing with bcrypt, JWT token generation & verification.
"""

from __future__ import annotations

import datetime
import logging
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from config import settings
from database.connection import get_collection

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
SECRET_KEY = getattr(settings, "SECRET_KEY", "roadsense-secure-jwt-secret-key-32bytes-long-for-production!")
if len(SECRET_KEY) < 32:
    SECRET_KEY = SECRET_KEY.ljust(32, "x")

# In-memory users store fallback
IN_MEMORY_USERS: dict[str, dict] = {}


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        logger.warning(f"Password verification error: {e}")
        return False


def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Generate a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.debug("Token has expired.")
        return None
    except jwt.PyJWTError as e:
        logger.debug(f"JWT decode error: {e}")
        return None


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> dict:
    """
    FastAPI dependency: extracts and validates user from Authorization: Bearer <token>.
    Raises 401 if missing or invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    # Check MongoDB first
    users_col = get_collection("users")
    if users_col is not None:
        user = await users_col.find_one({"email": email})
        if user:
            user["id"] = str(user.pop("_id", user.get("id", "")))
            user.pop("hashed_password", None)
            return user

    # Check in-memory store
    if email in IN_MEMORY_USERS:
        user = dict(IN_MEMORY_USERS[email])
        user.pop("hashed_password", None)
        return user

    raise credentials_exception


async def get_optional_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[dict]:
    """
    FastAPI dependency: returns user dict if valid token is provided, or None if unauthenticated.
    """
    if not token:
        return None
    try:
        return await get_current_user(token)
    except HTTPException:
        return None
