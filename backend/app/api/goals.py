"""
API эндпоинты для работы с целями
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models import User
from app.schemas.goals import (
    GoalCreate, GoalCreateLegacy, GoalUpdate, StoreItemGoalCreate, GoalStatus,
    Goal, GoalWithDetails, GoalResponse, GoalCreateResponse,
    GoalsListResponse, GoalProgressUpdateResponse, FamilyGoalStatistics,
    GoalNotFoundError, GoalCompletionError, InvalidGoalConditionsError,
    ExecutorType, GoalType, HabitGoalData, StoreItemGoalData
)
from app.services.goal_service import GoalService
from app.utils.permissions import get_current_user

router = APIRouter(prefix="/v1/goals", tags=["goals"])


# Эндпоинты для поддержки пошаговой формы
@router.get(
    "/form-data/executors",
    response_model=dict
)
async def get_goal_executors_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Получить данные для первого шага формы - выбор исполнителей цели
    
    **Доступ:** Все члены семьи
    """
    # Проверяем, что пользователь имеет семью
    if not current_user.family_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a member of any family"
        )
    
    try:
        data = await GoalService.get_executors_data(current_user.family_id, current_user.id, db)
        return data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get executors data: {str(e)}"
        )


@router.get(
    "/form-data/goal-types",
    response_model=dict
)
async def get_goal_types_data():
    """
    Получить данные для второго шага формы - выбор типа цели
    """
    return {
        "goal_types": [
            {
                "type": "store_item",
                "name": "Товар из магазина",
                "description": "Цель накопления монет на конкретный товар",
                "icon": "fas fa-shopping-cart"
            },
            {
                "type": "habit_building", 
                "name": "Привычка",
                "description": "Выполнение определённого количества действий за период",
                "icon": "fas fa-calendar-check"
            },
            {
                "type": "coin_saving",
                "name": "Накопить монеты", 
                "description": "Простая цель накопления определённого количества монет",
                "icon": "fas fa-coins"
            },
            {
                "type": "mixed",
                "name": "Смешанная цель",
                "description": "Цель с несколькими условиями и весами",
                "icon": "fas fa-tasks"
            }
        ]
    }


@router.post(
    "/enhanced",
    response_model=GoalCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": InvalidGoalConditionsError},
        404: {"description": "Child or store item not found"}
    }
)
async def create_enhanced_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Создать новую цель с расширенным функционалом
    
    Поддерживает:
    - Выбор исполнителей (отдельные дети, группы, вся семья)
    - Цели-привычки с настройкой периодов и количества действий
    - Интеграцию с магазином
    - Различные типы наград
    
    **Доступ:** Родители и дети (дети могут создавать цели только для себя)
    """
    try:
        goal = await GoalService.create_enhanced_goal(
            goal_data=goal_data,
            creator_id=current_user.id,
            family_id=current_user.family_id,
            db=db
        )
        
        return GoalCreateResponse(goal=goal)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create enhanced goal: {str(e)}"
        )


@router.post(
    "/",
    response_model=GoalCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": InvalidGoalConditionsError},
        404: {"description": "Child or store item not found"}
    }
)
async def create_goal(
    goal_data: GoalCreateLegacy,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Создать новую цель
    
    **Доступ:** Родители и дети (дети могут создавать цели только для себя)
    """
    # Проверяем права: родители могут создавать цели для любого ребенка, 
    # дети только для себя
    if current_user.role == "child" and goal_data.child_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Children can only create goals for themselves"
        )
    
    try:
        goal = await GoalService.create_legacy_goal(
            goal_data=goal_data,
            creator_id=current_user.id,
            family_id=current_user.family_id,
            db=db
        )
        
        return GoalCreateResponse(goal=goal)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create goal: {str(e)}"
        )


@router.get(
    "/",
    response_model=GoalsListResponse
)
async def get_goals(
    status_filter: Optional[GoalStatus] = Query(None, description="Фильтр по статусу цели"),
    child_id: Optional[uuid.UUID] = Query(None, description="Фильтр по ребенку (только для родителей)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Получить список целей
    
    **Доступ:** Родители видят все цели семьи, дети только свои
    """
    if current_user.role == "child":
        # Дети видят только свои цели
        goals = await GoalService.get_child_goals(
            child_id=current_user.id,
            family_id=current_user.family_id,
            db=db,
            status_filter=status_filter
        )
    else:
        # Родители видят цели всей семьи
        goals = await GoalService.get_family_goals(
            family_id=current_user.family_id,
            db=db,
            status_filter=status_filter,
            child_id_filter=child_id
        )
    
    # Формируем детализированные данные
    goals_with_details = []
    for goal in goals:
        progress_summary = await GoalService.get_goal_progress_summary(goal)
        
        goal_details = GoalWithDetails(
            **goal.__dict__,
            conditions=[condition.__dict__ for condition in goal.conditions],
            progress=[progress.__dict__ for progress in goal.progress],
            child_name=goal.child.name,
            creator_name=goal.creator.name,
            target_store_item_name=goal.target_store_item.name if goal.target_store_item else None
        )
        goals_with_details.append(goal_details)
    
    return GoalsListResponse(
        goals=goals_with_details,
        total_count=len(goals_with_details)
    )


@router.get(
    "/{goal_id}",
    response_model=GoalResponse,
    responses={404: {"model": GoalNotFoundError}}
)
async def get_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Получить детали конкретной цели
    
    **Доступ:** Родители - любые цели семьи, дети - только свои цели
    """
    goal = await GoalService.get_goal_by_id(goal_id, current_user.family_id, db)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    # Проверяем права доступа
    if current_user.role == "child" and goal.child_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    progress_summary = await GoalService.get_goal_progress_summary(goal)
    
    goal_details = GoalWithDetails(
        **goal.__dict__,
        conditions=[condition.__dict__ for condition in goal.conditions],
        progress=[progress.__dict__ for progress in goal.progress],
        child_name=goal.child.name,
        creator_name=goal.creator.name,
        target_store_item_name=goal.target_store_item.name if goal.target_store_item else None
    )
    
    return GoalResponse(
        goal=goal_details,
        progress_summary=progress_summary
    )


@router.put(
    "/{goal_id}",
    response_model=Goal,
    responses={
        404: {"model": GoalNotFoundError},
        403: {"description": "Access denied"}
    }
)
async def update_goal(
    goal_id: uuid.UUID,
    goal_data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Обновить цель
    
    **Доступ:** Создатели цели и родители
    """
    goal = await GoalService.get_goal_by_id(goal_id, current_user.family_id, db)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    # Проверяем права: создатель цели или родитель
    if goal.created_by != current_user.id and current_user.role != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only goal creator or parents can update goals"
        )
    
    try:
        updated_goal = await GoalService.update_goal(goal_id, goal_data, current_user.family_id, db)
        return updated_goal
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update goal: {str(e)}"
        )


@router.post(
    "/{goal_id}/pause",
    response_model=Goal,
    responses={
        404: {"model": GoalNotFoundError},
        403: {"description": "Access denied"}
    }
)
async def pause_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Приостановить цель
    
    **Доступ:** Создатели цели и родители
    """
    goal = await GoalService.get_goal_by_id(goal_id, current_user.family_id, db)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    # Проверяем права
    if goal.created_by != current_user.id and current_user.role != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only goal creator or parents can pause goals"
        )
    
    return await GoalService.pause_goal(goal_id, current_user.family_id, db)


@router.post(
    "/{goal_id}/resume",
    response_model=Goal,
    responses={
        404: {"model": GoalNotFoundError},
        403: {"description": "Access denied"}
    }
)
async def resume_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Возобновить приостановленную цель
    
    **Доступ:** Создатели цели и родители
    """
    goal = await GoalService.get_goal_by_id(goal_id, current_user.family_id, db)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    # Проверяем права
    if goal.created_by != current_user.id and current_user.role != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only goal creator or parents can resume goals"
        )
    
    return await GoalService.resume_goal(goal_id, current_user.family_id, db)


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": GoalNotFoundError},
        403: {"description": "Access denied"}
    }
)
async def delete_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Удалить цель
    
    **Доступ:** Создатели цели и родители
    """
    goal = await GoalService.get_goal_by_id(goal_id, current_user.family_id, db)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    # Проверяем права
    if goal.created_by != current_user.id and current_user.role != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only goal creator or parents can delete goals"
        )
    
    await GoalService.delete_goal(goal_id, current_user.family_id, db)


@router.get(
    "/statistics/family",
    response_model=FamilyGoalStatistics
)
async def get_family_goal_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Получить статистику целей семьи
    
    **Доступ:** Все члены семьи
    """
    stats = await GoalService.get_family_goal_statistics(current_user.family_id, db)
    return FamilyGoalStatistics(**stats)


# Эндпоинты для интеграции с магазином
@router.post(
    "/store-item/{item_id}",
    response_model=GoalCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Store item not found"},
        400: {"model": InvalidGoalConditionsError}
    }
)
async def create_store_item_goal(
    item_id: uuid.UUID,
    goal_data: StoreItemGoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Создать цель "накопить на товар" из магазина
    
    **Доступ:** Родители и дети (дети могут создавать цели только для себя)
    """
    # Проверяем права
    if current_user.role == "child" and goal_data.child_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Children can only create goals for themselves"
        )
    
    try:
        goal = await GoalService.create_store_item_goal(
            item_id=item_id,
            goal_data=goal_data,
            creator_id=current_user.id,
            family_id=current_user.family_id,
            db=db
        )
        
        return GoalCreateResponse(goal=goal)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create store item goal: {str(e)}"
        )


# Внутренние эндпоинты для обновления прогресса (используются другими сервисами)
@router.post(
    "/_internal/update-progress/coins",
    response_model=GoalProgressUpdateResponse,
    include_in_schema=False  # Скрываем из OpenAPI документации
)
async def update_goal_progress_coins(
    user_id: uuid.UUID,
    coin_change: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Внутренний эндпоинт для обновления прогресса целей при изменении коинов
    
    Используется CoinService автоматически
    """
    updated_goals = await GoalService.update_goal_progress_on_coin_change(
        user_id=user_id,
        coin_change=coin_change,
        db=db
    )
    
    if updated_goals:
        # Возвращаем прогресс первой обновленной цели как пример
        goal = updated_goals[0]
        progress_list = [progress.__dict__ for progress in goal.progress]
        
        return GoalProgressUpdateResponse(
            goal_id=goal.id,
            updated_progress=progress_list,
            is_goal_completed=goal.status == "completed",
            message=f"Обновлен прогресс {len(updated_goals)} цели(ей)"
        )
    
    return GoalProgressUpdateResponse(
        goal_id=None,
        updated_progress=[],
        is_goal_completed=False,
        message="Нет целей для обновления"
    )


@router.post(
    "/_internal/update-progress/task",
    response_model=GoalProgressUpdateResponse,
    include_in_schema=False  # Скрываем из OpenAPI документации
)
async def update_goal_progress_task(
    child_id: uuid.UUID,
    task_assignment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Внутренний эндпоинт для обновления прогресса целей при выполнении задания
    
    Используется TaskService автоматически
    """
    updated_goals = await GoalService.update_goal_progress_on_task_completion(
        child_id=child_id,
        task_assignment_id=task_assignment_id,
        db=db
    )
    
    if updated_goals:
        # Возвращаем прогресс первой обновленной цели
        goal = updated_goals[0]
        progress_list = [progress.__dict__ for progress in goal.progress]
        
        return GoalProgressUpdateResponse(
            goal_id=goal.id,
            updated_progress=progress_list,
            is_goal_completed=goal.status == "completed",
            message=f"Обновлен прогресс {len(updated_goals)} цели(ей) после выполнения задания"
        )
    
    return GoalProgressUpdateResponse(
        goal_id=None,
        updated_progress=[],
        is_goal_completed=False,
        message="Нет целей для обновления"
    )
