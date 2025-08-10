# 🚀 Деплой Frontend на Railway

## Краткое описание изменений

Настройка деплоя frontend была исправлена для корректной работы с переменными окружения и правильной конфигурацией Railway.

### ✅ Исправленные проблемы

1. **Убран захардкоженный API URL** - теперь используются переменные окружения
2. **Добавлена поддержка конфигурации** - создан `config.js.template` для динамической подстановки переменных
3. **Обновлен Dockerfile.frontend** - добавлена поддержка переменных окружения
4. **Улучшен startup script** - корректная обработка переменных и генерация конфигурации
5. **Создан nginx template** - поддержка динамического PORT

## Пошаговая инструкция деплоя

### Шаг 1: Подготовка (уже готово ✅)

Все необходимые файлы созданы:
- ✅ `Dockerfile.frontend` - обновлен
- ✅ `frontend/config.js.template` - создан
- ✅ `frontend/nginx.conf.template` - создан  
- ✅ `frontend/startup.sh` - обновлен
- ✅ `railway-frontend.json` - проверен
- ✅ `railway-frontend-env-template.txt` - создан

### Шаг 2: Создание Frontend сервиса в Railway (Git деплой)

#### Важно! У вас монорепозиторий - нужна специальная настройка

1. **Откройте ваш проект в Railway**
2. **Добавьте новый сервис:**
   - Нажмите "+ New Service" 
   - Выберите "GitHub Repo"
   - Выберите тот же репозиторий (где уже есть backend)

3. **Настройте конфигурацию для монорепо:**
   
   **Вариант А: Через railway.toml (рекомендуется)**
   - Railway обнаружит `railway-frontend.toml` 
   - Автоматически настроит сборку через `Dockerfile.frontend`
   
   **Вариант Б: Ручная настройка**
   - В Settings → Source: укажите Root Directory = `/` (корень репо)
   - В Settings → Build: выберите Dockerfile
   - Укажите Dockerfile Path = `Dockerfile.frontend`
   
4. **Важные настройки для монорепо:**
   - ✅ Source: подключен к тому же GitHub репо
   - ✅ Watch Paths: следить за изменениями во всем репо
   - ✅ Dockerfile Path: `Dockerfile.frontend` (а не `frontend/Dockerfile`)

### Шаг 3: Настройка переменных окружения

Перейдите в Frontend Service → Variables и добавьте:

```env
# Основная конфигурация (ОБЯЗАТЕЛЬНО)
API_BASE_URL=https://ваш-backend-сервис.railway.app

# Информация о приложении (опционально)
APP_NAME=FamilyCoins
APP_VERSION=1.0.0
ENVIRONMENT=production
```

⚠️ **Важно**: Замените `ваш-backend-сервис.railway.app` на реальный URL вашего backend сервиса!

### Шаг 4: Деплой

1. **Railway автоматически начнет сборку**
2. **Следите за логами** во вкладке "Deployments"
3. **Проверьте успешность сборки**

### Шаг 5: Получение URL Frontend

После успешного деплоя:
1. Перейдите в Settings → Domains
2. Скопируйте URL вида: `https://familycoins-frontend-production-xxxx.up.railway.app`

### Шаг 6: Обновление CORS в Backend

Добавьте URL frontend в переменные окружения backend:

```env
BACKEND_CORS_ORIGINS=["https://ваш-frontend-url.railway.app", "http://localhost:8080"]
```

### Шаг 7: Тестирование

Откройте frontend URL в браузере и проверьте:
- ✅ Страница загружается
- ✅ API запросы работают (проверьте в DevTools → Network)
- ✅ Авторизация функционирует
- ✅ Все функции приложения работают

## Структура файлов

```
frontend/
├── index.html              # Основная страница (обновлена)
├── app.js                  # JS логика (исправлен API_BASE_URL)
├── styles.css              # Стили
├── config.js.template      # 🆕 Шаблон конфигурации
├── nginx.conf.template     # 🆕 Nginx template
├── nginx.conf              # Старая конфигурация (можно удалить)
├── startup.sh              # 🔄 Обновленный startup script
└── Dockerfile.nginx        # Альтернативный Dockerfile (можно удалить)

Dockerfile.frontend         # 🔄 Основной Dockerfile (обновлен)
railway-frontend.json       # ✅ Конфигурация Railway
railway-frontend-env-template.txt  # 🆕 Шаблон переменных
```

## Отладка

### Если frontend не загружается

1. **Проверьте логи сборки** в Railway Deployments
2. **Убедитесь что Dockerfile корректный**:
   ```bash
   # Локальная проверка
   docker build -f Dockerfile.frontend -t frontend-test .
   docker run -p 8080:80 -e API_BASE_URL=http://localhost:8000 frontend-test
   ```

### Если API запросы не работают

1. **Проверьте переменную API_BASE_URL** в Railway Variables
2. **Откройте DevTools → Console** и проверьте `window.APP_CONFIG`
3. **Проверьте CORS в backend** - добавьте frontend URL в BACKEND_CORS_ORIGINS

### Если конфигурация не применяется

1. **Проверьте startup script логи** в Railway
2. **Убедитесь что файл config.js генерируется**:
   ```bash
   # В логах должно быть:
   # Generated config.js:
   # window.APP_CONFIG = { API_BASE_URL: '...' }
   ```

## Мониторинг

Railway предоставляет:
- 📊 **Логи в реальном времени** - следите за ошибками
- 📈 **Метрики производительности** - использование ресурсов
- 🔄 **Автоматический перезапуск** - при ошибках
- 🌐 **CDN** - быстрая доставка статики

## Стоимость

- **Railway**: $0-5/месяц (в зависимости от трафика)
- **Два сервиса**: Backend + Frontend = до $10/месяц
- **Итого**: $0-10/месяц 💰

## Альтернативы

Если Railway становится дорогим:

### Vercel (рекомендуется для статики)
```bash
# Скопируйте только папку frontend в отдельный репозиторий
# Настройте Build Command: cp config.js.template public/config.js && echo "window.APP_CONFIG={API_BASE_URL:'$API_BASE_URL'}" > public/config.js
# Переменные: API_BASE_URL=https://ваш-backend.railway.app
```

### Netlify
```bash
# Загрузите папку frontend
# Создайте файл _redirects:
# /api/* https://ваш-backend.railway.app/v1/:splat 200
# /* /index.html 200
```

## Следующие шаги

1. ✅ **Frontend деплой настроен**
2. 🔄 **Протестируйте полную интеграцию**
3. 🎯 **Настройте кастомный домен** (опционально)
4. 📊 **Настройте мониторинг** (опционально)

Ваше приложение готово к использованию! 🎉
