"""
Модели для семей и пользователей
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, JSON, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Family(Base):
    __tablename__ = "families"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    passcode: Mapped[str] = mapped_column(String(255), nullable=False)
    settings: Mapped[Optional[dict]] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношения
    members: Mapped[List["User"]] = relationship("User", back_populates="family", cascade="all, delete-orphan")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="family", cascade="all, delete-orphan")
    store_items: Mapped[List["StoreItem"]] = relationship("StoreItem", back_populates="family", cascade="all, delete-orphan")
    goals: Mapped[List["Goal"]] = relationship("Goal", back_populates="family", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Ограничения
    __table_args__ = (
        CheckConstraint("role IN ('parent', 'child')", name="check_user_role"),
    )

    # Отношения
    family: Mapped["Family"] = relationship("Family", back_populates="members")
    created_tasks: Mapped[List["Task"]] = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    task_assignments: Mapped[List["TaskAssignment"]] = relationship("TaskAssignment", foreign_keys="TaskAssignment.child_id", back_populates="child")
    approved_tasks: Mapped[List["TaskAssignment"]] = relationship("TaskAssignment", foreign_keys="TaskAssignment.approved_by", back_populates="approver")
    created_store_items: Mapped[List["StoreItem"]] = relationship("StoreItem", back_populates="creator")
    purchases: Mapped[List["Purchase"]] = relationship("Purchase", back_populates="child")
    coin_balance: Mapped[Optional["CoinBalance"]] = relationship("CoinBalance", back_populates="user", uselist=False)
    coin_transactions: Mapped[List["CoinTransaction"]] = relationship("CoinTransaction", back_populates="user")
    goals: Mapped[List["Goal"]] = relationship("Goal", foreign_keys="Goal.child_id", back_populates="child")
    created_goals: Mapped[List["Goal"]] = relationship("Goal", foreign_keys="Goal.created_by", back_populates="creator")
    goal_achievements: Mapped[List["GoalAchievement"]] = relationship("GoalAchievement", back_populates="child")