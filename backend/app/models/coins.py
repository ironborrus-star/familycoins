"""
Модели для системы коинов и транзакций
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, CheckConstraint, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class CoinBalance(Base):
    __tablename__ = "coin_balances"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_earned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_spent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Ограничения
    __table_args__ = (
        UniqueConstraint("user_id", name="unique_user_balance"),
    )

    # Отношения
    user: Mapped["User"] = relationship("User", back_populates="coin_balance")


class CoinTransaction(Base):
    __tablename__ = "coin_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # положительное для заработка, отрицательное для трат
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))  # ID задания или покупки
    reference_type: Mapped[Optional[str]] = mapped_column(String(20))  # 'task', 'purchase', 'manual'
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Ограничения
    __table_args__ = (
        CheckConstraint("transaction_type IN ('earned', 'spent', 'bonus', 'penalty')", name="check_transaction_type"),
    )

    # Отношения
    user: Mapped["User"] = relationship("User", back_populates="coin_transactions")