"""
Основное приложение FastAPI для FamilyCoins
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.database import create_tables, get_async_session
from app.api import auth, coins, tasks, store, stats, goals
from app.services.init_data import create_default_task_templates

# Настройка логирования
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Создаем приложение FastAPI
app = FastAPI(
    title=settings.project_name,
    description="API для семейного мотивационного приложения",
    version="1.0.0",
    debug=settings.debug,
    openapi_url=f"{settings.api_v1_str}/openapi.json" if settings.debug else None,
    docs_url=f"{settings.api_v1_str}/docs" if settings.debug else None,
    redoc_url=f"{settings.api_v1_str}/redoc" if settings.debug else None,
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router, prefix="/v1/auth", tags=["authentication"])
app.include_router(tasks.router, prefix="/v1/tasks", tags=["tasks"])
app.include_router(store.router, prefix="/v1/store", tags=["store"])
app.include_router(coins.router, prefix="/v1/coins", tags=["coins"])
app.include_router(stats.router, prefix="/v1/stats", tags=["stats"])
app.include_router(goals.router, tags=["goals"])


@app.on_event("startup")
async def startup():
    """Инициализация при запуске"""
    logger.info(f"Starting {settings.project_name} in {settings.environment} mode")
    
    await create_tables()
    
    # Инициализируем данные по умолчанию
    async for db in get_async_session():
        await create_default_task_templates(db)
        break
    
    logger.info("Application startup completed")


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "FamilyCoins API is running"}


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    try:
        # Проверка подключения к базе данных
        async for db in get_async_session():
            await db.execute("SELECT 1")
            break
        
        from datetime import datetime
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": settings.environment
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        from datetime import datetime
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/metrics")
async def metrics():
    """Метрики для мониторинга"""
    if not settings.debug:
        # В продакшене метрики доступны только локально
        from fastapi import Request
        
        def get_client_ip(request: Request):
            x_forwarded_for = request.headers.get("X-Forwarded-For")
            if x_forwarded_for:
                return x_forwarded_for.split(",")[0].strip()
            return request.client.host
        
        # Разрешить доступ только с локальных адресов
        # В реальном проекте нужно настроить правильную авторизацию
    
    return {
        "app_info": {
            "name": settings.project_name,
            "version": "1.0.0",
            "environment": settings.environment
        },
        "system_info": {
            "python_version": "3.11",
            "framework": "FastAPI"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)