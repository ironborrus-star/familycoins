# 🏆 FamilyCoins - Семейное мотивационное приложение

Веб-приложение для мотивации детей через систему задач и вознаграждений.

## 🚀 Быстрый старт

### Локальная разработка

```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/familycoins.git
cd familycoins

# Backend (в отдельном терминале)
cd backend
pip install -r requirements.txt
cp .env.example .env
# Настройте переменные в .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (в отдельном терминале)
cd frontend
cp .env.example .env
# Настройте переменные в .env
python start_server.py

# Приложение доступно на:
# Frontend: http://localhost:8080
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Деплой в облаке

#### Railway (рекомендуется)

**Backend:**
1. Создайте аккаунт на [railway.app](https://railway.app)
2. Создайте новый проект и подключите этот GitHub репозиторий
3. Railway автоматически обнаружит `backend/railway.toml`
4. Добавьте PostgreSQL и Redis сервисы
5. Настройте переменные окружения из `backend/.env.example`

**Frontend:**
1. В том же проекте Railway добавьте новый сервис
2. Подключите тот же GitHub репозиторий
3. Railway автоматически обнаружит `frontend/railway.toml`
4. Настройте переменные окружения из `frontend/.env.example`
5. Укажите URL backend сервиса в `API_BASE_URL`

Подробные инструкции: [docs/deployment/](./docs/deployment/)

#### Другие платформы
- **DigitalOcean**: [docs/deployment/DEPLOYMENT_GUIDE.md](./docs/deployment/DEPLOYMENT_GUIDE.md)
- **Vercel/Netlify**: для frontend
- **Heroku**: альтернатива Railway

## 📁 Структура проекта

```
familycoins/
├── backend/                 # FastAPI приложение
│   ├── app/
│   │   ├── api/            # API роутеры
│   │   ├── models/         # SQLAlchemy модели
│   │   ├── schemas/        # Pydantic схемы
│   │   ├── services/       # Бизнес логика
│   │   └── utils/          # Утилиты
│   ├── alembic/            # Миграции БД
│   ├── tests/              # Тесты backend
│   ├── Dockerfile          # Docker образ backend
│   ├── railway.toml        # Конфигурация Railway для backend
│   ├── requirements.txt    # Python зависимости
│   └── .env.example        # Пример переменных backend
├── frontend/               # HTML/CSS/JS фронтенд
│   ├── *.html              # HTML страницы
│   ├── *.css               # Стили
│   ├── *.js                # JavaScript логика
│   ├── Dockerfile          # Docker образ frontend
│   ├── railway.toml        # Конфигурация Railway для frontend
│   └── .env.example        # Пример переменных frontend
├── docs/                   # Документация
│   ├── deployment/         # Инструкции по развертыванию
│   └── DOC/                # Техническая документация
└── README.md               # Этот файл
```

## 🛠 Технологии

### Backend
- **FastAPI** - современный Python веб-фреймворк
- **PostgreSQL** - надежная реляционная база данных
- **Redis** - кэширование и сессии
- **SQLAlchemy** - ORM для работы с БД
- **Alembic** - миграции базы данных

### Frontend
- **Vanilla JavaScript** - без лишних зависимостей
- **CSS Grid/Flexbox** - современная верстка
- **Responsive Design** - адаптивность

### DevOps
- **Docker** - контейнеризация
- **GitHub Actions** - CI/CD
- **Nginx** - reverse proxy
- **Prometheus + Grafana** - мониторинг

## 🎯 Основные функции

- ✅ **Система пользователей** - родители и дети
- ✅ **Задачи** - создание и назначение задач
- ✅ **Монеты** - виртуальная валюта за выполнение
- ✅ **Магазин** - покупка вознаграждений
- ✅ **Цели** - долгосрочная мотивация
- ✅ **Статистика** - отслеживание прогресса

## 📊 API документация

После запуска приложения API документация доступна по адресу:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Разработка

### Требования
- Python 3.11+
- Docker и Docker Compose
- Git

### Установка зависимостей
```bash
cd backend
pip install -r requirements.txt
```

### Переменные окружения
Скопируйте `.env.example` в `.env` и настройте:
```bash
cp .env.example .env
```

### Миграции базы данных
```bash
cd backend
alembic upgrade head
```

### Запуск тестов
```bash
cd backend
pytest
```

## 🤝 Участие в разработке

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📝 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## 📞 Поддержка

- 📧 Email: support@familycoins.app
- 💬 Telegram: @familycoins_support
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/familycoins/issues)

---

Сделано с ❤️ для семей!
