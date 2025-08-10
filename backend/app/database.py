"""
Конфигурация базы данных
"""
import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# URL подключения к базе данных
raw_database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/familycoins")

# ВСЕГДА используем asyncpg для Railway совместимости
if raw_database_url.startswith("postgresql://"):
    # Принудительно заменяем на asyncpg
    DATABASE_URL = raw_database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    logger.info(f"Converted DATABASE_URL for asyncpg: postgresql+asyncpg://...")
elif raw_database_url.startswith("postgres://"):
    # Railway иногда использует postgres:// вместо postgresql://
    DATABASE_URL = raw_database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    logger.info(f"Converted postgres:// to asyncpg: postgresql+asyncpg://...")
else:
    DATABASE_URL = raw_database_url
    logger.info(f"Using DATABASE_URL as is: {DATABASE_URL[:30]}...")

# Настройки для продакшена
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Принудительная проверка URL перед созданием движка
if not DATABASE_URL.startswith("postgresql+asyncpg://"):
    raise ValueError(f"DATABASE_URL должен использовать asyncpg драйвер. Получен: {DATABASE_URL[:50]}...")

logger.info(f"Creating engine with URL: {DATABASE_URL[:50]}...")

# Создаем асинхронный движок с принудительным указанием asyncpg
engine = create_async_engine(
    DATABASE_URL, 
    echo=DEBUG,
    future=True,
    pool_pre_ping=True
)

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