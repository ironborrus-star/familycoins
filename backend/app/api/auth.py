"""
API для аутентификации и управления семьями
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.schemas.family import (
    FamilyCreate, FamilyJoin, FamilyCreateResponse, 
    AuthResponse, FamilyMembersResponse, UserLogin
)
from app.services.auth_service import AuthService
from app.utils.permissions import get_current_user
from app.models import User

router = APIRouter()


@router.post("/family/create", response_model=FamilyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_family(
    family_data: FamilyCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Создать новую семью"""
    try:
        family, parent, access_token, passcode = await AuthService.create_family(family_data, db)
        
        return FamilyCreateResponse(
            access_token=access_token,
            user=parent,
            family_id=family.id,
            passcode=passcode,
            parent=parent
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create family: {str(e)}"
        )


@router.post("/family/join", response_model=AuthResponse)
async def join_family(
    join_data: FamilyJoin,
    db: AsyncSession = Depends(get_async_session)
):
    """Присоединиться к семье"""
    user, access_token = await AuthService.join_family(join_data, db)
    
    return AuthResponse(
        access_token=access_token,
        user=user
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_async_session)
):
    """Авторизация пользователя по логину и паролю"""
    user, access_token = await AuthService.login_user(login_data, db)
    
    return AuthResponse(
        access_token=access_token,
        user=user
    )


@router.get("/family/members", response_model=FamilyMembersResponse)
async def get_family_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить членов семьи"""
    family, members = await AuthService.get_family_members(current_user.family_id, db)
    
    return FamilyMembersResponse(
        family=family,
        members=members
    )