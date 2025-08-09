"""
Модели для заданий и их выполнения
"""
import uuid
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, CheckConstraint, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class TaskTemplate(Base):
    __tablename__ = "task_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    default_reward_coins: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    is_system_template: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Отношения
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="template")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id", ondelete="CASCADE"), nullable=False)
    template_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("task_templates.id"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    reward_coins: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Ограничения
    __table_args__ = (
        CheckConstraint("status IN ('active', 'paused', 'archived')", name="check_task_status"),
    )

    # Отношения
    family: Mapped["Family"] = relationship("Family", back_populates="tasks")
    template: Mapped[Optional["TaskTemplate"]] = relationship("TaskTemplate", back_populates="tasks")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by], back_populates="created_tasks")
    assignments: Mapped[List["TaskAssignment"]] = relationship("TaskAssignment", back_populates="task", cascade="all, delete-orphan")


class TaskAssignment(Base):
    __tablename__ = "task_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    child_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="assigned")
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    proof_text: Mapped[Optional[str]] = mapped_column(Text)
    proof_image_url: Mapped[Optional[str]] = mapped_column(String(255))
    coins_earned: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Ограничения
    __table_args__ = (
        CheckConstraint("status IN ('assigned', 'completed', 'approved', 'rejected')", name="check_assignment_status"),
    )

    # Отношения
    task: Mapped["Task"] = relationship("Task", back_populates="assignments")
    child: Mapped["User"] = relationship("User", foreign_keys=[child_id], back_populates="task_assignments")
    approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by], back_populates="approved_tasks")