# 🏆 FamilyCoins - Семейное мотивационное приложение

Веб-приложение для мотивации детей через систему задач и вознаграждений.

## 🚀 Быстрый старт

### Локальная разработка

```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/familycoins.git
cd familycoins

# Запустите с Docker
docker-compose up -d

# Приложение доступно на:
# Frontend: http://localhost:8080
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Деплой в облаке

#### Railway (рекомендуется для начала)
1. Создайте аккаунт на [railway.app](https://railway.app)
2. Подключите этот GitHub репозиторий
3. Railway автоматически создаст PostgreSQL и Redis
4. Настройте переменные окружения (см. `.env.example`)
5. Готово! 🎉

#### DigitalOcean
Следуйте инструкциям в [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

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
│   ├── Dockerfile          # Docker образ
│   └── requirements.txt    # Python зависимости
├── frontend/               # HTML/CSS/JS фронтенд
├── .github/workflows/      # CI/CD пайплайны
└── docs/                   # Документация
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
