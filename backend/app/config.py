"""
Конфигурация приложения
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    environment: str = "development"
    debug: bool = True
    api_v1_str: str = "/v1"
    project_name: str = "FamilyCoins API"
    
    # База данных
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/familycoins"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # JWT
    jwt_secret_key: str = "your_secret_key_here_change_in_production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    backend_cors_origins: List[str] = ["*"]
    
    # Серверные настройки
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Логирование
    log_level: str = "INFO"
    
    @validator("backend_cors_origins", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Парсинг CORS origins"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @property
    def is_production(self) -> bool:
        """Проверка продакшен окружения"""
        return self.environment.lower() == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Маппинг переменных окружения
        fields = {
            "database_url": {"env": "DATABASE_URL"},
            "redis_url": {"env": "REDIS_URL"},
            "jwt_secret_key": {"env": "JWT_SECRET_KEY"},
            "jwt_algorithm": {"env": "JWT_ALGORITHM"},
            "access_token_expire_minutes": {"env": "ACCESS_TOKEN_EXPIRE_MINUTES"},
            "backend_cors_origins": {"env": "BACKEND_CORS_ORIGINS"},
            "log_level": {"env": "LOG_LEVEL"},
            "environment": {"env": "ENVIRONMENT"},
            "debug": {"env": "DEBUG"},
            "host": {"env": "HOST"},
            "port": {"env": "PORT"},
        }


# Глобальный экземпляр настроек
settings = Settings()
