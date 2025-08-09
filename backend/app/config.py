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
    def assemble_cors_origins(cls, v):
        """Парсинг CORS origins"""
        if v is None:
            return ["*"]
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                # Попытка парсинга JSON-like строки
                import json
                try:
                    return json.loads(v)
                except:
                    pass
            # Парсинг как список через запятую
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["*"]
    
    @property
    def is_production(self) -> bool:
        """Проверка продакшен окружения"""
        return self.environment.lower() == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Глобальный экземпляр настроек
settings = Settings()
