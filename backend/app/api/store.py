"""
API для семейного магазина
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.schemas.store import (
    StoreItemsResponse, StoreItemCreate, StoreItem,
    PurchaseCreate, PurchaseResponse
)
from app.schemas.goals import StoreItemGoalCreate, GoalCreateResponse
from app.services.store_service import StoreService
from app.utils.permissions import get_current_user, require_parent, require_child
from app.models import User

router = APIRouter()


@router.get("/items", response_model=StoreItemsResponse)
async def get_store_items(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить товары в семейном магазине"""
    items = await StoreService.get_store_items(current_user.family_id, db)
    
    return StoreItemsResponse(items=items)


@router.post("/items", response_model=StoreItem, status_code=status.HTTP_201_CREATED)
async def create_store_item(
    item_data: StoreItemCreate,
    current_user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_async_session)
):
    """Добавить товар в магазин (родители)"""
    item = await StoreService.create_store_item(
        item_data=item_data,
        creator_id=current_user.id,
        family_id=current_user.family_id,
        db=db
    )
    
    return item


@router.post("/purchase", response_model=PurchaseResponse)
async def purchase_item(
    purchase_data: PurchaseCreate,
    current_user: User = Depends(require_child),
    db: AsyncSession = Depends(get_async_session)
):
    """Купить товар (дети)"""
    try:
        purchase, new_balance = await StoreService.purchase_item(
            purchase_data=purchase_data,
            child_id=current_user.id,
            family_id=current_user.family_id,
            db=db
        )
        
        # Получаем название товара для ответа
        from sqlalchemy import select
        from app.models import StoreItem
        
        result = await db.execute(select(StoreItem).where(StoreItem.id == purchase.item_id))
        item = result.scalar_one()
        
        purchase_with_item = {
            "id": purchase.id,
            "child_id": purchase.child_id,
            "item_id": purchase.item_id,
            "price_paid": purchase.price_paid,
            "status": purchase.status,
            "used_at": purchase.used_at,
            "expires_at": purchase.expires_at,
            "created_at": purchase.created_at,
            "item_name": item.name
        }
        
        return PurchaseResponse(
            purchase=purchase_with_item,
            new_balance=new_balance
        )
        
    except HTTPException as e:
        # Проверяем, если это ошибка недостатка коинов
        if hasattr(e, 'detail') and isinstance(e.detail, dict) and e.detail.get('error') == 'insufficient_coins':
            raise e
        raise e


@router.post("/items/{item_id}/create-goal", response_model=GoalCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_goal_for_store_item(
    item_id: str,
    goal_data: StoreItemGoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Создать цель "накопить на товар"
    
    **Доступ:** Родители и дети (дети могут создавать цели только для себя)
    """
    # Проверяем права: родители могут создавать цели для любого ребенка, дети только для себя
    if current_user.role == "child" and goal_data.child_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Children can only create goals for themselves"
        )
    
    try:
        from app.services.goal_service import GoalService
        import uuid
        
        goal = await GoalService.create_store_item_goal(
            item_id=uuid.UUID(item_id),
            goal_data=goal_data,
            creator_id=current_user.id,
            family_id=current_user.family_id,
            db=db
        )
        
        return GoalCreateResponse(goal=goal)
        
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Goals service not available"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create goal for store item: {str(e)}"
        )