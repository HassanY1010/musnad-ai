"""
MUSNAD AI - Authentication Endpoints
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user, TokenData
from app.models import User, UserRole
from app.schemas import APIResponse, LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(tags=["Auth"])


@router.post("/auth/register", response_model=APIResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    res = await db.execute(select(User).where(User.email == request.email))
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "EMAIL_EXISTS", "message": "Email already registered"},
        )

    user = User(
        id=str(uuid.uuid4()),
        name=request.name,
        email=request.email,
        hashed_password=hash_password(request.password),
        role=UserRole.user,
    )
    db.add(user)
    await db.commit()

    token = create_access_token(subject=user.id, role=user.role.value)
    return APIResponse(
        success=True,
        data=TokenResponse(access_token=token, role=user.role.value, user_id=user.id),
    )


@router.post("/auth/login", response_model=APIResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.email == request.email))
    user = res.scalar_one_or_none()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"},
        )

    token = create_access_token(subject=user.id, role=user.role.value)
    return APIResponse(
        success=True,
        data=TokenResponse(access_token=token, role=user.role.value, user_id=user.id),
    )


@router.get("/auth/me", response_model=APIResponse)
async def get_me(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"},
        )

    return APIResponse(
        success=True,
        data=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role.value,
            created_at=user.created_at,
        ),
    )
