"""
Pydantic схемы для коинов и транзакций
"""
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CoinBalance(BaseModel):
    balance: int
    total_earned: int
    total_spent: int
    updated_at: datetime

    class Config:
        from_attributes = True


class CoinTransactionBase(BaseModel):
    amount: int
    transaction_type: str = Field(..., pattern="^(earned|spent|bonus|penalty)$")
    description: str = Field(..., max_length=255)
    reference_type: Optional[str] = Field(None, pattern="^(task|purchase|manual)$")


class CoinTransaction(CoinTransactionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    reference_id: Optional[uuid.UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class CoinAdjustment(BaseModel):
    child_id: uuid.UUID
    amount: int = Field(..., description="Положительное для добавления, отрицательное для списания")
    reason: str = Field(..., max_length=255)


class CoinTransactionsResponse(BaseModel):
    transactions: List[CoinTransaction]
    total_count: int
    has_more: bool


class CoinAdjustmentResponse(BaseModel):
    transaction: CoinTransaction
    new_balance: int


class CoinBalanceResponse(BaseModel):
    balance: int
    total_earned: int
    total_spent: int
    updated_at: datetime