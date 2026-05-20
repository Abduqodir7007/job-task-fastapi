"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_db
from app.models.users import User, Role
from app.schemas.users import UserRegisterSchema, UserLoginSchema, TokenSchema, UserResponseSchema
from app.utils import hash_password, verify_password, create_access_token, create_refresh_token

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/register", response_model=TokenSchema, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegisterSchema, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    roles = await db.execute(select(Role).where(Role.name.in_(["user"])))
    roles = roles.scalars().all()

    admin_roles = [r for r in roles if r.name == "admin"]
    if admin_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Admin role cannot be assigned during registration"
        )

    user = User(
        email=user_data.email,
        password=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_active=True,
        is_staff=False,
    )
    user.roles = roles

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=TokenSchema)
async def login(user_data: UserLoginSchema, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalars().first()

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
