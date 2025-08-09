# FamilyCoins Backend

Бэкенд для семейного мотивационного приложения FamilyCoins.

## Описание

FamilyCoins - это API для мотивационного приложения, которое помогает родителям мотивировать детей выполнять задания через систему виртуальных коинов.

## Основные функции

- 👨‍👩‍👧‍👦 **Управление семьей**: создание семьи, присоединение участников
- 📋 **Система заданий**: создание, назначение и выполнение заданий
- 🪙 **Коин система**: заработок и трата виртуальных коинов
- 🛍️ **Семейный магазин**: покупка привилегий и наград
- 📊 **Статистика**: отслеживание прогресса и достижений

## Технологический стек

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL + Redis
- **ORM**: SQLAlchemy (async)
- **Authentication**: JWT токены
- **Deployment**: Docker + Docker Compose

## Быстрый старт

### Требования

- Python 3.11+
- Docker и Docker Compose
- PostgreSQL (если запуск без Docker)
- Redis (если запуск без Docker)

### Запуск с Docker

```bash
# Клонировать проект
cd backend

# Запустить все сервисы
docker-compose up -d

# API будет доступно по адресу http://localhost:8000
```

### Запуск для разработки

```bash
# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.example .env
# Отредактировать .env файл

# Запустить приложение
uvicorn app.main:app --reload

# API будет доступно по адресу http://localhost:8000
```

## API Документация

После запуска приложения документация API доступна по адресам:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Основные эндпоинты

### Аутентификация
- `POST /v1/auth/family/create` - Создать семью
- `POST /v1/auth/family/join` - Присоединиться к семье
- `GET /v1/auth/family/members` - Получить членов семьи

### Задания
- `GET /v1/tasks/templates` - Получить шаблоны заданий
- `POST /v1/tasks` - Создать задание (родители)
- `GET /v1/tasks/my` - Получить мои задания
- `PUT /v1/tasks/assignments/{id}/complete` - Отметить выполнение (дети)
- `PUT /v1/tasks/assignments/{id}/approve` - Одобрить выполнение (родители)

### Магазин
- `GET /v1/store/items` - Получить товары
- `POST /v1/store/items` - Добавить товар (родители)
- `POST /v1/store/purchase` - Купить товар (дети)

### Коины
- `GET /v1/coins/balance` - Получить баланс
- `GET /v1/coins/transactions` - История транзакций
- `POST /v1/coins/adjust` - Ручная корректировка (родители)

### Статистика
- `GET /v1/stats/family` - Статистика семьи (родители)
- `GET /v1/stats/child` - Статистика ребенка

## Переменные окружения

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/familycoins
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## Структура проекта

```
backend/
├── app/
│   ├── api/              # API endpoints
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   ├── services/         # Бизнес логика
│   ├── utils/            # Утилиты
│   ├── database.py       # Конфигурация БД
│   └── main.py           # FastAPI приложение
├── tests/                # Тесты
├── docker-compose.yml    # Docker конфигурация
├── Dockerfile           # Docker образ
├── requirements.txt     # Python зависимости
└── README.md           # Документация
```

## Схема базы данных

Основные таблицы:
- `families` - Семьи
- `users` - Пользователи (родители и дети)
- `task_templates` - Шаблоны заданий
- `tasks` - Задания
- `task_assignments` - Назначения заданий
- `store_items` - Товары в магазине
- `purchases` - Покупки
- `coin_balances` - Балансы коинов
- `coin_transactions` - Транзакции коинов

## Примеры использования

### Создание семьи

```bash
curl -X POST "http://localhost:8000/v1/auth/family/create" \
     -H "Content-Type: application/json" \
     -d '{
       "family_name": "Семья Ивановых",
       "parent_name": "Анна Иванова"
     }'
```

### Присоединение к семье

```bash
curl -X POST "http://localhost:8000/v1/auth/family/join" \
     -H "Content-Type: application/json" \
     -d '{
       "passcode": "123456",
       "user_name": "Петя Иванов",
       "role": "child"
     }'
```

## Разработка

### Тестирование

```bash
# Запуск тестов
pytest

# Тестирование с покрытием
pytest --cov=app
```

### Миграции базы данных

```bash
# Создать миграцию
alembic revision --autogenerate -m "Description"

# Применить миграции
alembic upgrade head
```

## Лицензия

MIT License



Учетные данные для тестирования:
Администратор:
Логин: admin
Пароль: 123456
Ребенок:
Логин: daughter
Пароль: child123