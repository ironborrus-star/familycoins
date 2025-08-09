"""
Pydantic схемы для целей
"""
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class GoalType(str, Enum):
    COIN_SAVING = "coin_saving"
    STORE_ITEM = "store_item"
    HABIT_BUILDING = "habit_building"
    MIXED = "mixed"


class GoalStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class ConditionType(str, Enum):
    COIN_AMOUNT = "coin_amount"
    TASK_COMPLETION = "task_completion"
    HABIT_STREAK = "habit_streak"
    HABIT_ACTIONS = "habit_actions"  # Для привычек с количеством действий
    CUSTOM = "custom"


class ExecutorType(str, Enum):
    INDIVIDUAL = "individual"  # Конкретный член семьи
    MULTIPLE_CHILDREN = "multiple_children"  # Несколько детей
    ALL_CHILDREN = "all_children"  # Все дети
    ALL_PARENTS = "all_parents"  # Все родители
    WHOLE_FAMILY = "whole_family"  # Вся семья


class RewardType(str, Enum):
    COINS = "coins"
    BADGE = "badge"
    STORE_ITEM = "store_item"


class PeriodType(str, Enum):
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"


# Goal Condition schemas
class GoalConditionBase(BaseModel):
    condition_type: ConditionType
    target_value: int = Field(..., ge=1)
    target_reference_id: Optional[uuid.UUID] = None
    description: str = Field(..., max_length=255)
    weight: Decimal = Field(1.0, ge=0, le=1)
    is_streak_required: bool = False


class GoalConditionCreate(GoalConditionBase):
    pass


class GoalCondition(GoalConditionBase):
    id: uuid.UUID
    goal_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Goal Progress schemas
class GoalProgressBase(BaseModel):
    current_value: int = Field(0, ge=0)
    streak_count: int = Field(0, ge=0)
    last_activity_date: Optional[date] = None


class GoalProgress(GoalProgressBase):
    id: uuid.UUID
    goal_id: uuid.UUID
    condition_id: uuid.UUID
    updated_at: datetime

    class Config:
        from_attributes = True


# Goal Achievement schemas
class GoalAchievementBase(BaseModel):
    reward_coins_earned: int = Field(0, ge=0)
    notes: Optional[str] = None


class GoalAchievement(GoalAchievementBase):
    id: uuid.UUID
    goal_id: uuid.UUID
    child_id: uuid.UUID
    achieved_at: datetime

    class Config:
        from_attributes = True


# Goal schemas
class GoalBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    goal_type: GoalType
    target_store_item_id: Optional[uuid.UUID] = None
    deadline: Optional[date] = None
    reward_coins: int = Field(0, ge=0)


# Enhanced Goal Creation schemas
class GoalExecutor(BaseModel):
    """Схема для определения исполнителя цели"""
    executor_type: ExecutorType
    user_ids: Optional[List[uuid.UUID]] = None  # Конкретные пользователи для INDIVIDUAL и MULTIPLE_CHILDREN


class HabitGoalData(BaseModel):
    """Дополнительные данные для цели-привычки"""
    habit_name: str = Field(..., max_length=200)
    habit_description: Optional[str] = None
    actions_count: int = Field(..., ge=1)  # Количество действий
    period_value: int = Field(..., ge=1)   # Значение периода (например, 30)
    period_type: PeriodType = PeriodType.DAYS  # Тип периода
    reward_type: RewardType = RewardType.COINS
    reward_value: int = Field(..., ge=0)  # Размер награды
    reward_reference_id: Optional[uuid.UUID] = None  # ID товара или значка для награды
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_streak_required: bool = False  # Требуется выполнение подряд


class StoreItemGoalData(BaseModel):
    """Дополнительные данные для цели накопления на товар"""
    store_item_id: uuid.UUID
    store_item_name: str
    store_item_cost: int
    store_item_image_url: Optional[str] = None
    availability_deadline: Optional[date] = None


class GoalCreate(GoalBase):
    executor: GoalExecutor
    conditions: List[GoalConditionCreate] = Field(..., min_items=1)
    
    # Дополнительные данные в зависимости от типа цели
    habit_data: Optional[HabitGoalData] = None
    store_item_data: Optional[StoreItemGoalData] = None

    @validator('conditions')
    def validate_conditions_weights(cls, v, values):
        """Validate that weights sum to 1.0 for mixed goals"""
        if values.get('goal_type') == GoalType.MIXED:
            total_weight = sum(condition.weight for condition in v)
            if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
                raise ValueError("Total weight of conditions must equal 1.0 for mixed goals")
        return v
    
    @validator('habit_data')
    def validate_habit_data(cls, v, values):
        """Validate habit data for habit goals"""
        if values.get('goal_type') == GoalType.HABIT_BUILDING and not v:
            raise ValueError("habit_data is required for habit_building goals")
        return v
    
    @validator('store_item_data')
    def validate_store_item_data(cls, v, values):
        """Validate store item data for store item goals"""
        if values.get('goal_type') == GoalType.STORE_ITEM and not v:
            raise ValueError("store_item_data is required for store_item goals")
        return v


# Backward compatibility - старая схема создания цели
class GoalCreateLegacy(GoalBase):
    child_id: uuid.UUID
    conditions: List[GoalConditionCreate] = Field(..., min_items=1)

    @validator('conditions')
    def validate_conditions_weights(cls, v, values):
        """Validate that weights sum to 1.0 for mixed goals"""
        if values.get('goal_type') == GoalType.MIXED:
            total_weight = sum(condition.weight for condition in v)
            if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
                raise ValueError("Total weight of conditions must equal 1.0 for mixed goals")
        return v


class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[GoalStatus] = None
    deadline: Optional[date] = None
    reward_coins: Optional[int] = Field(None, ge=0)


class Goal(GoalBase):
    id: uuid.UUID
    family_id: uuid.UUID
    child_id: uuid.UUID
    status: GoalStatus
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GoalWithDetails(Goal):
    conditions: List[GoalCondition]
    progress: List[GoalProgress]
    child_name: str
    creator_name: str
    target_store_item_name: Optional[str] = None


class GoalProgressSummary(BaseModel):
    goal_id: uuid.UUID
    overall_progress_percentage: float = Field(..., ge=0, le=100)
    conditions_progress: List[dict]  # List of {condition_id, progress_percentage, current_value, target_value}
    is_completed: bool


# Store item goal creation
class StoreItemGoalCreate(BaseModel):
    title: Optional[str] = None  # Will default to "Накопить на {item_name}"
    description: Optional[str] = None
    child_id: uuid.UUID
    deadline: Optional[date] = None
    reward_coins: int = Field(0, ge=0)


# Response schemas
class GoalsListResponse(BaseModel):
    goals: List[GoalWithDetails]
    total_count: int


class GoalResponse(BaseModel):
    goal: GoalWithDetails
    progress_summary: GoalProgressSummary


class GoalCreateResponse(BaseModel):
    goal: Goal
    message: str = "Цель успешно создана"


class GoalProgressUpdateResponse(BaseModel):
    goal_id: uuid.UUID
    updated_progress: List[GoalProgress]
    is_goal_completed: bool
    message: Optional[str] = None


class GoalStatistics(BaseModel):
    total_goals: int
    active_goals: int
    completed_goals: int
    paused_goals: int
    cancelled_goals: int
    completion_rate: float = Field(..., ge=0, le=100)


class FamilyGoalStatistics(BaseModel):
    family_stats: GoalStatistics
    children_stats: List[dict]  # List of {child_id, child_name, stats: GoalStatistics}


# Error responses
class GoalNotFoundError(BaseModel):
    error: str = "goal_not_found"
    message: str = "Цель не найдена"


class GoalCompletionError(BaseModel):
    error: str = "goal_completion_error"
    message: str = "Не удается завершить цель"
    details: Optional[str] = None


class InvalidGoalConditionsError(BaseModel):
    error: str = "invalid_goal_conditions"
    message: str = "Некорректные условия цели"
    details: List[str]
