# Руководство по деплою FamilyCoins в облаке

## Обзор инфраструктуры

Приложение состоит из:
- **Backend API** - FastAPI приложение с PostgreSQL и Redis
- **Frontend** - Статические HTML/CSS/JS файлы через Nginx  
- **Мониторинг** - Prometheus + Grafana
- **CI/CD** - GitHub Actions

## Варианты деплоя

### 1. 🚀 Быстрый деплой (рекомендуется для начала)

#### DigitalOcean App Platform
```bash
# 1. Создайте аккаунт на DigitalOcean
# 2. Подключите GitHub репозиторий
# 3. Настройте автодеплой из ветки main
# 4. Добавьте переменные окружения (см. ниже)
```

#### Heroku
```bash
# 1. Установите Heroku CLI
heroku create familycoins-app
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini

# 2. Настройте переменные окружения
heroku config:set ENVIRONMENT=production
heroku config:set DEBUG=false
heroku config:set JWT_SECRET_KEY=your_super_secret_key

# 3. Деплой
git push heroku main
```

### 2. 🔧 Полный деплой на VPS

#### Требования к серверу
- **CPU**: 2+ ядра
- **RAM**: 4GB+
- **Диск**: 20GB+ SSD
- **ОС**: Ubuntu 20.04/22.04

#### Установка на сервер

```bash
# 1. Подключение к серверу
ssh root@your-server-ip

# 2. Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker

# 3. Установка Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 4. Клонирование проекта
git clone https://github.com/your-username/familycoins.git /opt/familycoins
cd /opt/familycoins

# 5. Настройка окружения
cp .env.example .env
nano .env  # Редактируем переменные

# 6. Запуск продакшен версии
docker-compose -f backend/docker-compose.prod.yml up -d
```

## Переменные окружения

### Обязательные переменные
```bash
# База данных (для внешней БД)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Redis (для внешнего Redis)
REDIS_URL=redis://host:6379

# Безопасность
JWT_SECRET_KEY=your_super_secret_jwt_key_min_32_chars
ENVIRONMENT=production
DEBUG=false

# CORS (домены вашего приложения)
BACKEND_CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
```

### Дополнительные переменные
```bash
# Сервер
HOST=0.0.0.0
PORT=8000

# Логирование
LOG_LEVEL=INFO

# JWT настройки
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Облачные базы данных

### PostgreSQL
- **AWS RDS** - самый надежный вариант
- **DigitalOcean Managed Database** - простой в настройке
- **Supabase** - бесплатный тариф доступен

### Redis
- **Redis Cloud** - бесплатный тариф 30MB
- **AWS ElastiCache** - масштабируемый
- **DigitalOcean Managed Redis**

## SSL/TLS сертификаты

### Автоматические сертификаты (рекомендуется)
```bash
# Установка Certbot
apt install certbot python3-certbot-nginx

# Получение сертификата
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Автопродление
crontab -e
# Добавить: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Настройка домена
1. Купите домен (Namecheap, GoDaddy, etc.)
2. Настройте DNS записи:
   ```
   A record: @ -> your-server-ip
   A record: www -> your-server-ip
   ```

## Мониторинг

### Запуск мониторинга
```bash
cd /opt/familycoins
docker-compose -f backend/monitoring/docker-compose.monitoring.yml up -d
```

### Доступ к интерфейсам
- **Grafana**: http://your-server:3000 (admin/admin123)
- **Prometheus**: http://your-server:9090

## Автоматический деплой (CI/CD)

### Настройка GitHub Actions

1. **Создайте secrets в GitHub**:
   ```
   HOST: your-server-ip
   USERNAME: root
   SSH_KEY: your-private-ssh-key
   ```

2. **Настройте SSH ключи**:
   ```bash
   # На локальной машине
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/familycoins_deploy
   
   # Скопируйте публичный ключ на сервер
   ssh-copy-id -i ~/.ssh/familycoins_deploy.pub root@your-server
   
   # Добавьте приватный ключ в GitHub Secrets
   cat ~/.ssh/familycoins_deploy  # Скопируйте содержимое
   ```

3. **Пуш в main ветку автоматически запустит деплой**

## Резервное копирование

### Автоматический бэкап БД
```bash
#!/bin/bash
# /opt/scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
DB_CONTAINER="familycoins_postgres_1"

# Создание бэкапа
docker exec $DB_CONTAINER pg_dump -U user familycoins > $BACKUP_DIR/backup_$DATE.sql

# Удаление старых бэкапов (старше 7 дней)
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete

# Добавить в crontab:
# 0 2 * * * /opt/scripts/backup.sh
```

## Масштабирование

### Горизонтальное масштабирование
```yaml
# В docker-compose.prod.yml
api:
  deploy:
    replicas: 3  # Увеличить количество инстансов
```

### Вертикальное масштабирование
```yaml
# Увеличить ресурсы контейнера
deploy:
  resources:
    limits:
      cpus: '1.0'      # Было '0.5'
      memory: 1024M    # Было 512M
```

## Безопасность

### Обновления системы
```bash
# Регулярно обновляйте сервер
apt update && apt upgrade -y

# Настройте файрвол
ufw allow ssh
ufw allow 80
ufw allow 443
ufw enable
```

### Ограничение доступа к API
- Используйте API ключи для внешних интеграций
- Настройте rate limiting в Nginx
- Регулярно меняйте JWT_SECRET_KEY

## Поиск проблем

### Логи
```bash
# Логи приложения
docker-compose logs api

# Логи Nginx
docker-compose logs nginx

# Системные логи
journalctl -u docker.service
```

### Проверка состояния
```bash
# Health check
curl http://your-domain/health

# Статус контейнеров
docker ps

# Использование ресурсов
docker stats
```

## Контакты для поддержки

- 📧 **Email**: support@yourcompany.com
- 💬 **Telegram**: @yourusername
- 📞 **Телефон**: +7 (xxx) xxx-xx-xx

---

**Удачного деплоя! 🚀**
