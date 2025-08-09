# 📚 Создание GitHub репозитория и настройка деплоя

## Шаг 1: Создание репозитория на GitHub

### 1.1 Через веб-интерфейс GitHub
1. Идите на [github.com](https://github.com) и войдите в аккаунт
2. Нажмите зеленую кнопку **"New"** или **"Create repository"**
3. Заполните форму:
   ```
   Repository name: familycoins
   Description: 🏆 Семейное мотивационное приложение с системой задач и вознаграждений
   Public/Private: Public (рекомендуется для деплоя)
   ❌ НЕ добавляйте README, .gitignore, license (у нас уже есть)
   ```
4. Нажмите **"Create repository"**

### 1.2 Через GitHub CLI (альтернатива)
```bash
# Установите GitHub CLI если еще не установлен
brew install gh

# Войдите в аккаунт
gh auth login

# Создайте репозиторий
gh repo create familycoins --public --description "🏆 Семейное мотивационное приложение"
```

## Шаг 2: Связывание локального репозитория с GitHub

### 2.1 Добавление remote origin
```bash
# Замените YOUR_USERNAME на ваш GitHub username
git remote add origin https://github.com/YOUR_USERNAME/familycoins.git

# Проверьте что remote добавлен
git remote -v
```

### 2.2 Первый push
```bash
# Отправьте код на GitHub
git branch -M main
git push -u origin main
```

## Шаг 3: Настройка деплоя на Railway

### 3.1 Подключение к Railway
1. Идите на [railway.app](https://railway.app)
2. Нажмите **"Login with GitHub"**
3. Авторизуйте Railway доступ к вашим репозиториям
4. Нажмите **"New Project"**
5. Выберите **"Deploy from GitHub repo"**
6. Найдите и выберите репозиторий **familycoins**

### 3.2 Railway автоматически:
- 🔍 Найдет `railway.json` и `Dockerfile`
- 🗄️ Создаст PostgreSQL database
- 🔴 Создаст Redis database
- 🚀 Запустит первый деплой

### 3.3 Настройка переменных окружения в Railway
В Railway Dashboard → Settings → Variables добавьте:

```env
# Эти переменные Railway создаст автоматически
DATABASE_URL = ${{Postgres.DATABASE_URL}}
REDIS_URL = ${{Redis.REDIS_URL}}

# Эти нужно добавить вручную
ENVIRONMENT = production
DEBUG = false
JWT_SECRET_KEY = ваш_секретный_ключ_минимум_32_символа
BACKEND_CORS_ORIGINS = ["https://${{RAILWAY_STATIC_URL}}"]
LOG_LEVEL = INFO
```

## Шаг 4: Получение ссылки на приложение

После успешного деплоя Railway предоставит:
- 🌐 **Public URL**: `https://familycoins-production-xxxx.up.railway.app`
- 📊 **API Docs**: `https://familycoins-production-xxxx.up.railway.app/docs`
- ❤️ **Health Check**: `https://familycoins-production-xxxx.up.railway.app/health`

## Шаг 5: Настройка фронтенда

### 5.1 Опция 1: Отдельный деплой на Vercel
```bash
# 1. Создайте аккаунт на vercel.com
# 2. Подключите GitHub репозиторий
# 3. Выберите папку frontend для деплоя
# 4. Добавьте переменную окружения:
VITE_API_URL = https://ваш-railway-url.up.railway.app
```

### 5.2 Опция 2: Вместе с backend через Nginx
Добавьте в Railway переменную:
```env
SERVE_STATIC = true
```

## Шаг 6: Автоматический деплой

### 6.1 GitHub Actions (уже настроен)
Railway автоматически деплоит при каждом push в main ветку.

### 6.2 Проверка деплоя
```bash
# Внесите изменения
echo "# Test update" >> README.md

# Закоммитьте и отправьте
git add .
git commit -m "🧪 Test automatic deploy"
git push origin main

# Railway автоматически запустит новый деплой!
```

## Шаг 7: Мониторинг и отладка

### 7.1 Railway Dashboard
- 📊 **Metrics**: CPU, Memory, Network
- 📝 **Logs**: Real-time логи приложения
- ⚙️ **Settings**: Переменные окружения
- 💰 **Usage**: Использование ресурсов

### 7.2 Полезные команды Railway CLI
```bash
# Установка CLI
npm install -g @railway/cli

# Вход в аккаунт
railway login

# Просмотр логов
railway logs

# Подключение к базе данных
railway connect postgres

# Список переменных
railway variables

# Открыть приложение в браузере
railway open
```

## Шаг 8: Настройка домена (опционально)

### 8.1 Кастомный домен в Railway
1. Railway Dashboard → Settings → Domains
2. Нажмите **"Custom Domain"**
3. Введите ваш домен: `familycoins.ru`
4. Railway покажет CNAME запись для DNS

### 8.2 Настройка DNS
У вашего регистратора домена добавьте:
```
Type: CNAME
Name: familycoins.ru (или www)
Value: ваш-проект.up.railway.app
```

## 🎯 Полный процесс за 10 минут

```bash
# 1. Создайте GitHub репозиторий (2 мин)
# 2. Запушьте код (1 мин)
git remote add origin https://github.com/YOUR_USERNAME/familycoins.git
git push -u origin main

# 3. Подключите к Railway (3 мин)
# - Зайдите на railway.app
# - Deploy from GitHub
# - Выберите репозиторий

# 4. Настройте переменные (2 мин)
# - Добавьте JWT_SECRET_KEY
# - Остальные Railway создаст сам

# 5. Дождитесь деплоя (2 мин)
# - Railway автоматически соберет и запустит

# 🎉 Готово! Ваше приложение в облаке!
```

## ❗ Важные замечания

### Безопасность
- 🔐 **JWT_SECRET_KEY** должен быть сложным (минимум 32 символа)
- 🚫 Никогда не коммитьте `.env` файлы в Git
- 🔒 Используйте HTTPS в продакшене

### Ограничения Railway бесплатного тарифа
- ⏰ **500 часов/месяц** (около 16 часов в день)
- 💾 **1GB** storage для БД
- 🌐 **100GB** bandwidth
- 🔄 **Sleep after 30 min** inactivity

### Когда переходить на платный план
- 👥 Более 100 активных пользователей
- 🗄️ База данных больше 500MB
- 🚀 Нужна 24/7 работа без засыпания

## 🆘 Решение проблем

### Ошибка при деплое
```bash
# Проверьте логи в Railway Dashboard
railway logs

# Локальная отладка
docker build -t familycoins backend/
docker run -p 8000:8000 familycoins
```

### Проблемы с базой данных
```bash
# Подключитесь к Railway PostgreSQL
railway connect postgres

# Проверьте таблицы
\dt

# Выполните миграции вручную
railway run alembic upgrade head
```

### Медленная работа
- Проверьте метрики в Railway Dashboard
- Оптимизируйте SQL запросы
- Добавьте индексы в базу данных
- Перейдите на платный план Railway

---

**Удачи с деплоем! 🚀**

Если что-то не получается, пишите в Telegram: @your_username
