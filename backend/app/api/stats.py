"""
API для статистики
"""
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.services.stats_service import StatsService
from app.utils.permissions import get_current_user, require_parent
from app.models import User

router = APIRouter()


@router.get("/family")
async def get_family_stats(
    period: str = Query("month", pattern="^(week|month)$"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_async_session)
):
    """Статистика по семье (родители)"""
    
    # Устанавливаем период, если не указан явно
    if not start_date or not end_date:
        if period == "week":
            end_date = date.today()
            start_date = end_date - timedelta(days=7)
        else:  # month
            end_date = date.today()
            start_date = end_date.replace(day=1)
    
    stats = await StatsService.get_family_stats(
        family_id=current_user.family_id,
        start_date=start_date,
        end_date=end_date,
        db=db
    )
    
    return stats


@router.get("/child")
async def get_child_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Статистика ребенка"""
    
    # Проверяем, что это ребенок или родитель может смотреть статистику своих детей
    if current_user.role == "child":
        child_id = current_user.id
    else:
        # Для родителей можно добавить параметр child_id в будущем
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Child access required or specify child_id parameter"
        )
    
    stats = await StatsService.get_child_stats(child_id, db)
    
    return stats