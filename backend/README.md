# 🏆 FamilyCoins Backend

FastAPI приложение для системы мотивации детей через задачи и вознаграждения.

## 🚀 Быстрый старт

### Локальная разработка

```bash
# Перейти в папку backend
cd backend

# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.example .env
# Отредактируйте .env файл

# Запустить приложение
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Из корня проекта
docker build -t familycoins-backend -f backend/Dockerfile backend/

# Запуск
docker run -p 8000:8000 --env-file backend/.env familycoins-backend
```

## 🛠 Технологии

- **FastAPI** - современный Python веб-фреймворк
- **PostgreSQL** - надежная реляционная база данных
- **Redis** - кэширование и сессии
- **SQLAlchemy** - ORM для работы с БД
- **Alembic** - миграции базы данных
- **Pydantic** - валидация данных

## 📁 Структура

```
backend/
├── app/
│   ├── api/            # API роутеры
│   ├── models/         # SQLAlchemy модели
│   ├── schemas/        # Pydantic схемы
│   ├── services/       # Бизнес логика
│   └── utils/          # Утилиты
├── alembic/            # Миграции БД
├── tests/              # Тесты
├── Dockerfile          # Docker образ
├── requirements.txt    # Python зависимости
├── railway.toml        # Конфигурация Railway
└── .env.example        # Пример переменных окружения
```

## 📊 API

После запуска API документация доступна:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 Разработка

### Миграции базы данных

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "Description"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1
```

### Тестирование

```bash
# Запустить все тесты
pytest

# С покрытием
pytest --cov=app tests/

# Только определенный тест
pytest tests/test_auth.py
```

## 🚀 Развертывание

### Railway

1. Создайте проект в Railway
2. Подключите этот репозиторий
3. Railway автоматически обнаружит `railway.toml`
4. Добавьте PostgreSQL и Redis сервисы
5. Настройте переменные окружения из `.env.example`

Подробные инструкции: [docs/deployment/RAILWAY_DEPLOY.md](../docs/deployment/RAILWAY_DEPLOY.md)

## 🔐 Переменные окружения

Основные переменные (см. `.env.example`):

```env
# Приложение
ENVIRONMENT=development
DEBUG=true
PROJECT_NAME=FamilyCoins API

# База данных
DATABASE_URL=postgresql://user:pass@localhost:5432/familycoins
REDIS_URL=redis://localhost:6379

# Безопасность
JWT_SECRET_KEY=your-secret-key-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:8080"]
```

## 🤝 Участие в разработке

1. Создайте ветку для новой функции
2. Внесите изменения
3. Добавьте тесты
4. Убедитесь что все тесты проходят
5. Создайте Pull Request

## 📝 Лицензия

MIT License