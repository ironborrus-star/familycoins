"""
Утилиты для проверки прав доступа
"""
import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_async_session
from app.models import User
from app.utils.auth import verify_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_session)
) -> User:
    """Получить текущего пользователя из токена"""
    payload = verify_token(credentials.credentials)
    user_id: str = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Получаем пользователя из базы данных
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def require_parent(current_user: User = Depends(get_current_user)) -> User:
    """Требует, чтобы пользователь был родителем"""
    if current_user.role != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Parent access required"
        )
    return current_user


async def require_child(current_user: User = Depends(get_current_user)) -> User:
    """Требует, чтобы пользователь был ребенком"""
    if current_user.role != "child":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Child access required"
        )
    return current_user


async def require_family_member(
    family_id: uuid.UUID,
    current_user: User = Depends(get_current_user)
) -> User:
    """Требует, чтобы пользователь был членом указанной семьи"""
    if current_user.family_id != family_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: not a family member"
        )
    return current_user


async def require_child_or_parent_of_child(
    child_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> User:
    """Требует, чтобы пользователь был указанным ребенком или родителем в той же семье"""
    if current_user.id == child_id:
        # Пользователь - это сам ребенок
        return current_user
    
    if current_user.role == "parent":
        # Проверяем, что ребенок в той же семье
        result = await db.execute(select(User).where(User.id == child_id))
        child = result.scalar_one_or_none()
        
        if child and child.family_id == current_user.family_id:
            return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied: not authorized for this child"
    )