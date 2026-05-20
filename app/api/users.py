from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, or_
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.dependencies import check_admin_role
from app.models.users import Role, User
from app.schemas.users import UserCreateSchema, UserUpdateSchema, UserResponseSchema
from app.utils import hash_password

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    dependencies=[Depends(check_admin_role)],
)


async def _get_user_or_404(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).options(selectinload(User.roles)).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def _get_roles_or_400(db: AsyncSession, role_ids: list[int]) -> list[Role]:
    if not role_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one role is required")

    result = await db.execute(select(Role).where(Role.id.in_(role_ids)))
    roles = result.scalars().all()
    return roles


@router.get("/", response_model=list[UserResponseSchema])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    role: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(User).options(selectinload(User.roles)).order_by(User.id)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.where(
            or_(
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
            )
        )

    if role:
        query = query.where(User.roles.any(func.lower(Role.name) == role.strip().lower()))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserResponseSchema)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await _get_user_or_404(db, user_id)


@router.post("/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreateSchema, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    roles = await _get_roles_or_400(db, payload.role_ids)

    user = User(
        email=payload.email,
        password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    user.roles = roles

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return await _get_user_or_404(db, user.id)


@router.patch("/{user_id}", response_model=UserResponseSchema)
async def update_user(
    user_id: int,
    payload: UserUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    user = await _get_user_or_404(db, user_id)

    if payload.password is not None:
        user.password = hash_password(payload.password)

    if payload.first_name is not None:
        user.first_name = payload.first_name

    if payload.last_name is not None:
        user.last_name = payload.last_name

    if payload.is_active is not None:
        user.is_active = payload.is_active

    if payload.role_ids is not None:
        roles = await _get_roles_or_400(db, payload.role_ids)
        user.roles = roles

    await db.commit()
    return await _get_user_or_404(db, user.id)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await _get_user_or_404(db, user_id)
    await db.delete(user)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
