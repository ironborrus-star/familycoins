# 🎨 FamilyCoins Frontend

Современный веб-интерфейс для системы мотивации детей.

## 🚀 Быстрый старт

### Локальная разработка

```bash
# Перейти в папку frontend
cd frontend

# Настроить конфигурацию
cp .env.example .env
# Отредактируйте .env файл

# Запустить простой HTTP сервер
python start_server.py

# Или использовать любой статический сервер
# python -m http.server 8080
# npx serve .
```

### Docker

```bash
# Из корня проекта
docker build -t familycoins-frontend -f frontend/Dockerfile frontend/

# Запуск с переменными окружения
docker run -p 8080:8080 \
  -e API_BASE_URL=http://localhost:8000 \
  -e APP_NAME=FamilyCoins \
  familycoins-frontend
```

## 🛠 Технологии

- **Vanilla JavaScript** - без лишних зависимостей
- **CSS Grid/Flexbox** - современная верстка
- **Responsive Design** - адаптивность для всех устройств
- **Nginx** - веб-сервер для продакшена
- **Docker** - контейнеризация

## 📁 Структура

```
frontend/
├── index.html              # Главная страница
├── login.html              # Страница входа
├── dashboard.html          # Дашборд пользователя
├── app.js                  # Основная логика приложения
├── config.js               # Конфигурация (генерируется автоматически)
├── styles.css              # Стили приложения
├── config.js.template      # Шаблон конфигурации
├── nginx.conf.template     # Шаблон конфигурации Nginx
├── startup.sh              # Скрипт запуска с переменными окружения
├── Dockerfile              # Docker образ
├── railway.toml            # Конфигурация Railway
└── .env.example            # Пример переменных окружения
```

## ⚙️ Конфигурация

Frontend использует переменные окружения для настройки:

```env
# API конфигурация
API_BASE_URL=http://localhost:8000

# Информация о приложении
APP_NAME=FamilyCoins
APP_VERSION=1.0.0
ENVIRONMENT=development
```

Конфигурация автоматически генерируется в файл `config.js` при запуске контейнера.

## 🎨 Особенности

- **Адаптивный дизайн** - работает на всех устройствах
- **Темная тема** - современный интерфейс
- **Быстрая загрузка** - оптимизированные ресурсы
- **Безопасность** - JWT аутентификация
- **Реактивность** - динамическое обновление данных

## 🚀 Развертывание

### Railway

1. Создайте проект в Railway
2. Подключите этот репозиторий
3. Railway автоматически обнаружит `railway.toml`
4. Настройте переменные окружения из `.env.example`
5. Укажите URL backend сервиса в `API_BASE_URL`

Подробные инструкции: [docs/deployment/FRONTEND_RAILWAY_DEPLOY.md](../docs/deployment/FRONTEND_RAILWAY_DEPLOY.md)

### Альтернативы

#### Vercel
```bash
# Загрузите папку frontend в Vercel
# Настройте переменные окружения
# Build Command: cp config.js.template public/config.js
```

#### Netlify
```bash
# Загрузите папку frontend в Netlify
# Создайте файл _redirects для SPA маршрутизации
```

## 🔧 Разработка

### Локальная разработка

```bash
# Запуск с автоматической перезагрузкой
python start_server.py --reload

# Или с любым статическим сервером
npx live-server --port=8080
```

### Отладка

1. **Откройте DevTools** (F12)
2. **Console** - проверьте ошибки JavaScript
3. **Network** - проверьте API запросы
4. **Application** - проверьте localStorage/sessionStorage

### Тестирование

```bash
# Проверка конфигурации
curl http://localhost:8080/config.js

# Проверка API соединения
curl http://localhost:8080/health
```

## 🤝 Участие в разработке

1. Создайте ветку для новой функции
2. Внесите изменения в HTML/CSS/JS
3. Протестируйте на разных устройствах
4. Убедитесь что все работает с backend API
5. Создайте Pull Request

## 📝 Лицензия

MIT License