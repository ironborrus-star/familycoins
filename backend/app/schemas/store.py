"""
Pydantic схемы для магазина
"""
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class StoreItemBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category: str = Field(..., max_length=50)
    price_coins: int = Field(..., ge=1)


class StoreItemCreate(StoreItemBase):
    pass


class StoreItemUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    price_coins: Optional[int] = Field(None, ge=1)
    is_available: Optional[bool] = None


class StoreItem(StoreItemBase):
    id: uuid.UUID
    family_id: uuid.UUID
    is_available: bool
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PurchaseCreate(BaseModel):
    item_id: uuid.UUID


class Purchase(BaseModel):
    id: uuid.UUID
    child_id: uuid.UUID
    item_id: uuid.UUID
    price_paid: int
    status: str
    used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseWithItem(Purchase):
    item_name: str


class StoreItemsResponse(BaseModel):
    items: List[StoreItem]


class PurchaseResponse(BaseModel):
    purchase: PurchaseWithItem
    new_balance: int


class InsufficientCoinsError(BaseModel):
    error: str = "insufficient_coins"
    message: str = "Недостаточно коинов для покупки"
    required: int
    available: int