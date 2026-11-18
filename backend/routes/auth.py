"""
Authentication routes – Registration, Login, Token generation, Current user info.
"""

from __future__ import annotations

import datetime
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from database.connection import get_collection
from utils.auth import (
    IN_MEMORY_USERS,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ── Pydantic Request/Response Models ──────────────────────────────────────────

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=60, example="Dr. Jane Smith")
    email: str = Field(..., min_length=5, max_length=120, example="jane.smith@roadsense.ai")
    password: str = Field(..., min_length=6, max_length=100, example="SecurePassword123")
    role: str = Field(default="inspector", example="inspector")  # inspector | engineer | admin


class UserLogin(BaseModel):
    email: str = Field(..., example="jane.smith@roadsense.ai")
    password: str = Field(..., example="SecurePassword123")


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# Pre-seed a default demo user for instant login
DEFAULT_DEMO_EMAIL = "inspector@roadsense.ai"
DEFAULT_DEMO_PASS = "demo12345"

if DEFAULT_DEMO_EMAIL not in IN_MEMORY_USERS:
    IN_MEMORY_USERS[DEFAULT_DEMO_EMAIL] = {
        "id": "demo-user-001",
        "name": "Alex Mercer (Inspector)",
        "email": DEFAULT_DEMO_EMAIL,
        "hashed_password": hash_password(DEFAULT_DEMO_PASS),
        "role": "inspector",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister):
    """Register a new user account and return JWT access token."""
    email_clean = payload.email.lower().strip()

    # Check MongoDB
    users_col = get_collection("users")
    if users_col is not None:
        existing = await users_col.find_one({"email": email_clean})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists.",
            )

    # Check in-memory store
    if email_clean in IN_MEMORY_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    user_id = uuid.uuid4().hex
    hashed_pwd = hash_password(payload.password)

    user_doc = {
        "id": user_id,
        "name": payload.name.strip(),
        "email": email_clean,
        "hashed_password": hashed_pwd,
        "role": payload.role.lower().strip() if payload.role else "inspector",
        "created_at": now,
    }

    if users_col is not None:
        db_doc = dict(user_doc)
        result = await users_col.insert_one(db_doc)
        user_doc["id"] = str(result.inserted_id)

    # Save to memory cache
    IN_MEMORY_USERS[email_clean] = user_doc

    token = create_access_token(data={"sub": email_clean, "role": user_doc["role"], "name": user_doc["name"]})

    user_out = UserOut(
        id=user_doc["id"],
        name=user_doc["name"],
        email=user_doc["email"],
        role=user_doc["role"],
        created_at=user_doc["created_at"],
    )

    return AuthResponse(access_token=token, token_type="bearer", user=user_out)


@router.post("/login", response_model=AuthResponse)
async def login(payload: UserLogin):
    """Authenticate with email and password and return JWT access token."""
    email_clean = payload.email.lower().strip()
    user_record = None

    # Check MongoDB
    users_col = get_collection("users")
    if users_col is not None:
        user_record = await users_col.find_one({"email": email_clean})
        if user_record:
            user_record["id"] = str(user_record.pop("_id", user_record.get("id", "")))

    # Fallback to in-memory store
    if not user_record and email_clean in IN_MEMORY_USERS:
        user_record = dict(IN_MEMORY_USERS[email_clean])

    if not user_record or not verify_password(payload.password, user_record.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": email_clean, "role": user_record.get("role", "inspector"), "name": user_record.get("name", "")})

    user_out = UserOut(
        id=user_record["id"],
        name=user_record["name"],
        email=user_record["email"],
        role=user_record.get("role", "inspector"),
        created_at=user_record.get("created_at", ""),
    )

    return AuthResponse(access_token=token, token_type="bearer", user=user_out)


@router.post("/token")
async def oauth2_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatible token login for Swagger UI."""
    return await login(UserLogin(email=form_data.username, password=form_data.password))


@router.get("/me", response_model=UserOut)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Return currently authenticated user profile."""
    return UserOut(
        id=str(current_user.get("id", "")),
        name=current_user.get("name", "User"),
        email=current_user.get("email", ""),
        role=current_user.get("role", "inspector"),
        created_at=current_user.get("created_at", ""),
    )
