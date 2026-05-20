"""Dependencies for FastAPI."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db import get_db
from app.models.users import User
from app.utils import verify_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).options(selectinload(User.roles)).where(User.id == int(user_id)))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


async def check_admin_role(current_user: User = Depends(get_current_user)) -> User:
    """Check if user has admin role."""
    if not any(role.name == "admin" for role in current_user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",

            
        )
    return current_user


async def check_payment_role(current_user: User = Depends(get_current_user)) -> User:
    """Check if user has payment role."""
    if not any(role.name == "payment" for role in current_user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Payment role required",
        )
    return current_user


async def check_report_role(current_user: User = Depends(get_current_user)) -> User:
    """Check if user has report role."""
    if not any(role.name == "reports" for role in current_user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Report role required",
        )
    return current_user


async def check_admin_or_payment_role(current_user: User = Depends(get_current_user)) -> User:
    """Check if user has admin or payment role."""
    roles = {role.name for role in current_user.roles}
    if not ("admin" in roles or "payment" in roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Payment role required",
        )
    return current_user


async def check_admin_or_report_role(current_user: User = Depends(get_current_user)) -> User:
    """Check if user has admin or report role."""
    roles = {role.name for role in current_user.roles}
    if not ("admin" in roles or "reports" in roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Report role required",
        )
    return current_user
