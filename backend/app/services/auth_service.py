"""
Сервис для аутентификации и управления семьями
"""
import uuid
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models import Family, User, CoinBalance
from app.schemas.family import FamilyCreate, FamilyJoin, UserLogin
from app.utils.auth import generate_passcode, create_access_token, get_password_hash, verify_password


class AuthService:
    
    @staticmethod
    async def create_family(family_data: FamilyCreate, db: AsyncSession) -> Tuple[Family, User, str]:
        """Создать новую семью с родителем"""
        
        # Генерируем пасскод
        passcode = generate_passcode()
        
        # Создаем семью
        family = Family(
            name=family_data.name,
            passcode=passcode  # Сохраняем пасскод как есть, без хеширования
        )
        db.add(family)
        await db.flush()  # Получаем ID семьи
        
        # Создаем родителя
        parent = User(
            family_id=family.id,
            name=family_data.parent_name,
            username=family_data.parent_username,
            password_hash=get_password_hash(family_data.parent_password),
            role="parent"
        )
        db.add(parent)
        await db.flush()  # Получаем ID родителя
        
        # Создаем баланс коинов для родителя
        balance = CoinBalance(
            user_id=parent.id,
            balance=0,
            total_earned=0,
            total_spent=0
        )
        db.add(balance)
        
        await db.commit()
        await db.refresh(family)
        await db.refresh(parent)
        
        # Создаем токен
        access_token = create_access_token(data={"sub": str(parent.id)})
        
        return family, parent, access_token, passcode
    
    @staticmethod
    async def join_family(join_data: FamilyJoin, db: AsyncSession) -> Tuple[User, str]:
        """Присоединиться к существующей семье"""
        
        # Ищем семью по пасскоду (прямое сравнение)
        result = await db.execute(select(Family).where(Family.passcode == join_data.passcode))
        family = result.scalar_one_or_none()
        
        if not family:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family not found with this passcode"
            )
        
        # Проверяем, что пользователь с таким username не существует в семье
        result = await db.execute(
            select(User).where(User.username == join_data.username)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username already exists"
            )
        
        # Создаем нового пользователя
        user = User(
            family_id=family.id,
            name=join_data.user_name,
            username=join_data.username,
            password_hash=get_password_hash(join_data.password),
            role=join_data.role
        )
        db.add(user)
        await db.flush()
        
        # Создаем баланс коинов
        balance = CoinBalance(
            user_id=user.id,
            balance=0,
            total_earned=0,
            total_spent=0
        )
        db.add(balance)
        
        await db.commit()
        await db.refresh(user)
        
        # Создаем токен
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return user, access_token
    
    @staticmethod
    async def login_user(login_data: UserLogin, db: AsyncSession) -> Tuple[User, str]:
        """Авторизация пользователя по логину и паролю"""
        
        # Ищем пользователя по username
        result = await db.execute(select(User).where(User.username == login_data.username))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Проверяем пароль
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Создаем токен
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return user, access_token
    
    @staticmethod
    async def get_family_members(family_id: uuid.UUID, db: AsyncSession) -> Tuple[Family, list[User]]:
        """Получить семью и её членов"""
        
        # Получаем семью
        result = await db.execute(select(Family).where(Family.id == family_id))
        family = result.scalar_one_or_none()
        
        if not family:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family not found"
            )
        
        # Получаем членов семьи
        result = await db.execute(select(User).where(User.family_id == family_id))
        members = result.scalars().all()
        
        return family, list(members)