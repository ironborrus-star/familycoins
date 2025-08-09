"""
Модели для системы целей
"""
import uuid
from datetime import datetime, date
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, CheckConstraint, Boolean, Text, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id", ondelete="CASCADE"), nullable=False)
    
    # Поддержка разных типов исполнителей
    executor_type: Mapped[str] = mapped_column(String(20), nullable=False, default="individual")  # individual, multiple_children, etc.
    executor_data: Mapped[Optional[dict]] = mapped_column(JSON, default={})  # Дополнительные данные об исполнителях
    
    # Для обратной совместимости оставляем child_id
    child_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    goal_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_store_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("store_items.id"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    deadline: Mapped[Optional[date]] = mapped_column(Date)
    reward_coins: Mapped[int] = mapped_column(Integer, default=0)  # Бонусные коины за достижение цели
    
    # Дополнительные данные для разных типов целей
    goal_metadata: Mapped[Optional[dict]] = mapped_column(JSON, default={})  # Дополнительные данные (для привычек, товаров и т.д.)
    
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Ограничения
    __table_args__ = (
        CheckConstraint("goal_type IN ('coin_saving', 'store_item', 'habit_building', 'mixed')", name="check_goal_type"),
        CheckConstraint("status IN ('active', 'completed', 'paused', 'cancelled')", name="check_goal_status"),
        CheckConstraint("executor_type IN ('individual', 'multiple_children', 'all_children', 'all_parents', 'whole_family')", name="check_executor_type"),
    )

    # Отношения
    family: Mapped["Family"] = relationship("Family", back_populates="goals")
    child: Mapped["User"] = relationship("User", foreign_keys=[child_id], back_populates="goals")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by], back_populates="created_goals")
    target_store_item: Mapped[Optional["StoreItem"]] = relationship("StoreItem", back_populates="goals")
    conditions: Mapped[List["GoalCondition"]] = relationship("GoalCondition", back_populates="goal", cascade="all, delete-orphan")
    progress: Mapped[List["GoalProgress"]] = relationship("GoalProgress", back_populates="goal", cascade="all, delete-orphan")
    achievements: Mapped[List["GoalAchievement"]] = relationship("GoalAchievement", back_populates="goal", cascade="all, delete-orphan")


class GoalCondition(Base):
    __tablename__ = "goal_conditions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    condition_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_value: Mapped[int] = mapped_column(Integer, nullable=False)
    target_reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))  # ID задания или другой сущности
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=1.0)  # Вес условия для смешанных целей
    is_streak_required: Mapped[bool] = mapped_column(Boolean, default=False)  # Требуется выполнение подряд
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Ограничения
    __table_args__ = (
        CheckConstraint("condition_type IN ('coin_amount', 'task_completion', 'habit_streak', 'habit_actions', 'custom')", name="check_condition_type"),
        CheckConstraint("weight >= 0 AND weight <= 1", name="check_weight_range"),
    )

    # Отношения
    goal: Mapped["Goal"] = relationship("Goal", back_populates="conditions")
    progress: Mapped[List["GoalProgress"]] = relationship("GoalProgress", back_populates="condition", cascade="all, delete-orphan")


class GoalProgress(Base):
    __tablename__ = "goal_progress"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    condition_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("goal_conditions.id", ondelete="CASCADE"), nullable=False)
    current_value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    streak_count: Mapped[int] = mapped_column(Integer, default=0)  # Количество дней подряд для streak целей
    last_activity_date: Mapped[Optional[date]] = mapped_column(Date)  # Последняя дата активности для streak
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношения
    goal: Mapped["Goal"] = relationship("Goal", back_populates="progress")
    condition: Mapped["GoalCondition"] = relationship("GoalCondition", back_populates="progress")


class GoalAchievement(Base):
    __tablename__ = "goal_achievements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    child_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achieved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reward_coins_earned: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text)  # Заметки о достижении

    # Отношения
    goal: Mapped["Goal"] = relationship("Goal", back_populates="achievements")
    child: Mapped["User"] = relationship("User", back_populates="goal_achievements")
