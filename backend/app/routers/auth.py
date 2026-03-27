"""
Authentication router using Supabase Auth.
Handles user signup, login, and session management.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.services.supabase_service import (
    signup_user,
    login_user,
    get_user_from_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ==================== Models ====================

class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str


class AuthResponse(BaseModel):
    user: Optional[UserResponse] = None
    session: Optional[dict] = None
    message: str


# ==================== Dependencies ====================

async def get_current_user(authorization: str = Header(...)) -> dict:
    """Extract and verify user from Authorization header.

    Usage: Depends(get_current_user)
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.replace("Bearer ", "")
    user = await get_user_from_token(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user


# ==================== Endpoints ====================

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    """Register a new user with email and password."""
    try:
        result = await signup_user(request.email, request.password)
        return AuthResponse(
            user=UserResponse(**result["user"]) if result["user"] else None,
            session=result["session"],
            message="Account created successfully. You can now sign in!",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login with email and password."""
    try:
        result = await login_user(request.email, request.password)
        return AuthResponse(
            user=UserResponse(**result["user"]),
            session=result["session"],
            message="Login successful",
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid email or password")


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """Get the currently authenticated user's info."""
    return UserResponse(**user)
