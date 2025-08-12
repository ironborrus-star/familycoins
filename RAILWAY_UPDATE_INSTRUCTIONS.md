# 🔄 Инструкции по обновлению Railway после реорганизации

После реорганизации проекта на backend и frontend части, необходимо обновить конфигурацию в Railway.

## 📋 Что изменилось

### Структура файлов:
- `Dockerfile` → `backend/Dockerfile`
- `railway-backend.toml` → `backend/railway.toml`
- `Dockerfile.frontend` → `frontend/Dockerfile`
- `railway-frontend.toml` → `frontend/railway.toml`
- Документация перемещена в `docs/deployment/`

## 🚀 Пошаговые инструкции

### 1. Обновление Backend сервиса

1. **Откройте ваш проект в Railway**
2. **Перейдите в Backend сервис**
3. **Обновите настройки сборки:**
   - Settings → Source → Root Directory: `/backend`
   - Settings → Build → Dockerfile Path: `Dockerfile` (не `backend/Dockerfile`)
   - Railway автоматически найдет `backend/railway.toml`

4. **Проверьте переменные окружения:**
   - Убедитесь что все переменные из `backend/.env.example` настроены
   - Особенно важно: `JWT_SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`

5. **Запустите Redeploy:**
   - Deployments → Redeploy latest

### 2. Обновление Frontend сервиса

1. **Перейдите в Frontend сервис**
2. **Обновите настройки сборки:**
   - Settings → Source → Root Directory: `/frontend`
   - Settings → Build → Dockerfile Path: `Dockerfile` (не `frontend/Dockerfile`)
   - Railway автоматически найдет `frontend/railway.toml`

3. **Проверьте переменные окружения:**
   ```env
   API_BASE_URL=https://ваш-backend-сервис.railway.app
   APP_NAME=FamilyCoins
   APP_VERSION=1.0.0
   ENVIRONMENT=production
   ```

4. **Запустите Redeploy:**
   - Deployments → Redeploy latest

### 3. Если сервисы не настроены

Если у вас еще нет отдельных сервисов для backend и frontend:

#### Создание Backend сервиса:
1. New Service → GitHub Repo → Выберите ваш репозиторий
2. Root Directory: `/backend`
3. Railway найдет `backend/railway.toml` и `backend/Dockerfile`
4. Добавьте PostgreSQL и Redis сервисы
5. Настройте переменные окружения

#### Создание Frontend сервиса:
1. New Service → GitHub Repo → Выберите тот же репозиторий
2. Root Directory: `/frontend`
3. Railway найдет `frontend/railway.toml` и `frontend/Dockerfile`
4. Настройте переменные окружения
5. Укажите URL backend в `API_BASE_URL`

## ✅ Проверка работоспособности

### Backend:
- `https://ваш-backend.railway.app/health` - должен вернуть статус OK
- `https://ваш-backend.railway.app/docs` - Swagger документация

### Frontend:
- `https://ваш-frontend.railway.app/` - главная страница
- Проверьте в DevTools → Network что API запросы идут на правильный backend URL

### Интеграция:
- Попробуйте войти в систему
- Создайте тестовую задачу
- Проверьте что все функции работают

## 🐛 Возможные проблемы

### Backend не запускается:
- Проверьте логи в Railway Deployments
- Убедитесь что `DATABASE_URL` и `REDIS_URL` настроены
- Проверьте что PostgreSQL и Redis сервисы созданы и работают

### Frontend не загружается:
- Проверьте логи сборки
- Убедитесь что `API_BASE_URL` указывает на правильный backend
- Проверьте что nginx конфигурация корректна

### API запросы не работают:
- Проверьте CORS настройки в backend
- Убедитесь что `BACKEND_CORS_ORIGINS` включает URL frontend
- Проверьте что `API_BASE_URL` в frontend правильный

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи в Railway
2. Сравните с примерами в `docs/deployment/`
3. Создайте Issue в GitHub репозитории

## 🎉 Готово!

После успешного обновления:
- Backend и Frontend развертываются независимо
- Изменения в одной части не влияют на другую
- Можно разрабатывать и деплоить раздельно
- Легче масштабировать и поддерживать

---

**Удалите этот файл после выполнения инструкций**
