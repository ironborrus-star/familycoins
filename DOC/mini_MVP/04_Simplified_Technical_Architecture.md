# Упрощенная техническая архитектура
## Техническое описание минимального MVP FamilyCoins

---

### 🎯 Архитектурный обзор

**Принципы упрощенной архитектуры:**
- **Монолитный backend** - FastAPI для быстрой разработки
- **Простая база данных** - PostgreSQL + Redis для кеширования
- **Локальная аутентификация** - без OAuth, простые токены
- **Минимальные интеграции** - только push-уведомления
- **Single-region deployment** - без распределенной архитектуры

---

## 🏗️ Упрощенная архитектура системы

```mermaid
graph TB
    subgraph "Client Layer"
        A1[Mobile App<br/>React Native/Flutter]
    end
    
    subgraph "API Layer"
        B1[FastAPI Backend<br/>Монолитное приложение]
    end
    
    subgraph "Data Layer"
        C1[PostgreSQL<br/>Primary Database]
        C2[Redis<br/>Cache & Sessions]
    end
    
    subgraph "External Services"
        D1[Push Notifications<br/>FCM/APNS]
    end
    
    A1 --> B1
    B1 --> C1
    B1 --> C2
    B1 --> D1
```

---

## 📊 Модели данных

### Схема базы данных PostgreSQL

```sql
-- Семьи
CREATE TABLE families (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    passcode VARCHAR(6) NOT NULL, -- простой код доступа вместо авторизации
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Пользователи (родители и дети)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(10) NOT NULL CHECK (role IN ('parent', 'child')),
    avatar_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Шаблоны заданий
CREATE TABLE task_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(50) NOT NULL, -- 'household', 'screen_time', 'activity'
    title VARCHAR(200) NOT NULL,
    description TEXT,
    default_reward_coins INTEGER NOT NULL DEFAULT 10,
    is_system_template BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Задания для семьи
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    template_id UUID REFERENCES task_templates(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    reward_coins INTEGER NOT NULL DEFAULT 10,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'archived')),
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Назначения заданий детям
CREATE TABLE task_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    child_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'assigned' CHECK (status IN ('assigned', 'completed', 'approved', 'rejected')),
    due_date DATE,
    completed_at TIMESTAMP,
    approved_at TIMESTAMP,
    approved_by UUID REFERENCES users(id),
    proof_text TEXT,
    proof_image_url VARCHAR(255),
    coins_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Товары в семейном магазине
CREATE TABLE store_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL, -- 'screen_privileges', 'family_activities', 'material_rewards'
    price_coins INTEGER NOT NULL,
    is_available BOOLEAN DEFAULT true,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Покупки
CREATE TABLE purchases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_id UUID NOT NULL REFERENCES store_items(id),
    price_paid INTEGER NOT NULL, -- цена на момент покупки
    status VARCHAR(20) DEFAULT 'purchased' CHECK (status IN ('purchased', 'used', 'expired')),
    used_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Баланс коинов
CREATE TABLE coin_balances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    balance INTEGER NOT NULL DEFAULT 0,
    total_earned INTEGER NOT NULL DEFAULT 0,
    total_spent INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Транзакции коинов
CREATE TABLE coin_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL, -- положительное для заработка, отрицательное для трат
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('earned', 'spent', 'bonus', 'penalty')),
    description VARCHAR(255) NOT NULL,
    reference_id UUID, -- ID задания или покупки
    reference_type VARCHAR(20), -- 'task', 'purchase', 'manual'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Индексы для производительности
CREATE INDEX idx_users_family_id ON users(family_id);
CREATE INDEX idx_tasks_family_id ON tasks(family_id);
CREATE INDEX idx_task_assignments_child_id ON task_assignments(child_id);
CREATE INDEX idx_task_assignments_status ON task_assignments(status);
CREATE INDEX idx_store_items_family_id ON store_items(family_id);
CREATE INDEX idx_purchases_child_id ON purchases(child_id);
CREATE INDEX idx_coin_transactions_user_id ON coin_transactions(user_id);
CREATE INDEX idx_coin_transactions_created_at ON coin_transactions(created_at DESC);
```

---

## 🔗 REST API Спецификация

### Базовый URL и аутентификация

```
Base URL: https://api.familycoins.app/v1
Authentication: Bearer token (простой JWT)
Content-Type: application/json
```

### 1. Семья и пользователи

#### POST /auth/family/create
Создание новой семьи
```json
// Request
{
  "family_name": "Семья Ивановых",
  "parent_name": "Анна Иванова"
}

// Response 201
{
  "family_id": "uuid",
  "passcode": "123456",
  "access_token": "jwt_token",
  "parent": {
    "id": "uuid",
    "name": "Анна Иванова",
    "role": "parent"
  }
}
```

#### POST /auth/family/join
Присоединение к семье
```json
// Request
{
  "passcode": "123456",
  "user_name": "Петя Иванов",
  "role": "child"
}

// Response 200
{
  "access_token": "jwt_token",
  "user": {
    "id": "uuid",
    "name": "Петя Иванов",
    "role": "child",
    "family_id": "uuid"
  }
}
```

#### GET /family/members
Получить членов семьи
```json
// Response 200
{
  "family": {
    "id": "uuid",
    "name": "Семья Ивановых"
  },
  "members": [
    {
      "id": "uuid",
      "name": "Анна Иванова",
      "role": "parent",
      "avatar_url": null
    },
    {
      "id": "uuid", 
      "name": "Петя Иванов",
      "role": "child",
      "avatar_url": null
    }
  ]
}
```

### 2. Задания

#### GET /tasks/templates
Получить шаблоны заданий
```json
// Response 200
{
  "templates": [
    {
      "id": "uuid",
      "category": "household",
      "title": "Убрать комнату",
      "description": "Навести порядок в своей комнате",
      "default_reward_coins": 10
    },
    {
      "id": "uuid",
      "category": "screen_time",
      "title": "Соблюдать экранное время",
      "description": "Не превышать лимит использования устройства",
      "default_reward_coins": 15
    }
  ]
}
```

#### POST /tasks
Создать задание (только родители)
```json
// Request
{
  "template_id": "uuid", // опционально
  "title": "Убрать комнату",
  "description": "Навести порядок в своей комнате",
  "category": "household",
  "reward_coins": 15,
  "assigned_to": ["child_id_1", "child_id_2"], // список детей
  "due_date": "2024-01-15"
}

// Response 201
{
  "task": {
    "id": "uuid",
    "title": "Убрать комнату",
    "description": "Навести порядок в своей комнате",
    "category": "household", 
    "reward_coins": 15,
    "status": "active",
    "created_at": "2024-01-10T10:00:00Z"
  },
  "assignments": [
    {
      "id": "uuid",
      "child_id": "uuid",
      "child_name": "Петя Иванов",
      "status": "assigned",
      "due_date": "2024-01-15"
    }
  ]
}
```

#### GET /tasks/my
Получить задания текущего пользователя
```json
// Response 200 (для ребенка)
{
  "assignments": [
    {
      "id": "uuid",
      "task": {
        "id": "uuid",
        "title": "Убрать комнату",
        "description": "Навести порядок в своей комнате",
        "category": "household",
        "reward_coins": 15
      },
      "status": "assigned",
      "due_date": "2024-01-15",
      "created_at": "2024-01-10T10:00:00Z"
    }
  ]
}

// Response 200 (для родителя)
{
  "created_tasks": [
    {
      "id": "uuid",
      "title": "Убрать комнату",
      "category": "household",
      "reward_coins": 15,
      "assignments_count": 2,
      "completed_count": 1
    }
  ],
  "pending_approvals": [
    {
      "assignment_id": "uuid",
      "task_title": "Убрать комнату",
      "child_name": "Петя Иванов",
      "completed_at": "2024-01-12T15:00:00Z",
      "proof_text": "Все убрал!",
      "proof_image_url": "https://..."
    }
  ]
}
```

#### PUT /tasks/assignments/{assignment_id}/complete
Отметить задание как выполненное (дети)
```json
// Request
{
  "proof_text": "Все убрал, комната чистая!",
  "proof_image_url": "https://storage.../image.jpg" // опционально
}

// Response 200
{
  "assignment": {
    "id": "uuid",
    "status": "completed",
    "completed_at": "2024-01-12T15:00:00Z",
    "proof_text": "Все убрал, комната чистая!"
  }
}
```

#### PUT /tasks/assignments/{assignment_id}/approve
Одобрить выполнение задания (родители)
```json
// Request
{
  "approved": true, // true = одобрить, false = отклонить
  "feedback": "Отлично выполнено!" // опционально
}

// Response 200
{
  "assignment": {
    "id": "uuid",
    "status": "approved",
    "approved_at": "2024-01-12T18:00:00Z",
    "coins_earned": 15
  },
  "new_balance": 125 // новый баланс ребенка
}
```

### 3. Магазин

#### GET /store/items
Получить товары в семейном магазине
```json
// Response 200
{
  "items": [
    {
      "id": "uuid",
      "name": "Дополнительные 30 минут экранного времени",
      "description": "Можно добавить к дневному лимиту",
      "category": "screen_privileges",
      "price_coins": 20,
      "is_available": true
    },
    {
      "id": "uuid", 
      "name": "Выбор фильма на вечер",
      "description": "Выбрать что смотреть всей семьей",
      "category": "family_activities",
      "price_coins": 15,
      "is_available": true
    }
  ]
}
```

#### POST /store/items
Добавить товар в магазин (родители)
```json
// Request
{
  "name": "Любимое мороженое",
  "description": "Купить любимое мороженое",
  "category": "material_rewards",
  "price_coins": 25
}

// Response 201
{
  "item": {
    "id": "uuid",
    "name": "Любимое мороженое",
    "description": "Купить любимое мороженое", 
    "category": "material_rewards",
    "price_coins": 25,
    "is_available": true,
    "created_at": "2024-01-10T10:00:00Z"
  }
}
```

#### POST /store/purchase
Купить товар (дети)
```json
// Request
{
  "item_id": "uuid"
}

// Response 200
{
  "purchase": {
    "id": "uuid",
    "item_name": "Дополнительные 30 минут экранного времени",
    "price_paid": 20,
    "status": "purchased",
    "created_at": "2024-01-12T16:00:00Z"
  },
  "new_balance": 105
}

// Response 400 (недостаточно коинов)
{
  "error": "insufficient_coins",
  "message": "Недостаточно коинов для покупки",
  "required": 20,
  "available": 15
}
```

### 4. Баланс и транзакции

#### GET /coins/balance
Получить баланс коинов
```json
// Response 200
{
  "balance": 125,
  "total_earned": 200,
  "total_spent": 75,
  "updated_at": "2024-01-12T18:00:00Z"
}
```

#### GET /coins/transactions
Получить историю транзакций
```json
// Query params: ?limit=20&offset=0&type=earned|spent

// Response 200
{
  "transactions": [
    {
      "id": "uuid",
      "amount": 15,
      "transaction_type": "earned",
      "description": "Выполнение задания: Убрать комнату",
      "reference_type": "task",
      "created_at": "2024-01-12T18:00:00Z"
    },
    {
      "id": "uuid",
      "amount": -20,
      "transaction_type": "spent", 
      "description": "Покупка: Дополнительные 30 минут экранного времени",
      "reference_type": "purchase",
      "created_at": "2024-01-12T16:00:00Z"
    }
  ],
  "total_count": 25,
  "has_more": true
}
```

#### POST /coins/adjust
Ручная корректировка баланса (только родители)
```json
// Request
{
  "child_id": "uuid",
  "amount": 10, // положительное для добавления, отрицательное для списания
  "reason": "Бонус за хорошее поведение"
}

// Response 200
{
  "transaction": {
    "id": "uuid",
    "amount": 10,
    "transaction_type": "bonus",
    "description": "Бонус за хорошее поведение"
  },
  "new_balance": 135
}
```

### 5. Статистика

#### GET /stats/family
Статистика по семье (родители)
```json
// Query params: ?period=week|month&start_date=2024-01-01&end_date=2024-01-31

// Response 200
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "summary": {
    "total_tasks_assigned": 45,
    "total_tasks_completed": 38,
    "completion_rate": 84.4,
    "total_coins_earned": 570,
    "total_coins_spent": 320,
    "active_children": 2
  },
  "children_stats": [
    {
      "child_id": "uuid",
      "child_name": "Петя Иванов",
      "tasks_completed": 20,
      "coins_earned": 300,
      "coins_spent": 150,
      "completion_rate": 87.0
    }
  ],
  "daily_activity": [
    {
      "date": "2024-01-01",
      "tasks_completed": 3,
      "coins_earned": 45
    }
  ]
}
```

#### GET /stats/child
Статистика ребенка
```json
// Response 200
{
  "current_month": {
    "tasks_completed": 12,
    "coins_earned": 180,
    "coins_spent": 95,
    "completion_rate": 92.3
  },
  "achievements": [
    {
      "title": "Первое задание",
      "description": "Выполнил первое задание",
      "earned_at": "2024-01-01T10:00:00Z"
    },
    {
      "title": "Неделя без пропусков",
      "description": "Выполнял задания каждый день недели",
      "earned_at": "2024-01-08T20:00:00Z"
    }
  ]
}
```

---

## 🔧 Техническая реализация

### Backend Stack (Python)

```python
# requirements.txt
fastapi==0.104.0
uvicorn==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
redis==5.0.1
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.6
pydantic==2.4.0
alembic==1.12.1
```

### Структура проекта

```
backend/
├── app/
│   ├── main.py              # FastAPI приложение
│   ├── database.py          # Подключение к БД
│   ├── models/              # SQLAlchemy модели
│   │   ├── family.py
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── store.py
│   │   └── coins.py
│   ├── schemas/             # Pydantic схемы
│   │   ├── family.py
│   │   ├── task.py
│   │   ├── store.py
│   │   └── coins.py
│   ├── api/                 # API endpoints
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   ├── store.py
│   │   ├── coins.py
│   │   └── stats.py
│   ├── services/            # Бизнес логика
│   │   ├── auth_service.py
│   │   ├── task_service.py
│   │   ├── coin_service.py
│   │   └── notification_service.py
│   └── utils/
│       ├── auth.py          # JWT токены
│       ├── permissions.py   # Проверка прав
│       └── redis.py         # Кеширование
├── alembic/                 # Миграции БД
├── tests/
└── Dockerfile
```

### Пример основного файла приложения

```python
# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, tasks, store, coins, stats
from app.database import engine, create_tables

app = FastAPI(
    title="FamilyCoins API",
    description="API для семейного мотивационного приложения",
    version="1.0.0"
)

# CORS для мобильного приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/v1/tasks", tags=["tasks"])
app.include_router(store.router, prefix="/v1/store", tags=["store"])
app.include_router(coins.router, prefix="/v1/coins", tags=["coins"])
app.include_router(stats.router, prefix="/v1/stats", tags=["stats"])

@app.on_event("startup")
async def startup():
    await create_tables()

@app.get("/")
async def root():
    return {"message": "FamilyCoins API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## 📱 Frontend интеграция

### HTTP клиент для мобильного приложения

```typescript
// api/client.ts
class FamilyCoinsAPI {
  private baseURL = 'https://api.familycoins.app/v1';
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    };

    const response = await fetch(url, { ...options, headers });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return response.json();
  }

  // Семья и аутентификация
  async createFamily(familyName: string, parentName: string) {
    return this.request('/auth/family/create', {
      method: 'POST',
      body: JSON.stringify({
        family_name: familyName,
        parent_name: parentName,
      }),
    });
  }

  async joinFamily(passcode: string, userName: string, role: 'parent' | 'child') {
    return this.request('/auth/family/join', {
      method: 'POST',
      body: JSON.stringify({
        passcode,
        user_name: userName,
        role,
      }),
    });
  }

  // Задания
  async getMyTasks() {
    return this.request('/tasks/my');
  }

  async completeTask(assignmentId: string, proofText?: string, proofImageUrl?: string) {
    return this.request(`/tasks/assignments/${assignmentId}/complete`, {
      method: 'PUT',
      body: JSON.stringify({
        proof_text: proofText,
        proof_image_url: proofImageUrl,
      }),
    });
  }

  async approveTask(assignmentId: string, approved: boolean, feedback?: string) {
    return this.request(`/tasks/assignments/${assignmentId}/approve`, {
      method: 'PUT',
      body: JSON.stringify({
        approved,
        feedback,
      }),
    });
  }

  // Магазин
  async getStoreItems() {
    return this.request('/store/items');
  }

  async purchaseItem(itemId: string) {
    return this.request('/store/purchase', {
      method: 'POST',
      body: JSON.stringify({
        item_id: itemId,
      }),
    });
  }

  // Коины
  async getCoinBalance() {
    return this.request('/coins/balance');
  }

  async getCoinTransactions(limit = 20, offset = 0) {
    return this.request(`/coins/transactions?limit=${limit}&offset=${offset}`);
  }
}

export const api = new FamilyCoinsAPI();
```

---

## 🚀 Развертывание

### Docker конфигурация

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose для локальной разработки

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/familycoins
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET_KEY=your_secret_key_here
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=familycoins
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Переменные окружения

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/familycoins
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
PUSH_NOTIFICATIONS_ENABLED=true
FCM_SERVER_KEY=your_fcm_server_key
```

---

## 📋 План разработки

### Этап 1: Backend API (2-3 недели)
1. **Неделя 1**: Настройка проекта, модели данных, базовая аутентификация
2. **Неделя 2**: API для заданий и магазина
3. **Неделя 3**: API для коинов, статистики, тестирование

### Этап 2: Мобильное приложение (2-3 недели)  
1. **Неделя 1**: Базовая структура, экраны аутентификации
2. **Неделя 2**: Экраны заданий и магазина
3. **Неделя 3**: Интеграция с API, отладка

### Этап 3: Тестирование и деплой (1 неделя)
1. Интеграционное тестирование
2. Настройка production окружения
3. Деплой и мониторинг

---

**Версия документа:** 1.0  
**Дата создания:** $(date)  
**Статус:** Ready for Development  
**Предыдущий документ:** Simplified MVP Specification  
**Следующий документ:** Development Guide