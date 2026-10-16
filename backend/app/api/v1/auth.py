"""
Authentication Endpoints - Login, Refresh Token, Demo Accounts
"""
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Body, Depends, Header, HTTPException, status, Response, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    get_current_user, get_demo_user, require_role
)
from app.core.logging import get_logger, audit_log
from app.db.session import get_db
from app.models.user import User

router = APIRouter()
logger = get_logger(__name__)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: Optional[str] = None


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    response: Response,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return access + refresh tokens."""
    # Find user
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        audit_log("login_failed", email=credentials.email, request_id=getattr(request.state, "request_id", None))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    # Create tokens
    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_MINUTES),
    )
    refresh_token = create_refresh_token(
        {"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=timedelta(days=7),
    )
    
    # Set refresh token in httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.APP_ENV == "prod",
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )
    
    audit_log("login_success", user_id=str(user.id), role=user.role)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={"id": user.id, "email": user.email, "role": user.role, "name": user.name},
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    body: Optional[RefreshRequest] = Body(default=None),
    refresh_token: Optional[str] = None,
    authorization: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token from cookie or body."""
    if authorization and authorization.lower().startswith("bearer "):
        refresh_token = authorization[7:].strip()
    if not refresh_token and body:
        refresh_token = body.refresh_token
    if not refresh_token:
        refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )
    
    from app.core.security import decode_token
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Get user
    result = await db.execute(select(User).where(User.id == int(payload["sub"])))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Create new tokens (rotate refresh token)
    new_access = create_access_token(
        {"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_MINUTES),
    )
    new_refresh = create_refresh_token(
        {"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=timedelta(days=7),
    )
    
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=settings.APP_ENV == "prod",
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )
    
    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        user={"id": user.id, "email": user.email, "role": user.role, "name": user.name},
    )


@router.post("/demo/{role}", response_model=TokenResponse)
async def demo_login(
    role: str,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Get demo account token (only in DEMO_MODE)."""
    if not settings.DEMO_MODE:
        raise HTTPException(status_code=403, detail="Demo mode disabled")
    
    valid_roles = ["guest", "resident", "manager"] + (
        ["admin"] if settings.DEMO_ALLOW_ADMIN else []
    )
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {valid_roles}")
    
    # Find or create demo user
    email = f"{role}@demo.recircle"
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            email=email,
            password_hash=get_password_hash("demo123"),
            role=role,
            name=f"Demo {role.title()}",
            is_demo=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_MINUTES),
    )
    refresh_token = create_refresh_token(
        {"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=timedelta(days=7),
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.APP_ENV == "prod",
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={"id": user.id, "email": user.email, "role": user.role, "name": user.name},
    )


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user info."""
    return user


@router.post("/logout")
async def logout(response: Response):
    """Logout - clear refresh token cookie."""
    response.delete_cookie(key="refresh_token", httponly=True, secure=settings.APP_ENV == "prod", samesite="lax")
    return {"message": "Logged out"}