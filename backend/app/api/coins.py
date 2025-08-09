"""
API для работы с коинами и транзакциями
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.schemas.coins import (
    CoinBalanceResponse, CoinTransactionsResponse, CoinAdjustment, CoinAdjustmentResponse
)
from app.services.coin_service import CoinService
from app.utils.permissions import get_current_user, require_parent, require_child_or_parent_of_child
from app.models import User

router = APIRouter()


@router.get("/balance", response_model=CoinBalanceResponse)
async def get_coin_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить баланс коинов текущего пользователя"""
    balance = await CoinService.get_user_balance(current_user.id, db)
    
    return CoinBalanceResponse(
        balance=balance.balance,
        total_earned=balance.total_earned,
        total_spent=balance.total_spent,
        updated_at=balance.updated_at
    )


@router.get("/transactions", response_model=CoinTransactionsResponse)
async def get_coin_transactions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    transaction_type: Optional[str] = Query(None, pattern="^(earned|spent|bonus|penalty)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить историю транзакций"""
    transactions, total_count, has_more = await CoinService.get_transactions(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        transaction_type=transaction_type,
        db=db
    )
    
    return CoinTransactionsResponse(
        transactions=transactions,
        total_count=total_count,
        has_more=has_more
    )


@router.post("/adjust", response_model=CoinAdjustmentResponse)
async def adjust_coins(
    adjustment: CoinAdjustment,
    current_user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_async_session)
):
    """Ручная корректировка баланса коинов (только для родителей)"""
    
    # Проверяем, что ребенок из той же семьи
    await require_child_or_parent_of_child(adjustment.child_id, current_user, db)
    
    transaction, new_balance = await CoinService.adjust_coins(adjustment, current_user.id, db)
    
    return CoinAdjustmentResponse(
        transaction=transaction,
        new_balance=new_balance
    )