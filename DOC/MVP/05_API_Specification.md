# API Specification
## Спецификация API для MVP FamilyCoins

---

> **Версия API:** v1.0  
> **Стандарт:** OpenAPI 3.0.3  
> **Base URL:** `https://api.familycoins.app/v1`  
> **Аутентификация:** Bearer JWT Token

---

## 📋 Table of Contents

1. [Authentication API](#authentication-api)
2. [Family Management API](#family-management-api)
3. [Task & Goal API](#task--goal-api)
4. [Store & Economy API](#store--economy-api)
5. [Analytics API](#analytics-api)
6. [Notification API](#notification-api)
7. [Common Schemas](#common-schemas)
8. [Error Handling](#error-handling)

---

## 🔐 Authentication API

### Base Path: `/auth`

#### POST `/auth/register`
Регистрация нового пользователя

**Request Body:**
```json
{
  "email": "parent@example.com",
  "password": "securePassword123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "parent",
  "family_name": "Doe Family",
  "timezone": "Europe/Moscow",
  "language": "ru"
}
```

**Response 201:**
```json
{
  "user": {
    "id": "uuid-v4",
    "email": "parent@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "parent",
    "family_id": "uuid-v4",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

#### POST `/auth/login`
Вход в систему

**Request Body:**
```json
{
  "email": "parent@example.com",
  "password": "securePassword123"
}
```

**Response 200:**
```json
{
  "user": {
    "id": "uuid-v4",
    "email": "parent@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "parent",
    "family_id": "uuid-v4",
    "last_login": "2024-01-01T00:00:00Z"
  },
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer", 
    "expires_in": 1800
  }
}
```

#### POST `/auth/refresh`
Обновление токена доступа

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response 200:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST `/auth/logout`
Выход из системы

**Headers:** `Authorization: Bearer {access_token}`

**Response 200:**
```json
{
  "message": "Successfully logged out"
}
```

#### POST `/auth/forgot-password`
Восстановление пароля

**Request Body:**
```json
{
  "email": "parent@example.com"
}
```

**Response 200:**
```json
{
  "message": "Password reset email sent",
  "reset_token_expires_at": "2024-01-01T01:00:00Z"
}
```

---

## 👨‍👩‍👧‍👦 Family Management API

### Base Path: `/families`

#### GET `/families/me`
Получение информации о семье текущего пользователя

**Headers:** `Authorization: Bearer {access_token}`

**Response 200:**
```json
{
  "family": {
    "id": "uuid-v4",
    "name": "Doe Family",
    "created_at": "2024-01-01T00:00:00Z",
    "settings": {
      "timezone": "Europe/Moscow",
      "language": "ru",
      "currency": "RUB",
      "default_coin_rate": 1.0
    },
    "members": [
      {
        "id": "uuid-v4",
        "first_name": "John",
        "last_name": "Doe", 
        "role": "parent",
        "avatar_url": "https://cdn.familycoins.app/avatars/uuid.jpg",
        "joined_at": "2024-01-01T00:00:00Z"
      },
      {
        "id": "uuid-v4-2",
        "first_name": "Jane",
        "last_name": "Doe",
        "role": "child",
        "age": 10,
        "avatar_url": "https://cdn.familycoins.app/avatars/uuid2.jpg",
        "joined_at": "2024-01-02T00:00:00Z"
      }
    ],
    "devices": [
      {
        "id": "uuid-v4",
        "user_id": "uuid-v4-2",
        "device_name": "Jane's iPhone",
        "platform": "ios",
        "model": "iPhone 13",
        "last_seen": "2024-01-01T12:00:00Z",
        "is_active": true
      }
    ]
  }
}
```

#### POST `/families/members`
Добавление нового члена семьи (ребенка)

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "first_name": "Alice",
  "last_name": "Doe",
  "age": 8,
  "role": "child",
  "initial_coin_balance": 100
}
```

**Response 201:**
```json
{
  "member": {
    "id": "uuid-v4-3",
    "first_name": "Alice",
    "last_name": "Doe",
    "role": "child",
    "age": 8,
    "family_id": "uuid-v4",
    "coin_balance": 100,
    "created_at": "2024-01-01T00:00:00Z",
    "invite_code": "ABC123"
  }
}
```

#### PUT `/families/members/{member_id}`
Обновление информации о члене семьи

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "first_name": "Alice",
  "age": 9,
  "avatar_url": "https://cdn.familycoins.app/avatars/new-avatar.jpg"
}
```

**Response 200:**
```json
{
  "member": {
    "id": "uuid-v4-3",
    "first_name": "Alice",
    "last_name": "Doe",
    "role": "child",
    "age": 9,
    "avatar_url": "https://cdn.familycoins.app/avatars/new-avatar.jpg",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### POST `/families/devices`
Регистрация нового устройства

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "user_id": "uuid-v4-2",
  "device_name": "Jane's iPad",
  "platform": "ios",
  "model": "iPad Pro",
  "os_version": "17.2",
  "app_version": "1.0.0",
  "device_token": "fcm-or-apns-token"
}
```

**Response 201:**
```json
{
  "device": {
    "id": "uuid-v4-device",
    "user_id": "uuid-v4-2",
    "device_name": "Jane's iPad",
    "platform": "ios",
    "model": "iPad Pro",
    "registered_at": "2024-01-01T00:00:00Z",
    "is_active": true
  }
}
```

---

## 📋 Task & Goal API

### Base Path: `/tasks`

#### GET `/tasks`
Получение списка заданий

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**
- `status` (optional): `all`, `assigned`, `in_progress`, `completed`, `overdue`
- `assignee_id` (optional): UUID члена семьи
- `category` (optional): `screen_habits`, `physical_activity`, `household`, `education`
- `limit` (optional): количество результатов (default: 20)
- `offset` (optional): смещение для пагинации (default: 0)

**Response 200:**
```json
{
  "tasks": [
    {
      "id": "uuid-v4",
      "title": "Убрать комнату",
      "description": "Аккуратно убрать игрушки и заправить кровать",
      "category": "household",
      "reward_coins": 50,
      "status": "assigned",
      "priority": "medium",
      "created_by": "uuid-v4-parent",
      "assigned_to": "uuid-v4-child",
      "due_date": "2024-01-02T18:00:00Z",
      "created_at": "2024-01-01T09:00:00Z",
      "estimated_duration_minutes": 30,
      "requires_photo_proof": true,
      "recurring": {
        "is_recurring": true,
        "frequency": "daily",
        "end_date": "2024-12-31T23:59:59Z"
      }
    }
  ],
  "pagination": {
    "total": 45,
    "limit": 20,
    "offset": 0,
    "has_next": true
  }
}
```

#### POST `/tasks`
Создание нового задания

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "title": "Прочитать 20 страниц книги",
  "description": "Прочитать главу из книги 'Гарри Поттер'",
  "category": "education",
  "reward_coins": 30,
  "assigned_to": "uuid-v4-child",
  "due_date": "2024-01-02T20:00:00Z",
  "estimated_duration_minutes": 45,
  "requires_photo_proof": false,
  "priority": "high",
  "recurring": {
    "is_recurring": true,
    "frequency": "daily",
    "days_of_week": [1, 2, 3, 4, 5],
    "end_date": "2024-02-01T23:59:59Z"
  }
}
```

**Response 201:**
```json
{
  "task": {
    "id": "uuid-v4-new",
    "title": "Прочитать 20 страниц книги",
    "description": "Прочитать главу из книги 'Гарри Поттер'",
    "category": "education",
    "reward_coins": 30,
    "status": "assigned",
    "priority": "high",
    "created_by": "uuid-v4-parent",
    "assigned_to": "uuid-v4-child",
    "due_date": "2024-01-02T20:00:00Z",
    "created_at": "2024-01-01T10:00:00Z",
    "estimated_duration_minutes": 45,
    "requires_photo_proof": false
  }
}
```

#### PUT `/tasks/{task_id}/complete`
Отметка задания как выполненного

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "completion_notes": "Прочитал всю главу про квиддич!",
  "actual_duration_minutes": 40,
  "proof_photo_url": "https://cdn.familycoins.app/proofs/uuid-proof.jpg"
}
```

**Response 200:**
```json
{
  "task_completion": {
    "id": "uuid-completion",
    "task_id": "uuid-v4-new",
    "completed_by": "uuid-v4-child",
    "completed_at": "2024-01-02T19:30:00Z",
    "completion_notes": "Прочитал всю главу про квиддич!",
    "actual_duration_minutes": 40,
    "proof_photo_url": "https://cdn.familycoins.app/proofs/uuid-proof.jpg",
    "coins_earned": 30,
    "bonus_coins": 5,
    "status": "pending_approval"
  }
}
```

#### PUT `/tasks/{task_id}/approve`
Одобрение выполненного задания (только родители)

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "approved": true,
  "feedback": "Отлично выполнено! Молодец!",
  "bonus_coins": 10
}
```

**Response 200:**
```json
{
  "task_completion": {
    "id": "uuid-completion",
    "task_id": "uuid-v4-new",
    "approved_by": "uuid-v4-parent",
    "approved_at": "2024-01-02T20:00:00Z",
    "status": "approved",
    "feedback": "Отлично выполнено! Молодец!",
    "total_coins_earned": 40,
    "bonus_coins": 10
  },
  "coin_transaction": {
    "id": "uuid-transaction",
    "user_id": "uuid-v4-child",
    "amount": 40,
    "type": "task_reward",
    "description": "Задание: Прочитать 20 страниц книги",
    "created_at": "2024-01-02T20:00:00Z"
  }
}
```

#### GET `/tasks/templates`
Получение шаблонов заданий

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**
- `category` (optional): фильтр по категории
- `age_group` (optional): `preschool`, `elementary`, `middle`, `high`

**Response 200:**
```json
{
  "templates": [
    {
      "id": "template-1",
      "title": "Убрать игрушки",
      "description": "Аккуратно сложить все игрушки в коробку",
      "category": "household",
      "recommended_reward": 25,
      "estimated_duration_minutes": 15,
      "age_group": "preschool",
      "requires_photo_proof": true,
      "tips": "Сделайте уборку игрой - считайте игрушки вместе!"
    }
  ]
}
```

---

## 🛍️ Store & Economy API

### Base Path: `/store`

#### GET `/store/products`
Получение каталога товаров семейного магазина

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**
- `category` (optional): `digital_privileges`, `entertainment`, `material_goods`, `privileges`
- `available_only` (optional): `true`/`false` - только доступные товары
- `price_min` (optional): минимальная цена в коинах
- `price_max` (optional): максимальная цена в коинах

**Response 200:**
```json
{
  "products": [
    {
      "id": "product-1",
      "name": "Дополнительное время в YouTube",
      "description": "30 минут дополнительного времени в YouTube",
      "category": "digital_privileges",
      "subcategory": "screen_time",
      "price_coins": 50,
      "is_available": true,
      "stock_quantity": null,
      "image_url": "https://cdn.familycoins.app/products/youtube-time.png",
      "created_by": "uuid-v4-parent",
      "created_at": "2024-01-01T00:00:00Z",
      "purchase_limit": {
        "per_day": 2,
        "per_week": 10,
        "per_month": null
      },
      "age_restrictions": {
        "min_age": 8,
        "max_age": null
      }
    },
    {
      "id": "product-2", 
      "name": "Поход в кино",
      "description": "Семейный поход в кинотеатр на выбранный фильм",
      "category": "entertainment",
      "subcategory": "family_activity",
      "price_coins": 300,
      "is_available": true,
      "stock_quantity": 1,
      "image_url": "https://cdn.familycoins.app/products/cinema.png",
      "created_by": "uuid-v4-parent",
      "estimated_real_cost": "1500 RUB"
    }
  ],
  "user_balance": {
    "coins": 245,
    "last_updated": "2024-01-01T15:30:00Z"
  }
}
```

#### POST `/store/products`
Создание нового товара (только родители)

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "name": "Новая настольная игра",
  "description": "Покупка новой настольной игры на выбор ребенка",
  "category": "material_goods",
  "subcategory": "toys_games",
  "price_coins": 500,
  "stock_quantity": 1,
  "image_url": "https://cdn.familycoins.app/products/board-game.png",
  "estimated_real_cost": "2000 RUB",
  "purchase_limit": {
    "per_month": 1
  },
  "age_restrictions": {
    "min_age": 6,
    "max_age": 14
  }
}
```

**Response 201:**
```json
{
  "product": {
    "id": "product-new",
    "name": "Новая настольная игра",
    "description": "Покупка новой настольной игры на выбор ребенка",
    "category": "material_goods",
    "subcategory": "toys_games",
    "price_coins": 500,
    "is_available": true,
    "stock_quantity": 1,
    "created_by": "uuid-v4-parent",
    "created_at": "2024-01-01T16:00:00Z"
  }
}
```

#### POST `/store/purchases`
Покупка товара

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "product_id": "product-1",
  "quantity": 1,
  "notes": "Хочу посмотреть новое видео про майнкрафт"
}
```

**Response 201:**
```json
{
  "purchase": {
    "id": "purchase-uuid",
    "product_id": "product-1",
    "product_name": "Дополнительное время в YouTube",
    "user_id": "uuid-v4-child",
    "quantity": 1,
    "total_cost": 50,
    "status": "completed",
    "purchased_at": "2024-01-01T17:00:00Z",
    "notes": "Хочу посмотреть новое видео про майнкрафт",
    "valid_until": "2024-01-01T23:59:59Z"
  },
  "coin_transaction": {
    "id": "transaction-uuid",
    "user_id": "uuid-v4-child",
    "amount": -50,
    "type": "purchase",
    "description": "Покупка: Дополнительное время в YouTube",
    "balance_after": 195
  }
}
```

#### GET `/store/purchases`
История покупок

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**
- `user_id` (optional): фильтр по пользователю
- `status` (optional): `completed`, `used`, `expired`, `refunded`
- `date_from` (optional): дата начала периода
- `date_to` (optional): дата окончания периода

**Response 200:**
```json
{
  "purchases": [
    {
      "id": "purchase-uuid",
      "product_name": "Дополнительное время в YouTube",
      "quantity": 1,
      "total_cost": 50,
      "status": "used",
      "purchased_at": "2024-01-01T17:00:00Z",
      "used_at": "2024-01-01T19:00:00Z",
      "valid_until": "2024-01-01T23:59:59Z"
    }
  ]
}
```

---

## 💰 Token Economy API

### Base Path: `/economy`

#### GET `/economy/balance`
Получение баланса пользователя

**Headers:** `Authorization: Bearer {access_token}`

**Response 200:**
```json
{
  "balance": {
    "user_id": "uuid-v4-child",
    "current_balance": 245,
    "total_earned": 1200,
    "total_spent": 955,
    "last_updated": "2024-01-01T17:00:00Z"
  },
  "recent_transactions": [
    {
      "id": "trans-1",
      "amount": -50,
      "type": "purchase",
      "description": "Покупка: Дополнительное время в YouTube",
      "created_at": "2024-01-01T17:00:00Z",
      "balance_after": 195
    },
    {
      "id": "trans-2", 
      "amount": 40,
      "type": "task_reward",
      "description": "Задание: Прочитать 20 страниц книги",
      "created_at": "2024-01-01T15:00:00Z",
      "balance_after": 245
    }
  ]
}
```

#### GET `/economy/transactions`
История транзакций

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**
- `user_id` (optional): фильтр по пользователю (только родители могут смотреть других)
- `type` (optional): `task_reward`, `purchase`, `bonus`, `adjustment`, `allowance`
- `date_from` (optional): начальная дата
- `date_to` (optional): конечная дата
- `limit` (optional): количество результатов
- `offset` (optional): смещение

**Response 200:**
```json
{
  "transactions": [
    {
      "id": "trans-uuid",
      "user_id": "uuid-v4-child",
      "amount": 40,
      "type": "task_reward",
      "description": "Задание: Прочитать 20 страниц книги",
      "created_at": "2024-01-01T15:00:00Z",
      "balance_before": 205,
      "balance_after": 245,
      "metadata": {
        "task_id": "uuid-v4-task",
        "approved_by": "uuid-v4-parent"
      }
    }
  ],
  "pagination": {
    "total": 150,
    "limit": 20,
    "offset": 0
  }
}
```

#### POST `/economy/adjust-balance`
Корректировка баланса (только родители)

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "user_id": "uuid-v4-child",
  "amount": 100,
  "type": "bonus",
  "reason": "Отличная неделя! Бонус за старания",
  "description": "Недельный бонус за примерное поведение"
}
```

**Response 200:**
```json
{
  "transaction": {
    "id": "trans-adjustment",
    "user_id": "uuid-v4-child",
    "amount": 100,
    "type": "bonus",
    "description": "Недельный бонус за примерное поведение",
    "created_at": "2024-01-01T18:00:00Z",
    "created_by": "uuid-v4-parent",
    "balance_after": 345
  }
}
```

#### GET `/economy/family-stats`
Статистика экономики семьи

**Headers:** `Authorization: Bearer {access_token}`

**Response 200:**
```json
{
  "family_stats": {
    "total_coins_in_circulation": 1250,
    "total_coins_earned_this_month": 800,
    "total_coins_spent_this_month": 450,
    "most_active_earner": {
      "user_id": "uuid-v4-child",
      "name": "Jane Doe",
      "coins_earned": 500
    },
    "popular_purchases": [
      {
        "product_name": "Дополнительное время в YouTube",
        "purchase_count": 8,
        "total_spent": 400
      }
    ],
    "economy_health": {
      "circulation_velocity": 2.3,
      "inflation_rate": 0.05,
      "recommendation": "Экономика здоровая, рассмотрите добавление новых товаров"
    }
  }
}
```

---

## 📊 Analytics API

### Base Path: `/analytics`

#### GET `/analytics/family-dashboard`
Дашборд семейной аналитики

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**
- `period` (optional): `week`, `month`, `quarter`, `year` (default: `month`)

**Response 200:**
```json
{
  "period": "month",
  "date_range": {
    "from": "2024-01-01T00:00:00Z",
    "to": "2024-01-31T23:59:59Z"
  },
  "overview": {
    "total_tasks_completed": 45,
    "total_coins_earned": 1200,
    "total_coins_spent": 800,
    "average_task_completion_time": 25,
    "family_engagement_score": 85
  },
  "task_analytics": {
    "completion_rate": 78,
    "by_category": [
      {
        "category": "household",
        "completed": 15,
        "assigned": 18,
        "completion_rate": 83
      },
      {
        "category": "education", 
        "completed": 12,
        "assigned": 15,
        "completion_rate": 80
      }
    ],
    "by_child": [
      {
        "user_id": "uuid-v4-child",
        "name": "Jane Doe",
        "completed": 20,
        "completion_rate": 85,
        "favorite_category": "education"
      }
    ]
  },
  "economy_analytics": {
    "spending_by_category": [
      {
        "category": "digital_privileges",
        "amount": 400,
        "percentage": 50
      },
      {
        "category": "entertainment",
        "amount": 300,
        "percentage": 37.5
      }
    ],
    "top_purchases": [
      {
        "product_name": "Дополнительное время в YouTube",
        "count": 8,
        "total_spent": 400
      }
    ]
  },
  "engagement_trends": {
    "daily_active_sessions": [
      {"date": "2024-01-01", "sessions": 5},
      {"date": "2024-01-02", "sessions": 7}
    ],
    "weekly_task_completion": [
      {"week": "2024-W01", "completed": 12},
      {"week": "2024-W02", "completed": 15}
    ]
  }
}
```

#### GET `/analytics/child/{child_id}/report`
Индивидуальный отчет ребенка

**Headers:** `Authorization: Bearer {access_token}`

**Response 200:**
```json
{
  "child": {
    "user_id": "uuid-v4-child",
    "name": "Jane Doe",
    "age": 10
  },
  "period_stats": {
    "tasks_completed": 20,
    "tasks_assigned": 25,
    "completion_rate": 80,
    "coins_earned": 600,
    "coins_spent": 350,
    "current_balance": 250
  },
  "achievements": [
    {
      "id": "achievement-1",
      "name": "Reading Master",
      "description": "Completed 10 reading tasks this month",
      "earned_at": "2024-01-15T00:00:00Z",
      "badge_url": "https://cdn.familycoins.app/badges/reading-master.png"
    }
  ],
  "strengths": [
    "Excellent at educational tasks",
    "Consistent daily performance",
    "Good time management"
  ],
  "improvement_areas": [
    "Could improve on household tasks",
    "Sometimes misses weekend assignments"
  ],
  "recommendations": [
    "Try gamifying household chores",
    "Set up weekend reminder notifications"
  ]
}
```

#### GET `/analytics/screen-time`
Аналитика экранного времени

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**
- `user_id` (optional): конкретный ребенок
- `period` (optional): `day`, `week`, `month`

**Response 200:**
```json
{
  "screen_time_data": [
    {
      "user_id": "uuid-v4-child",
      "name": "Jane Doe",
      "daily_average_minutes": 120,
      "daily_limit_minutes": 180,
      "compliance_rate": 85,
      "by_app": [
        {
          "app_name": "YouTube",
          "minutes": 45,
          "percentage": 37.5
        },
        {
          "app_name": "Minecraft",
          "minutes": 35,
          "percentage": 29.2
        }
      ],
      "weekly_trend": [
        {"date": "2024-01-01", "minutes": 110},
        {"date": "2024-01-02", "minutes": 130}
      ]
    }
  ]
}
```

---

## 🔔 Notification API

### Base Path: `/notifications`

#### GET `/notifications`
Получение списка уведомлений

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**
- `status` (optional): `unread`, `read`, `all` (default: `all`)
- `type` (optional): `task_assigned`, `task_completed`, `purchase`, `achievement`
- `limit` (optional): количество результатов

**Response 200:**
```json
{
  "notifications": [
    {
      "id": "notif-1",
      "type": "task_completed",
      "title": "Задание выполнено!",
      "message": "Jane выполнила задание 'Убрать комнату'",
      "is_read": false,
      "created_at": "2024-01-01T15:30:00Z",
      "data": {
        "task_id": "uuid-v4-task",
        "user_id": "uuid-v4-child",
        "coins_earned": 50
      }
    },
    {
      "id": "notif-2",
      "type": "achievement",
      "title": "Новое достижение!",
      "message": "Jane получила значок 'Reading Master'",
      "is_read": true,
      "created_at": "2024-01-01T12:00:00Z",
      "data": {
        "achievement_id": "achievement-1",
        "user_id": "uuid-v4-child"
      }
    }
  ]
}
```

#### PUT `/notifications/{notification_id}/read`
Отметка уведомления как прочитанного

**Headers:** `Authorization: Bearer {access_token}`

**Response 200:**
```json
{
  "notification": {
    "id": "notif-1",
    "is_read": true,
    "read_at": "2024-01-01T16:00:00Z"
  }
}
```

#### POST `/notifications/send`
Отправка custom уведомления (только родители)

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "recipient_id": "uuid-v4-child",
  "type": "custom",
  "title": "Напоминание",
  "message": "Не забудь покормить кота!",
  "schedule_at": "2024-01-01T18:00:00Z"
}
```

**Response 201:**
```json
{
  "notification": {
    "id": "notif-custom",
    "type": "custom",
    "title": "Напоминание", 
    "message": "Не забудь покормить кота!",
    "recipient_id": "uuid-v4-child",
    "scheduled_at": "2024-01-01T18:00:00Z",
    "created_at": "2024-01-01T15:00:00Z"
  }
}
```

---

## 📋 Common Schemas

### User Schema
```json
{
  "id": "string (uuid)",
  "email": "string (email)",
  "first_name": "string",
  "last_name": "string",
  "role": "enum ['parent', 'child']",
  "age": "integer (nullable, only for children)",
  "family_id": "string (uuid)",
  "avatar_url": "string (url, nullable)",
  "created_at": "string (datetime)",
  "updated_at": "string (datetime)",
  "last_login": "string (datetime, nullable)"
}
```

### Family Schema
```json
{
  "id": "string (uuid)",
  "name": "string",
  "settings": {
    "timezone": "string",
    "language": "string",
    "currency": "string",
    "default_coin_rate": "number"
  },
  "created_at": "string (datetime)",
  "updated_at": "string (datetime)"
}
```

### Task Schema
```json
{
  "id": "string (uuid)",
  "title": "string",
  "description": "string",
  "category": "enum ['screen_habits', 'physical_activity', 'household', 'education']",
  "reward_coins": "integer",
  "status": "enum ['assigned', 'in_progress', 'completed', 'approved', 'rejected']",
  "priority": "enum ['low', 'medium', 'high']",
  "family_id": "string (uuid)",
  "created_by": "string (uuid)",
  "assigned_to": "string (uuid)",
  "due_date": "string (datetime)",
  "created_at": "string (datetime)",
  "updated_at": "string (datetime)",
  "estimated_duration_minutes": "integer",
  "requires_photo_proof": "boolean",
  "recurring": {
    "is_recurring": "boolean",
    "frequency": "enum ['daily', 'weekly', 'monthly']",
    "days_of_week": "array of integers (1-7)",
    "end_date": "string (datetime, nullable)"
  }
}
```

### Product Schema
```json
{
  "id": "string (uuid)",
  "name": "string",
  "description": "string",
  "category": "enum ['digital_privileges', 'entertainment', 'material_goods', 'privileges']",
  "subcategory": "string",
  "price_coins": "integer",
  "is_available": "boolean",
  "stock_quantity": "integer (nullable)",
  "image_url": "string (url)",
  "family_id": "string (uuid)",
  "created_by": "string (uuid)",
  "created_at": "string (datetime)",
  "purchase_limit": {
    "per_day": "integer (nullable)",
    "per_week": "integer (nullable)",
    "per_month": "integer (nullable)"
  },
  "age_restrictions": {
    "min_age": "integer (nullable)",
    "max_age": "integer (nullable)"
  }
}
```

### Transaction Schema
```json
{
  "id": "string (uuid)",
  "user_id": "string (uuid)",
  "amount": "integer",
  "type": "enum ['task_reward', 'purchase', 'bonus', 'adjustment', 'allowance']",
  "description": "string",
  "created_at": "string (datetime)",
  "balance_before": "integer",
  "balance_after": "integer",
  "metadata": "object (optional additional data)"
}
```

---

## ❌ Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (optional)",
    "timestamp": "string (datetime)",
    "request_id": "string (uuid)"
  }
}
```

### HTTP Status Codes

| Code | Description | When to Use |
|------|-------------|-------------|
| 200 | OK | Successful GET, PUT requests |
| 201 | Created | Successful POST requests |
| 204 | No Content | Successful DELETE requests |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid auth token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource conflict (e.g., duplicate) |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |

### Common Error Codes

```json
{
  "INVALID_CREDENTIALS": {
    "status": 401,
    "message": "Invalid email or password"
  },
  "INSUFFICIENT_BALANCE": {
    "status": 422,
    "message": "Not enough coins for this purchase"
  },
  "TASK_ALREADY_COMPLETED": {
    "status": 409,
    "message": "This task has already been completed"
  },
  "FAMILY_MEMBER_NOT_FOUND": {
    "status": 404,
    "message": "Family member not found"
  },
  "PERMISSION_DENIED": {
    "status": 403,
    "message": "You don't have permission to perform this action"
  },
  "VALIDATION_ERROR": {
    "status": 422,
    "message": "Validation failed",
    "details": {
      "field_errors": {
        "email": ["Email is required"],
        "age": ["Age must be between 3 and 18"]
      }
    }
  }
}
```

### Rate Limiting

**Headers in Response:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
```

**Rate Limits:**
- Authentication endpoints: 10 requests per minute
- General API: 1000 requests per hour per user
- File uploads: 100 requests per hour per user

---

## 🔐 Authentication & Security

### JWT Token Format
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "uuid-v4",
    "family_id": "uuid-v4",
    "role": "parent",
    "exp": 1609459200,
    "iat": 1609457400,
    "type": "access"
  }
}
```

### Required Headers
```http
Authorization: Bearer {access_token}
Content-Type: application/json
Accept: application/json
X-API-Version: v1
```

### Optional Headers
```http
X-Request-ID: uuid-v4
X-Device-ID: device-uuid
X-App-Version: 1.0.0
X-Platform: ios|android
```

---

**Версия документа:** 1.0  
**Дата создания:** $(date)  
**Статус:** Ready for Implementation  
**Swagger/OpenAPI файл:** Готовится отдельно  
**Постман коллекция:** Готовится отдельно

---

**🎯 API готов к использованию!** Эта спецификация покрывает все основные функции MVP и готова для implementation команды разработки.