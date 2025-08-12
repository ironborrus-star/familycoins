# Деплой FamilyCoins на Railway

## Шаг 1: Подготовка проекта

### 1.1 Создайте файл railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 1.2 Обновите Dockerfile для Railway
```dockerfile
# В конце Dockerfile замените:
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# На:
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
```

## Шаг 2: Деплой на Railway

### 2.1 Регистрация
1. Идите на https://railway.app
2. Войдите через GitHub
3. Выберите репозиторий с проектом

### 2.2 Настройка сервисов
```bash
# Railway автоматически создаст:
# 1. Web Service (ваше приложение)
# 2. PostgreSQL Database
# 3. Redis Database
```

### 2.3 Переменные окружения
Добавьте в Railway Dashboard:

```env
# Автоматически создается Railway
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# Настройте вручную
ENVIRONMENT=production
DEBUG=false
JWT_SECRET_KEY=your_super_secret_key_min_32_chars
BACKEND_CORS_ORIGINS=["https://${{RAILWAY_STATIC_URL}}"]
LOG_LEVEL=INFO
```

## Шаг 3: Настройка домена

### 3.1 Получите Railway домен
```bash
# Railway автоматически даст домен вида:
# https://your-app-production.up.railway.app
```

### 3.2 Кастомный домен (опционально)
1. В Railway Dashboard → Settings → Domains
2. Добавьте ваш домен
3. Настройте DNS записи:
   ```
   CNAME: your-domain.com → your-app-production.up.railway.app
   ```

## Шаг 4: Деплой фронтенда

### 4.1 Отдельный сервис для фронтенда
```bash
# Создайте отдельный GitHub репозиторий для фронтенда
# Или используйте Netlify/Vercel для статики
```

### 4.2 Обновите CORS в бэкенде
```env
BACKEND_CORS_ORIGINS=["https://your-frontend-domain.com"]
```

## Шаг 5: Автоматический деплой

Railway автоматически:
- 🔄 Деплоит при пуше в main
- 📊 Показывает логи в реальном времени
- 📈 Мониторит здоровье приложения
- 🔧 Перезапускает при ошибках

## Шаг 6: Мониторинг

### 6.1 Встроенный мониторинг Railway
- CPU и Memory usage
- Network трафик
- Время отклика
- Логи приложения

### 6.2 Кастомные метрики
```bash
# Доступны через /metrics эндпоинт
curl https://your-app.railway.app/metrics
```

## Альтернативы для фронтенда

### Vercel (рекомендуется)
```bash
# 1. Создайте аккаунт на vercel.com
# 2. Подключите GitHub с фронтендом
# 3. Настройте переменные:
REACT_APP_API_URL=https://your-app.railway.app
```

### Netlify
```bash
# 1. Перетащите папку frontend на netlify.com
# 2. Настройте redirects в _redirects файле:
/api/* https://your-app.railway.app/v1/:splat 200
/* /index.html 200
```

## Стоимость

### Railway Pricing
- **Hobby**: $0-5/месяц (до 500 часов)
- **Pro**: $20/месяц (безлимит)
- **Databases**: включены бесплатно

### Общая стоимость MVP
- Railway (backend): $0-5/месяц
- Vercel (frontend): $0/месяц
- **Итого: $0-5/месяц** 🎉

## Команды для отладки

```bash
# Логи приложения
railway logs

# Подключение к БД
railway connect postgres

# Переменные окружения
railway variables

# Статус сервисов
railway status
```

## Миграция на DigitalOcean (когда нужно)

Признаки что пора переходить:
- 🚀 Более 1000 пользователей
- 📊 Нужен детальный мониторинг
- 🔄 Требуется load balancing
- 🗄️ Большая база данных (>1GB)

Миграция займет ~2 часа с нашей готовой конфигурацией!
