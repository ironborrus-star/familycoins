"""
Сервис для работы с семейным магазином
"""
import uuid
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models import StoreItem, Purchase, User
from app.schemas.store import StoreItemCreate, PurchaseCreate
from app.services.coin_service import CoinService


class StoreService:
    
    @staticmethod
    async def get_store_items(family_id: uuid.UUID, db: AsyncSession) -> List[StoreItem]:
        """Получить товары в семейном магазине"""
        result = await db.execute(
            select(StoreItem).where(
                and_(
                    StoreItem.family_id == family_id,
                    StoreItem.is_available == True
                )
            )
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def create_store_item(
        item_data: StoreItemCreate,
        creator_id: uuid.UUID,
        family_id: uuid.UUID,
        db: AsyncSession
    ) -> StoreItem:
        """Добавить товар в магазин (только родители)"""
        
        item = StoreItem(
            family_id=family_id,
            name=item_data.name,
            description=item_data.description,
            category=item_data.category,
            price_coins=item_data.price_coins,
            created_by=creator_id
        )
        
        db.add(item)
        await db.commit()
        await db.refresh(item)
        
        return item
    
    @staticmethod
    async def purchase_item(
        purchase_data: PurchaseCreate,
        child_id: uuid.UUID,
        family_id: uuid.UUID,
        db: AsyncSession
    ) -> Tuple[Purchase, int]:
        """Купить товар (дети)"""
        
        # Получаем товар
        result = await db.execute(
            select(StoreItem).where(
                and_(
                    StoreItem.id == purchase_data.item_id,
                    StoreItem.family_id == family_id,
                    StoreItem.is_available == True
                )
            )
        )
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store item not found or not available"
            )
        
        # Проверяем баланс и списываем коины
        try:
            _, new_balance = await CoinService.spend_coins(
                user_id=child_id,
                amount=item.price_coins,
                description=f"Покупка: {item.name}",
                reference_id=item.id,
                reference_type="purchase",
                db=db
            )
        except HTTPException as e:
            # Переформатируем ошибку для соответствия API спецификации
            if "insufficient_coins" in str(e.detail):
                balance = await CoinService.get_user_balance(child_id, db)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "insufficient_coins",
                        "message": "Недостаточно коинов для покупки",
                        "required": item.price_coins,
                        "available": balance.balance
                    }
                )
            raise e
        
        # Создаем покупку
        purchase = Purchase(
            child_id=child_id,
            item_id=item.id,
            price_paid=item.price_coins
        )
        
        db.add(purchase)
        await db.commit()
        await db.refresh(purchase)
        
        return purchase, new_balance
    
    @staticmethod
    async def get_child_purchases(child_id: uuid.UUID, db: AsyncSession) -> List[Purchase]:
        """Получить покупки ребенка"""
        result = await db.execute(
            select(Purchase)
            .options(selectinload(Purchase.item))
            .where(Purchase.child_id == child_id)
            .order_by(Purchase.created_at.desc())
        )
        return list(result.scalars().all())