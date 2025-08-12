# 🚀 Руководства по развертыванию FamilyCoins

Коллекция инструкций для развертывания приложения FamilyCoins на различных платформах.

## 📋 Доступные руководства

### Railway (рекомендуется)
- **[RAILWAY_DEPLOY.md](./RAILWAY_DEPLOY.md)** - развертывание backend на Railway
- **[FRONTEND_RAILWAY_DEPLOY.md](./FRONTEND_RAILWAY_DEPLOY.md)** - развертывание frontend на Railway
- **[RAILWAY_GIT_DEPLOY_GUIDE.md](./RAILWAY_GIT_DEPLOY_GUIDE.md)** - подробное руководство по Git развертыванию

### Другие платформы
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - общее руководство по развертыванию
- **[GITHUB_SETUP.md](./GITHUB_SETUP.md)** - настройка GitHub репозитория

### Дополнительные материалы
- **[railway-deploy.md](./railway-deploy.md)** - краткое руководство по Railway

## 🎯 Рекомендуемый путь развертывания

### Для начинающих:
1. Следуйте [RAILWAY_DEPLOY.md](./RAILWAY_DEPLOY.md) для backend
2. Затем [FRONTEND_RAILWAY_DEPLOY.md](./FRONTEND_RAILWAY_DEPLOY.md) для frontend
3. Готово! 🎉

### Для опытных разработчиков:
1. Изучите [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
2. Выберите подходящую платформу
3. Настройте CI/CD через GitHub Actions

## 💰 Сравнение платформ

| Платформа | Backend | Frontend | Стоимость/мес | Сложность |
|-----------|---------|----------|---------------|-----------|
| Railway   | ✅      | ✅       | $0-10         | Легко     |
| Vercel    | ❌      | ✅       | $0            | Легко     |
| Netlify   | ❌      | ✅       | $0            | Легко     |
| DigitalOcean | ✅   | ✅       | $10-20        | Средне    |
| AWS       | ✅      | ✅       | $5-15         | Сложно    |

## 🛠 Структура проекта после реорганизации

```
familycoins/
├── backend/
│   ├── Dockerfile          # Docker образ для backend
│   ├── railway.toml        # Конфигурация Railway
│   └── .env.example        # Переменные окружения
├── frontend/
│   ├── Dockerfile          # Docker образ для frontend
│   ├── railway.toml        # Конфигурация Railway
│   └── .env.example        # Переменные окружения
└── docs/deployment/        # Эта папка с инструкциями
```

## 🔧 Переменные окружения

### Backend (.env)
```env
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET_KEY=your-secret-key
BACKEND_CORS_ORIGINS=["https://your-frontend-url"]
```

### Frontend (.env)
```env
API_BASE_URL=https://your-backend-url
APP_NAME=FamilyCoins
ENVIRONMENT=production
```

## 🆘 Помощь и поддержка

Если у вас возникли проблемы:

1. **Проверьте логи** в панели управления платформы
2. **Убедитесь** что все переменные окружения настроены
3. **Проверьте** что сервисы баз данных созданы и доступны
4. **Создайте Issue** в GitHub репозитории с описанием проблемы

## 📞 Контакты

- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/familycoins/issues)
- 💬 **Обсуждения**: [GitHub Discussions](https://github.com/your-username/familycoins/discussions)

---

Выберите подходящее руководство и следуйте инструкциям! 🚀
