"""
Сервис для работы с коинами и транзакциями
"""
import uuid
from typing import Tuple, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from fastapi import HTTPException, status

from app.models import CoinBalance, CoinTransaction, User
from app.schemas.coins import CoinAdjustment


class CoinService:
    
    @staticmethod
    async def get_user_balance(user_id: uuid.UUID, db: AsyncSession) -> CoinBalance:
        """Получить баланс пользователя"""
        result = await db.execute(
            select(CoinBalance).where(CoinBalance.user_id == user_id)
        )
        balance = result.scalar_one_or_none()
        
        if not balance:
            # Создаем баланс, если его нет
            balance = CoinBalance(
                user_id=user_id,
                balance=0,
                total_earned=0,
                total_spent=0
            )
            db.add(balance)
            await db.commit()
            await db.refresh(balance)
        
        return balance
    
    @staticmethod
    async def add_coins(
        user_id: uuid.UUID,
        amount: int,
        description: str,
        transaction_type: str = "earned",
        reference_id: Optional[uuid.UUID] = None,
        reference_type: Optional[str] = None,
        db: AsyncSession = None
    ) -> Tuple[CoinTransaction, int]:
        """Добавить коины пользователю"""
        
        # Получаем текущий баланс
        balance = await CoinService.get_user_balance(user_id, db)
        
        # Создаем транзакцию
        transaction = CoinTransaction(
            user_id=user_id,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            reference_id=reference_id,
            reference_type=reference_type
        )
        db.add(transaction)
        
        # Обновляем баланс
        balance.balance += amount
        balance.total_earned += amount
        
        await db.commit()
        await db.refresh(transaction)
        await db.refresh(balance)
        
        # Обновляем прогресс целей при изменении коинов
        try:
            from app.services.goal_service import GoalService
            await GoalService.update_goal_progress_on_coin_change(user_id, amount, db)
        except ImportError:
            # Игнорируем если модуль целей недоступен
            pass
        except Exception:
            # Не прерываем основную операцию при ошибке обновления целей
            pass
        
        return transaction, balance.balance
    
    @staticmethod
    async def spend_coins(
        user_id: uuid.UUID,
        amount: int,
        description: str,
        reference_id: Optional[uuid.UUID] = None,
        reference_type: Optional[str] = None,
        db: AsyncSession = None
    ) -> Tuple[CoinTransaction, int]:
        """Потратить коины пользователя"""
        
        # Получаем текущий баланс
        balance = await CoinService.get_user_balance(user_id, db)
        
        # Проверяем, достаточно ли коинов
        if balance.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "insufficient_coins",
                    "message": "Недостаточно коинов для операции",
                    "required": amount,
                    "available": balance.balance
                }
            )
        
        # Создаем транзакцию
        transaction = CoinTransaction(
            user_id=user_id,
            amount=-amount,  # Отрицательное значение для трат
            transaction_type="spent",
            description=description,
            reference_id=reference_id,
            reference_type=reference_type
        )
        db.add(transaction)
        
        # Обновляем баланс
        balance.balance -= amount
        balance.total_spent += amount
        
        await db.commit()
        await db.refresh(transaction)
        await db.refresh(balance)
        
        # Обновляем прогресс целей при изменении коинов
        try:
            from app.services.goal_service import GoalService
            await GoalService.update_goal_progress_on_coin_change(user_id, -amount, db)
        except ImportError:
            # Игнорируем если модуль целей недоступен
            pass
        except Exception:
            # Не прерываем основную операцию при ошибке обновления целей
            pass
        
        return transaction, balance.balance
    
    @staticmethod
    async def adjust_coins(
        adjustment: CoinAdjustment,
        adjusted_by: uuid.UUID,
        db: AsyncSession
    ) -> Tuple[CoinTransaction, int]:
        """Ручная корректировка баланса (только родители)"""
        
        # Проверяем, что ребенок существует
        result = await db.execute(select(User).where(User.id == adjustment.child_id))
        child = result.scalar_one_or_none()
        
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Child not found"
            )
        
        # Определяем тип транзакции
        if adjustment.amount > 0:
            transaction_type = "bonus"
            return await CoinService.add_coins(
                user_id=adjustment.child_id,
                amount=adjustment.amount,
                description=adjustment.reason,
                transaction_type=transaction_type,
                reference_type="manual",
                db=db
            )
        else:
            # Для отрицательных значений
            balance = await CoinService.get_user_balance(adjustment.child_id, db)
            
            transaction = CoinTransaction(
                user_id=adjustment.child_id,
                amount=adjustment.amount,  # Уже отрицательное
                transaction_type="penalty",
                description=adjustment.reason,
                reference_type="manual"
            )
            db.add(transaction)
            
            # Обновляем баланс (не допускаем отрицательного баланса)
            new_balance = max(0, balance.balance + adjustment.amount)
            spent_amount = balance.balance - new_balance
            
            balance.balance = new_balance
            if spent_amount > 0:
                balance.total_spent += spent_amount
            
            await db.commit()
            await db.refresh(transaction)
            await db.refresh(balance)
            
            return transaction, balance.balance
    
    @staticmethod
    async def get_transactions(
        user_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
        transaction_type: Optional[str] = None,
        db: AsyncSession = None
    ) -> Tuple[List[CoinTransaction], int, bool]:
        """Получить историю транзакций пользователя"""
        
        # Базовый запрос
        query = select(CoinTransaction).where(CoinTransaction.user_id == user_id)
        
        # Фильтр по типу транзакции
        if transaction_type:
            query = query.where(CoinTransaction.transaction_type == transaction_type)
        
        # Подсчет общего количества
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await db.scalar(count_query)
        
        # Получаем транзакции с пагинацией
        query = query.order_by(desc(CoinTransaction.created_at)).limit(limit).offset(offset)
        result = await db.execute(query)
        transactions = result.scalars().all()
        
        has_more = (offset + limit) < total_count
        
        return list(transactions), total_count, has_more