# 🚀 Git Деплой FamilyCoins на Railway (Монорепозиторий)

## Обзор архитектуры

У вас **монорепозиторий** с двумя сервисами:
```
FamilyCoins/
├── backend/          # FastAPI приложение
├── frontend/         # Статический сайт на Nginx
├── Dockerfile        # Для backend сервиса
├── Dockerfile.frontend  # Для frontend сервиса
├── railway-backend.toml   # 🆕 Конфигурация backend
└── railway-frontend.toml  # 🆕 Конфигурация frontend
```

## Шаг 1: Подготовка GitHub репозитория

### 1.1 Убедитесь что код в Git
```bash
# Проверьте статус
git status

# Если есть изменения, добавьте их
git add .
git commit -m "🔧 Настройка Railway Git деплоя"
git push origin main
```

### 1.2 Проверьте структуру репо
Убедитесь что в корне есть:
- ✅ `Dockerfile` (для backend)
- ✅ `Dockerfile.frontend` (для frontend)  
- ✅ `railway-backend.toml` (конфигурация backend)
- ✅ `railway-frontend.toml` (конфигурация frontend)

## Шаг 2: Деплой Backend сервиса

### 2.1 Создание Backend сервиса
1. Откройте [railway.app](https://railway.app) → войдите через GitHub
2. Нажмите **"New Project"**
3. Выберите **"Deploy from GitHub repo"**
4. Выберите репозиторий **FamilyCoins**
5. Railway создаст первый сервис автоматически

### 2.2 Настройка Backend сервиса
1. Railway должен обнаружить `railway-backend.toml`
2. Если нет, в **Settings → Build**:
   - Source Provider: GitHub
   - Repository: ваш репо
   - Build Command: (оставить пустым)
   - Dockerfile Path: `Dockerfile`

### 2.3 Добавление баз данных
1. **PostgreSQL**: + New Service → Database → PostgreSQL  
2. **Redis**: + New Service → Database → Redis
3. Railway автоматически создаст переменные `DATABASE_URL` и `REDIS_URL`

### 2.4 Переменные окружения Backend
```env
# Автоматически созданные Railway
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
PORT=${{PORT}}

# Добавьте вручную
ENVIRONMENT=production
DEBUG=false
JWT_SECRET_KEY=ваш_секретный_ключ_32_символа
BACKEND_CORS_ORIGINS=["https://${{RAILWAY_STATIC_URL}}"]
LOG_LEVEL=INFO
```

## Шаг 3: Деплой Frontend сервиса

### 3.1 Создание Frontend сервиса  
1. В том же проекте нажмите **"+ New Service"**
2. Выберите **"GitHub Repo"** 
3. Выберите **тот же репозиторий** FamilyCoins
4. Railway создаст второй сервис

### 3.2 Настройка Frontend сервиса
1. Railway должен обнаружить `railway-frontend.toml`
2. Если нет, в **Settings → Build**:
   - Source Provider: GitHub  
   - Repository: ваш репо
   - Dockerfile Path: `Dockerfile.frontend`
   - Root Directory: `/` (корень репо)

### 3.3 Переменные окружения Frontend
```env
# Обязательно! URL вашего backend сервиса
API_BASE_URL=https://ваш-backend-сервис.railway.app

# Опционально
APP_NAME=FamilyCoins
APP_VERSION=1.0.0
ENVIRONMENT=production
```

⚠️ **Важно**: Замените `ваш-backend-сервис.railway.app` на реальный URL!

## Шаг 4: Настройка автоматического деплоя

### 4.1 Настройка Watch Paths (опционально)
Если хотите деплоить сервисы только при изменении их файлов:

**Backend сервис** → Settings → Source → Watch Paths:
```
backend/**
Dockerfile
railway-backend.toml
requirements.txt
```

**Frontend сервис** → Settings → Source → Watch Paths:  
```
frontend/**
Dockerfile.frontend
railway-frontend.toml
```

### 4.2 Настройка CORS
Обновите переменную в Backend сервисе:
```env
BACKEND_CORS_ORIGINS=["https://ваш-frontend-url.railway.app", "http://localhost:8080"]
```

## Шаг 5: Тестирование Git деплоя

### 5.1 Тест автоматического деплоя
```bash
# Внесите изменение в код
echo "<!-- Test deploy -->" >> frontend/index.html

# Закоммитьте и запушьте  
git add .
git commit -m "🧪 Test automatic deploy"
git push origin main
```

### 5.2 Проверка деплоя
1. В Railway Dashboard → Deployments  
2. Должны увидеть новые деплои обоих сервисов
3. Следите за логами сборки

### 5.3 Проверка работы
- Backend: `https://ваш-backend.railway.app/health`
- Frontend: `https://ваш-frontend.railway.app/`  
- API Docs: `https://ваш-backend.railway.app/docs`

## Troubleshooting

### ❌ Railway не находит конфигурацию
**Решение**: 
1. Убедитесь что `railway-frontend.toml` в корне репо
2. Проверьте синтаксис TOML файла
3. Попробуйте ручную настройку в Settings → Build

### ❌ Frontend не может подключиться к Backend  
**Решение**:
1. Проверьте переменную `API_BASE_URL` в Frontend
2. Обновите `BACKEND_CORS_ORIGINS` в Backend
3. Проверьте что config.js генерируется (в логах Frontend)

### ❌ Деплой не запускается автоматически
**Решение**:
1. Проверьте что репо подключен к Railway
2. Убедитесь что изменения действительно запушены в main ветку
3. Проверьте Watch Paths в настройках

### ❌ Сборка падает с ошибкой Docker
**Решение**:
1. Проверьте что Dockerfile.frontend находится в корне
2. Убедитесь что все пути в COPY командах корректны
3. Локально протестируйте сборку:
   ```bash
   docker build -f Dockerfile.frontend -t test-frontend .
   ```

## Мониторинг и логи

### Просмотр логов
- Railway Dashboard → ваш сервис → Deployments → View Logs
- Фильтрация по времени и уровню (Info, Error, etc.)

### Метрики  
- CPU, Memory, Network usage
- Response time и количество запросов
- Доступно в разделе Metrics

## Стоимость монорепо деплоя

- **2 сервиса Railway**: $0-10/месяц  
- **PostgreSQL + Redis**: включены бесплатно
- **GitHub интеграция**: бесплатно
- **Автоматический деплой**: бесплатно

**Итого**: $0-10/месяц для полного стека! 💰

## Альтернативы при росте нагрузки

### Когда пора мигрировать:
- 🚀 Более 10,000 пользователей
- 📊 Нужен детальный мониторинг  
- 🔄 Требуется CI/CD pipeline
- 🌍 Нужны multiple регионы

### Варианты миграции:
1. **DigitalOcean App Platform** - похожий на Railway
2. **AWS/GCP/Azure** - полный контроль
3. **Kubernetes** - максимальная гибкость

---

## ✅ Итоговый чек-лист

- [ ] Code закоммичен в GitHub
- [ ] Backend сервис создан и работает  
- [ ] PostgreSQL и Redis добавлены
- [ ] Frontend сервис создан с правильным Dockerfile
- [ ] Переменные окружения настроены
- [ ] CORS настроен между сервисами
- [ ] Автоматический деплой протестирован
- [ ] URLs сервисов обновлены в документации

Ваше приложение готово к Git деплою! 🎉
