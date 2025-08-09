"""
Сервис для работы с целями
"""
import uuid
from datetime import datetime, date, timedelta
from typing import List, Tuple, Optional, Dict
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException, status

from app.models import Goal, GoalCondition, GoalProgress, GoalAchievement, User, StoreItem, CoinBalance, TaskAssignment
from app.schemas.goals import (
    GoalCreate, GoalCreateLegacy, GoalUpdate, StoreItemGoalCreate, GoalType, GoalStatus, 
    ConditionType, GoalProgressSummary, GoalStatistics, ExecutorType, HabitGoalData, StoreItemGoalData
)
from app.services.coin_service import CoinService


class GoalService:
    
    @staticmethod
    async def get_executors_data(
        family_id: uuid.UUID,
        current_user_id: uuid.UUID,
        db: AsyncSession
    ) -> Dict:
        """Получить данные об исполнителях для первого шага формы"""
        
        # Получаем всех членов семьи
        result = await db.execute(
            select(User).where(User.family_id == family_id)
        )
        family_members = result.scalars().all()
        
        # Разделяем на родителей и детей
        parents = [m for m in family_members if m.role == "parent"]
        children = [m for m in family_members if m.role == "child"]
        current_user = next((m for m in family_members if m.id == current_user_id), None)
        
        executors = []
        
        # Если текущий пользователь - родитель, показываем все варианты
        if current_user and current_user.role == "parent":
            # Отдельные дети
            for child in children:
                executors.append({
                    "type": "individual",
                    "id": str(child.id),
                    "name": child.name,
                    "username": child.username,
                    "role": "child",
                    "avatar_letter": child.name[0].upper() if child.name else "?",
                    "description": f"Цель для {child.name}"
                })
            
            # Отдельные родители (включая себя)
            for parent in parents:
                executors.append({
                    "type": "individual", 
                    "id": str(parent.id),
                    "name": parent.name,
                    "username": parent.username,
                    "role": "parent",
                    "avatar_letter": parent.name[0].upper() if parent.name else "?",
                    "description": f"Цель для {parent.name}"
                })
            
            # Групповые варианты
            if len(children) > 1:
                executors.append({
                    "type": "all_children",
                    "id": "all_children",
                    "name": "Все дети",
                    "description": f"Общая цель для {len(children)} детей",
                    "icon": "fas fa-users",
                    "members": [{"name": c.name, "id": str(c.id)} for c in children]
                })
            
            if len(parents) > 1:
                executors.append({
                    "type": "all_parents",
                    "id": "all_parents", 
                    "name": "Все родители",
                    "description": f"Общая цель для {len(parents)} родителей",
                    "icon": "fas fa-user-friends",
                    "members": [{"name": p.name, "id": str(p.id)} for p in parents]
                })
            
            executors.append({
                "type": "whole_family",
                "id": "whole_family",
                "name": "Вся семья",
                "description": f"Общая цель для всей семьи ({len(family_members)} человек)",
                "icon": "fas fa-home",
                "members": [{"name": m.name, "id": str(m.id), "role": m.role} for m in family_members]
            })
        
        # Если текущий пользователь - ребенок, может создавать цели только для себя
        elif current_user and current_user.role == "child":
            executors.append({
                "type": "individual",
                "id": str(current_user.id),
                "name": current_user.name,
                "username": current_user.username,
                "role": "child",
                "avatar_letter": current_user.name[0].upper() if current_user.name else "?",
                "description": "Моя личная цель"
            })
        
        return {
            "executors": executors,
            "current_user": {
                "id": str(current_user.id),
                "name": current_user.name,
                "role": current_user.role
            } if current_user else None
        }
    
    @staticmethod
    async def create_enhanced_goal(
        goal_data: GoalCreate,
        creator_id: uuid.UUID,
        family_id: uuid.UUID,
        db: AsyncSession
    ) -> Goal:
        """Создать цель с расширенным функционалом"""
        
        # Валидируем исполнителей
        executor_ids = await GoalService._validate_and_get_executor_ids(
            goal_data.executor, family_id, creator_id, db
        )
        
        # Валидируем данные цели в зависимости от типа
        await GoalService._validate_goal_type_data(goal_data, family_id, db)
        
        # Создаем базовую цель
        goal_metadata = {}
        
        if goal_data.habit_data:
            goal_metadata["habit"] = goal_data.habit_data.dict()
        if goal_data.store_item_data:
            goal_metadata["store_item"] = goal_data.store_item_data.dict()
        
        # Для обратной совместимости устанавливаем child_id для индивидуальных целей
        child_id = None
        if goal_data.executor.executor_type == ExecutorType.INDIVIDUAL and len(executor_ids) == 1:
            # Проверяем, что это ребенок
            result = await db.execute(
                select(User).where(
                    and_(User.id == executor_ids[0], User.role == "child")
                )
            )
            child = result.scalar_one_or_none()
            if child:
                child_id = child.id
        
        goal = Goal(
            family_id=family_id,
            child_id=child_id,  # Для обратной совместимости
            executor_type=goal_data.executor.executor_type.value,
            executor_data={"user_ids": [str(uid) for uid in executor_ids]},
            title=goal_data.title,
            description=goal_data.description,
            goal_type=goal_data.goal_type.value,
            target_store_item_id=goal_data.target_store_item_id,
            deadline=goal_data.deadline,
            reward_coins=goal_data.reward_coins,
            goal_metadata=goal_metadata,
            created_by=creator_id
        )
        
        db.add(goal)
        await db.flush()
        
        # Создаем условия цели
        for condition_data in goal_data.conditions:
            condition = GoalCondition(
                goal_id=goal.id,
                condition_type=condition_data.condition_type.value,
                target_value=condition_data.target_value,
                target_reference_id=condition_data.target_reference_id,
                description=condition_data.description,
                weight=condition_data.weight,
                is_streak_required=condition_data.is_streak_required
            )
            db.add(condition)
            
            # Создаем прогресс для каждого условия и каждого исполнителя
            for executor_id in executor_ids:
                progress = GoalProgress(
                    goal_id=goal.id,
                    condition_id=condition.id,
                    current_value=0
                )
                db.add(progress)
        
        await db.commit()
        await db.refresh(goal)
        
        return goal
    
    @staticmethod
    async def _validate_and_get_executor_ids(
        executor_data,
        family_id: uuid.UUID,
        creator_id: uuid.UUID,
        db: AsyncSession
    ) -> List[uuid.UUID]:
        """Валидировать исполнителей и получить их ID"""
        
        # Получаем всех членов семьи
        result = await db.execute(
            select(User).where(User.family_id == family_id)
        )
        family_members = result.scalars().all()
        member_ids = {m.id: m for m in family_members}
        
        if executor_data.executor_type == ExecutorType.INDIVIDUAL:
            if not executor_data.user_ids or len(executor_data.user_ids) != 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Individual executor requires exactly one user_id"
                )
            
            user_id = executor_data.user_ids[0]
            if user_id not in member_ids:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Selected user not found in family"
                )
            
            # Проверяем права: дети могут создавать цели только для себя
            creator = member_ids[creator_id]
            if creator.role == "child" and user_id != creator_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Children can only create goals for themselves"
                )
            
            return [user_id]
        
        elif executor_data.executor_type == ExecutorType.MULTIPLE_CHILDREN:
            if not executor_data.user_ids or len(executor_data.user_ids) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Multiple children executor requires at least 2 user_ids"
                )
            
            children_ids = []
            for user_id in executor_data.user_ids:
                if user_id not in member_ids:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"User {user_id} not found in family"
                    )
                if member_ids[user_id].role != "child":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"User {user_id} is not a child"
                    )
                children_ids.append(user_id)
            
            return children_ids
        
        elif executor_data.executor_type == ExecutorType.ALL_CHILDREN:
            children = [m for m in family_members if m.role == "child"]
            if not children:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No children found in family"
                )
            return [c.id for c in children]
        
        elif executor_data.executor_type == ExecutorType.ALL_PARENTS:
            parents = [m for m in family_members if m.role == "parent"]
            if not parents:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No parents found in family"
                )
            return [p.id for p in parents]
        
        elif executor_data.executor_type == ExecutorType.WHOLE_FAMILY:
            return [m.id for m in family_members]
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported executor type: {executor_data.executor_type}"
            )
    
    @staticmethod
    async def _validate_goal_type_data(
        goal_data: GoalCreate,
        family_id: uuid.UUID,
        db: AsyncSession
    ):
        """Валидировать данные в зависимости от типа цели"""
        
        if goal_data.goal_type == GoalType.STORE_ITEM:
            if not goal_data.store_item_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="store_item_data is required for store_item goals"
                )
            
            # Проверяем, что товар существует и доступен
            result = await db.execute(
                select(StoreItem).where(
                    and_(
                        StoreItem.id == goal_data.store_item_data.store_item_id,
                        StoreItem.family_id == family_id,
                        StoreItem.is_available == True
                    )
                )
            )
            store_item = result.scalar_one_or_none()
            if not store_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Store item not found or not available"
                )
        
        elif goal_data.goal_type == GoalType.HABIT_BUILDING:
            if not goal_data.habit_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="habit_data is required for habit_building goals"
                )
            
            # Валидируем данные привычки
            habit_data = goal_data.habit_data
            if habit_data.actions_count <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="actions_count must be positive"
                )
            
            if habit_data.period_value <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="period_value must be positive"
                )
            
            # Если указана награда-товар, проверяем его
            if habit_data.reward_type == "store_item" and habit_data.reward_reference_id:
                result = await db.execute(
                    select(StoreItem).where(
                        and_(
                            StoreItem.id == habit_data.reward_reference_id,
                            StoreItem.family_id == family_id,
                            StoreItem.is_available == True
                        )
                    )
                )
                reward_item = result.scalar_one_or_none()
                if not reward_item:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Reward store item not found or not available"
                    )
    
    @staticmethod
    async def create_legacy_goal(
        goal_data: GoalCreateLegacy,
        creator_id: uuid.UUID,
        family_id: uuid.UUID,
        db: AsyncSession
    ) -> Goal:
        """Создать новую цель"""
        
        # Проверяем, что ребенок принадлежит к семье
        result = await db.execute(
            select(User).where(
                and_(
                    User.id == goal_data.child_id,
                    User.family_id == family_id,
                    User.role == "child"
                )
            )
        )
        child = result.scalar_one_or_none()
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Child not found in family"
            )
        
        # Проверяем target_store_item если указан
        if goal_data.target_store_item_id:
            result = await db.execute(
                select(StoreItem).where(
                    and_(
                        StoreItem.id == goal_data.target_store_item_id,
                        StoreItem.family_id == family_id,
                        StoreItem.is_available == True
                    )
                )
            )
            store_item = result.scalar_one_or_none()
            if not store_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Store item not found or not available"
                )
        
        # Валидируем условия цели
        await GoalService._validate_goal_conditions(goal_data, family_id, db)
        
        # Создаем цель (legacy format - один исполнитель)
        goal = Goal(
            family_id=family_id,
            child_id=goal_data.child_id,
            executor_type="individual",  # Для обратной совместимости
            executor_data={"user_ids": [str(goal_data.child_id)]},
            title=goal_data.title,
            description=goal_data.description,
            goal_type=goal_data.goal_type.value if hasattr(goal_data.goal_type, 'value') else goal_data.goal_type,
            target_store_item_id=goal_data.target_store_item_id,
            deadline=goal_data.deadline,
            reward_coins=goal_data.reward_coins,
            goal_metadata={},  # Пустые метаданные для legacy целей
            created_by=creator_id
        )
        
        db.add(goal)
        await db.flush()  # Получаем ID цели
        
        # Создаем условия цели
        for condition_data in goal_data.conditions:
            condition = GoalCondition(
                goal_id=goal.id,
                condition_type=condition_data.condition_type.value if hasattr(condition_data.condition_type, 'value') else condition_data.condition_type,
                target_value=condition_data.target_value,
                target_reference_id=condition_data.target_reference_id,
                description=condition_data.description,
                weight=condition_data.weight,
                is_streak_required=condition_data.is_streak_required
            )
            db.add(condition)
            
            # Создаем прогресс для каждого условия
            progress = GoalProgress(
                goal_id=goal.id,
                condition_id=condition.id,
                current_value=0,
                streak_count=0
            )
            db.add(progress)
        
        await db.commit()
        await db.refresh(goal)
        
        # Инициализируем прогресс для существующих данных
        await GoalService._initialize_goal_progress(goal.id, db)
        
        return goal
    
    @staticmethod
    async def create_store_item_goal(
        item_id: uuid.UUID,
        goal_data: StoreItemGoalCreate,
        creator_id: uuid.UUID,
        family_id: uuid.UUID,
        db: AsyncSession
    ) -> Goal:
        """Создать цель накопить на товар из магазина"""
        
        # Получаем товар
        result = await db.execute(
            select(StoreItem).where(
                and_(
                    StoreItem.id == item_id,
                    StoreItem.family_id == family_id,
                    StoreItem.is_available == True
                )
            )
        )
        store_item = result.scalar_one_or_none()
        if not store_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store item not found or not available"
            )
        
        # Создаем данные для цели
        title = goal_data.title or f"Накопить на {store_item.name}"
        description = goal_data.description or f"Накопить {store_item.price_coins} коинов на покупку '{store_item.name}'"
        
        goal_create_data = GoalCreate(
            title=title,
            description=description,
            goal_type=GoalType.STORE_ITEM,
            target_store_item_id=item_id,
            child_id=goal_data.child_id,
            deadline=goal_data.deadline,
            reward_coins=goal_data.reward_coins,
            conditions=[{
                "condition_type": ConditionType.COIN_AMOUNT,
                "target_value": store_item.price_coins,
                "description": f"Накопить {store_item.price_coins} коинов",
                "weight": Decimal("1.0"),
                "is_streak_required": False
            }]
        )
        
        return await GoalService.create_goal(goal_create_data, creator_id, family_id, db)
    
    @staticmethod
    async def get_child_goals(
        child_id: uuid.UUID,
        family_id: uuid.UUID,
        db: AsyncSession,
        status_filter: Optional[GoalStatus] = None
    ) -> List[Goal]:
        """Получить цели ребенка"""
        
        query = select(Goal).options(
            selectinload(Goal.conditions),
            selectinload(Goal.progress),
            joinedload(Goal.child),
            joinedload(Goal.creator),
            joinedload(Goal.target_store_item)
        ).where(
            and_(
                Goal.child_id == child_id,
                Goal.family_id == family_id
            )
        )
        
        if status_filter:
            query = query.where(Goal.status == status_filter)
        
        query = query.order_by(Goal.created_at.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_family_goals(
        family_id: uuid.UUID,
        db: AsyncSession,
        status_filter: Optional[GoalStatus] = None,
        child_id_filter: Optional[uuid.UUID] = None
    ) -> List[Goal]:
        """Получить цели семьи"""
        
        query = select(Goal).options(
            selectinload(Goal.conditions),
            selectinload(Goal.progress),
            joinedload(Goal.child),
            joinedload(Goal.creator),
            joinedload(Goal.target_store_item)
        ).where(Goal.family_id == family_id)
        
        if status_filter:
            query = query.where(Goal.status == status_filter)
        
        if child_id_filter:
            query = query.where(Goal.child_id == child_id_filter)
        
        query = query.order_by(Goal.created_at.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_goal_by_id(
        goal_id: uuid.UUID,
        family_id: uuid.UUID,
        db: AsyncSession
    ) -> Optional[Goal]:
        """Получить цель по ID"""
        
        result = await db.execute(
            select(Goal).options(
                selectinload(Goal.conditions),
                selectinload(Goal.progress),
                joinedload(Goal.child),
                joinedload(Goal.creator),
                joinedload(Goal.target_store_item)
            ).where(
                and_(
                    Goal.id == goal_id,
                    Goal.family_id == family_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_goal(
        goal_id: uuid.UUID,
        goal_data: GoalUpdate,
        family_id: uuid.UUID,
        db: AsyncSession
    ) -> Goal:
        """Обновить цель"""
        
        goal = await GoalService.get_goal_by_id(goal_id, family_id, db)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        # Обновляем поля
        update_data = goal_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)
        
        goal.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(goal)
        
        return goal
    
    @staticmethod
    async def pause_goal(goal_id: uuid.UUID, family_id: uuid.UUID, db: AsyncSession) -> Goal:
        """Приостановить цель"""
        return await GoalService.update_goal(
            goal_id, 
            GoalUpdate(status=GoalStatus.PAUSED), 
            family_id, 
            db
        )
    
    @staticmethod
    async def resume_goal(goal_id: uuid.UUID, family_id: uuid.UUID, db: AsyncSession) -> Goal:
        """Возобновить цель"""
        return await GoalService.update_goal(
            goal_id, 
            GoalUpdate(status=GoalStatus.ACTIVE), 
            family_id, 
            db
        )
    
    @staticmethod
    async def cancel_goal(goal_id: uuid.UUID, family_id: uuid.UUID, db: AsyncSession) -> Goal:
        """Отменить цель"""
        return await GoalService.update_goal(
            goal_id, 
            GoalUpdate(status=GoalStatus.CANCELLED), 
            family_id, 
            db
        )
    
    @staticmethod
    async def delete_goal(goal_id: uuid.UUID, family_id: uuid.UUID, db: AsyncSession) -> bool:
        """Удалить цель"""
        
        goal = await GoalService.get_goal_by_id(goal_id, family_id, db)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        await db.delete(goal)
        await db.commit()
        
        return True
    
    @staticmethod
    async def update_goal_progress_on_coin_change(
        user_id: uuid.UUID,
        coin_change: int,
        db: AsyncSession
    ) -> List[Goal]:
        """Обновить прогресс целей при изменении коинов"""
        
        # Получаем активные цели пользователя с условиями накопления коинов
        result = await db.execute(
            select(Goal).options(
                selectinload(Goal.conditions),
                selectinload(Goal.progress)
            ).where(
                and_(
                    Goal.child_id == user_id,
                    Goal.status == GoalStatus.ACTIVE
                )
            )
        )
        goals = list(result.scalars().all())
        
        updated_goals = []
        
        for goal in goals:
            coin_conditions = [c for c in goal.conditions if c.condition_type == ConditionType.COIN_AMOUNT]
            
            if coin_conditions:
                # Получаем текущий баланс
                balance = await CoinService.get_user_balance(user_id, db)
                
                for condition in coin_conditions:
                    # Находим прогресс для этого условия
                    progress = next((p for p in goal.progress if p.condition_id == condition.id), None)
                    if progress:
                        progress.current_value = balance.balance
                        progress.updated_at = datetime.utcnow()
                
                # Проверяем завершение цели
                if await GoalService._check_goal_completion(goal, db):
                    await GoalService._complete_goal(goal, db)
                    updated_goals.append(goal)
        
        await db.commit()
        return updated_goals
    
    @staticmethod
    async def update_goal_progress_on_task_completion(
        child_id: uuid.UUID,
        task_assignment_id: uuid.UUID,
        db: AsyncSession
    ) -> List[Goal]:
        """Обновить прогресс целей при выполнении задания"""
        
        # Получаем назначение задания
        result = await db.execute(
            select(TaskAssignment).options(
                joinedload(TaskAssignment.task)
            ).where(TaskAssignment.id == task_assignment_id)
        )
        assignment = result.scalar_one_or_none()
        
        if not assignment or assignment.status != "approved":
            return []
        
        # Получаем активные цели с условиями выполнения заданий
        result = await db.execute(
            select(Goal).options(
                selectinload(Goal.conditions),
                selectinload(Goal.progress)
            ).where(
                and_(
                    Goal.child_id == child_id,
                    Goal.status == GoalStatus.ACTIVE
                )
            )
        )
        goals = list(result.scalars().all())
        
        updated_goals = []
        today = date.today()
        
        for goal in goals:
            task_conditions = [c for c in goal.conditions 
                             if c.condition_type in [ConditionType.TASK_COMPLETION, ConditionType.HABIT_STREAK]]
            
            for condition in task_conditions:
                # Проверяем, относится ли условие к этому заданию
                if (condition.target_reference_id and 
                    condition.target_reference_id != assignment.task_id):
                    continue
                
                progress = next((p for p in goal.progress if p.condition_id == condition.id), None)
                if not progress:
                    continue
                
                if condition.condition_type == ConditionType.TASK_COMPLETION:
                    progress.current_value += 1
                    progress.updated_at = datetime.utcnow()
                    
                elif condition.condition_type == ConditionType.HABIT_STREAK and condition.is_streak_required:
                    # Проверяем streak
                    if progress.last_activity_date == today - timedelta(days=1):
                        # Продолжаем streak
                        progress.streak_count += 1
                    elif progress.last_activity_date != today:
                        # Начинаем новый streak
                        progress.streak_count = 1
                    
                    progress.current_value = progress.streak_count
                    progress.last_activity_date = today
                    progress.updated_at = datetime.utcnow()
            
            # Проверяем завершение цели
            if await GoalService._check_goal_completion(goal, db):
                await GoalService._complete_goal(goal, db)
                updated_goals.append(goal)
        
        await db.commit()
        return updated_goals
    
    @staticmethod
    async def get_goal_progress_summary(goal: Goal) -> GoalProgressSummary:
        """Получить сводку прогресса по цели"""
        
        conditions_progress = []
        total_progress = 0.0
        
        for condition in goal.conditions:
            progress = next((p for p in goal.progress if p.condition_id == condition.id), None)
            
            if progress:
                progress_percentage = min(100.0, (progress.current_value / condition.target_value) * 100)
            else:
                progress_percentage = 0.0
            
            conditions_progress.append({
                "condition_id": str(condition.id),
                "progress_percentage": progress_percentage,
                "current_value": progress.current_value if progress else 0,
                "target_value": condition.target_value,
                "description": condition.description
            })
            
            # Взвешенный прогресс для общего прогресса
            total_progress += progress_percentage * float(condition.weight)
        
        return GoalProgressSummary(
            goal_id=goal.id,
            overall_progress_percentage=min(100.0, total_progress),
            conditions_progress=conditions_progress,
            is_completed=goal.status == GoalStatus.COMPLETED
        )
    
    @staticmethod
    async def get_family_goal_statistics(family_id: uuid.UUID, db: AsyncSession) -> Dict:
        """Получить статистику целей семьи"""
        
        # Общая статистика семьи
        result = await db.execute(
            select(
                Goal.status,
                func.count(Goal.id).label('count')
            ).where(Goal.family_id == family_id)
            .group_by(Goal.status)
        )
        status_counts = {row.status: row.count for row in result}
        
        total_goals = sum(status_counts.values())
        completion_rate = (status_counts.get('completed', 0) / total_goals * 100) if total_goals > 0 else 0
        
        family_stats = GoalStatistics(
            total_goals=total_goals,
            active_goals=status_counts.get('active', 0),
            completed_goals=status_counts.get('completed', 0),
            paused_goals=status_counts.get('paused', 0),
            cancelled_goals=status_counts.get('cancelled', 0),
            completion_rate=completion_rate
        )
        
        # Статистика по детям
        result = await db.execute(
            select(User).where(
                and_(
                    User.family_id == family_id,
                    User.role == "child"
                )
            )
        )
        children = list(result.scalars().all())
        
        children_stats = []
        for child in children:
            result = await db.execute(
                select(
                    Goal.status,
                    func.count(Goal.id).label('count')
                ).where(
                    and_(
                        Goal.family_id == family_id,
                        Goal.child_id == child.id
                    )
                ).group_by(Goal.status)
            )
            child_status_counts = {row.status: row.count for row in result}
            
            child_total = sum(child_status_counts.values())
            child_completion_rate = (child_status_counts.get('completed', 0) / child_total * 100) if child_total > 0 else 0
            
            child_stats = GoalStatistics(
                total_goals=child_total,
                active_goals=child_status_counts.get('active', 0),
                completed_goals=child_status_counts.get('completed', 0),
                paused_goals=child_status_counts.get('paused', 0),
                cancelled_goals=child_status_counts.get('cancelled', 0),
                completion_rate=child_completion_rate
            )
            
            children_stats.append({
                "child_id": str(child.id),
                "child_name": child.name,
                "stats": child_stats
            })
        
        return {
            "family_stats": family_stats,
            "children_stats": children_stats
        }
    
    # Private helper methods
    
    @staticmethod
    async def _validate_goal_conditions(goal_data: GoalCreate, family_id: uuid.UUID, db: AsyncSession):
        """Валидировать условия цели"""
        
        if not goal_data.conditions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Goal must have at least one condition"
            )
        
        # Проверяем сумму весов для смешанных целей
        if goal_data.goal_type == GoalType.MIXED:
            total_weight = sum(condition.weight for condition in goal_data.conditions)
            if abs(total_weight - 1.0) > 0.01:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Total weight of conditions must equal 1.0 for mixed goals"
                )
        
        # Валидируем каждое условие
        for condition in goal_data.conditions:
            if condition.target_reference_id:
                # Проверяем существование referenced объекта
                if condition.condition_type in [ConditionType.TASK_COMPLETION, ConditionType.HABIT_STREAK]:
                    # Проверяем существование задания в семье
                    from app.models import Task
                    result = await db.execute(
                        select(Task).where(
                            and_(
                                Task.id == condition.target_reference_id,
                                Task.family_id == family_id
                            )
                        )
                    )
                    if not result.scalar_one_or_none():
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Referenced task not found: {condition.target_reference_id}"
                        )
    
    @staticmethod
    async def _initialize_goal_progress(goal_id: uuid.UUID, db: AsyncSession):
        """Инициализировать прогресс цели на основе существующих данных"""
        
        goal = await GoalService.get_goal_by_id(goal_id, None, db)  # family_id не нужен здесь
        if not goal:
            return
        
        for condition in goal.conditions:
            progress = next((p for p in goal.progress if p.condition_id == condition.id), None)
            if not progress:
                continue
            
            if condition.condition_type == ConditionType.COIN_AMOUNT:
                # Инициализируем прогресс накопления коинов
                balance = await CoinService.get_user_balance(goal.child_id, db)
                progress.current_value = balance.balance
        
        await db.commit()
    
    @staticmethod
    async def _check_goal_completion(goal: Goal, db: AsyncSession) -> bool:
        """Проверить завершение цели"""
        
        if goal.goal_type == GoalType.MIXED:
            # Для смешанных целей проверяем взвешенный прогресс
            total_progress = 0.0
            for condition in goal.conditions:
                progress = next((p for p in goal.progress if p.condition_id == condition.id), None)
                if progress:
                    condition_progress = min(1.0, progress.current_value / condition.target_value)
                    total_progress += condition_progress * float(condition.weight)
            
            return total_progress >= 1.0
        else:
            # Для обычных целей все условия должны быть выполнены
            for condition in goal.conditions:
                progress = next((p for p in goal.progress if p.condition_id == condition.id), None)
                if not progress or progress.current_value < condition.target_value:
                    return False
            return True
    
    @staticmethod
    async def _complete_goal(goal: Goal, db: AsyncSession):
        """Завершить цель и начислить награду"""
        
        goal.status = GoalStatus.COMPLETED
        goal.completed_at = datetime.utcnow()
        
        # Начисляем бонусные коины, если указаны
        if goal.reward_coins > 0:
            await CoinService.add_coins(
                user_id=goal.child_id,
                amount=goal.reward_coins,
                description=f"Награда за достижение цели: {goal.title}",
                reference_id=goal.id,
                reference_type="goal",
                db=db
            )
        
        # Создаем запись о достижении
        achievement = GoalAchievement(
            goal_id=goal.id,
            child_id=goal.child_id,
            reward_coins_earned=goal.reward_coins,
            notes=f"Цель '{goal.title}' успешно достигнута"
        )
        
        db.add(achievement)
