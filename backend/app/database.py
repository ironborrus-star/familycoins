"""
Конфигурация базы данных
"""
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# URL подключения к базе данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/familycoins")

# Настройки для продакшена
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Создаем асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=DEBUG)

# Создаем фабрику сессий
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Получить асинхронную сессию базы данных"""
    async with async_session_maker() as session:
        yield session


async def create_tables():
    """Создать все таблицы в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)