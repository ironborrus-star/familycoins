# Деплой FamilyCoins на VK Cloud

## Почему VK Cloud?
- 🆓 **3 месяца бесплатно** для новых пользователей
- 🇷🇺 **Российская платформа** с поддержкой на русском
- 🚀 **Kubernetes** из коробки
- 🗄️ **Managed PostgreSQL и Redis**
- 💰 **Конкурентные цены** после trial периода

## Шаг 1: Регистрация на VK Cloud

1. Идите на [cloud.vk.com](https://cloud.vk.com)
2. Регистрируйтесь (можно через VK/Mail.ru)
3. Активируйте trial на 3000₽
4. Выберите регион: Москва

## Шаг 2: Создание базы данных PostgreSQL

### 2.1 Через веб-интерфейс
1. **Базы данных** → **Создать кластер**
2. **PostgreSQL 15**
3. **Конфигурация**: Basic (1 vCPU, 2GB RAM)
4. **Имя кластера**: `familycoins-db`
5. **База данных**: `familycoins`
6. **Пользователь**: `familycoins_user`
7. **Пароль**: сгенерируйте сложный

### 2.2 Настройка сети
- **Подсеть**: default
- **Группа безопасности**: разрешить порт 5432
- **Публичный доступ**: Да (для простоты)

## Шаг 3: Создание Redis

1. **Базы данных** → **Redis** → **Создать кластер**
2. **Конфигурация**: Basic
3. **Имя**: `familycoins-redis`
4. **Без пароля** (для простоты) или задайте пароль

## Шаг 4: Создание Kubernetes кластера

### 4.1 Создание кластера
1. **Контейнеры** → **Kubernetes** → **Создать кластер**
2. **Имя**: `familycoins-k8s`
3. **Версия**: 1.28 (актуальная)
4. **Тип сети**: Calico
5. **Группа узлов**:
   - **Тип ВМ**: STD2-2-4 (2 vCPU, 4GB RAM)
   - **Количество узлов**: 1
   - **Автомасштабирование**: включить

### 4.2 Подключение к кластеру
```bash
# Установите kubectl если еще нет
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Скачайте kubeconfig из VK Cloud панели
# Файл → Настройки кластера → Скачать kubeconfig
```

## Шаг 5: Подготовка манифестов Kubernetes

### 5.1 Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: familycoins
---
```

### 5.2 ConfigMap с переменными
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: familycoins-config
  namespace: familycoins
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  API_V1_STR: "/v1"
---
```

### 5.3 Secret с паролями
```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: familycoins-secret
  namespace: familycoins
type: Opaque
stringData:
  JWT_SECRET_KEY: "your_super_secret_jwt_key_min_32_chars"
  DATABASE_URL: "postgresql+asyncpg://familycoins_user:password@postgres-host:5432/familycoins"
  REDIS_URL: "redis://redis-host:6379"
---
```

### 5.4 Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: familycoins-api
  namespace: familycoins
spec:
  replicas: 2
  selector:
    matchLabels:
      app: familycoins-api
  template:
    metadata:
      labels:
        app: familycoins-api
    spec:
      containers:
      - name: api
        image: cr.cloud.vk.com/your-registry/familycoins:latest
        ports:
        - containerPort: 8000
        env:
        - name: PORT
          value: "8000"
        envFrom:
        - configMapRef:
            name: familycoins-config
        - secretRef:
            name: familycoins-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
```

### 5.5 Service
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: familycoins-service
  namespace: familycoins
spec:
  selector:
    app: familycoins-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
---
```

## Шаг 6: Загрузка Docker образа

### 6.1 Создание Container Registry
1. **Контейнеры** → **Container Registry** → **Создать реестр**
2. **Имя**: `familycoins-registry`

### 6.2 Сборка и загрузка образа
```bash
# Получите адрес реестра из VK Cloud панели
REGISTRY_URL="cr.cloud.vk.com/your-project/familycoins"

# Соберите образ
docker build -t $REGISTRY_URL:latest ./backend

# Авторизуйтесь в реестре (токен из панели VK Cloud)
docker login cr.cloud.vk.com -u oauth -p your_oauth_token

# Загрузите образ
docker push $REGISTRY_URL:latest
```

## Шаг 7: Деплой в Kubernetes

```bash
# Примените все манифесты
kubectl apply -f k8s/

# Проверьте статус
kubectl get pods -n familycoins
kubectl get services -n familycoins

# Получите внешний IP
kubectl get service familycoins-service -n familycoins
```

## Шаг 8: Настройка домена (опционально)

### 8.1 Через VK Cloud DNS
1. **Сеть** → **DNS** → **Создать зону**
2. Добавьте A-запись с внешним IP LoadBalancer

### 8.2 SSL сертификат
```yaml
# Можно использовать cert-manager для автоматических Let's Encrypt сертификатов
```

## Стоимость

### Trial (3 месяца бесплатно)
- **PostgreSQL**: ~500₽/месяц
- **Redis**: ~300₽/месяц  
- **Kubernetes**: ~800₽/месяц
- **Container Registry**: ~100₽/месяц
- **Трафик**: ~200₽/месяц
- **Итого**: ~1900₽/месяц (покрывается trial)

### После trial
- **Скидка 50%** при оплате за год
- **Реальная стоимость**: ~950₽/месяц

## Альтернативный простой вариант: Compute Cloud VM

Если Kubernetes кажется сложным:

```bash
# 1. Создайте ВМ Ubuntu 22.04 (2 vCPU, 4GB RAM)
# 2. Установите Docker
curl -fsSL https://get.docker.com | sh

# 3. Клонируйте репозиторий
git clone https://github.com/ironborrus-star/familycoins.git

# 4. Создайте .env файл с настройками БД
# 5. Запустите приложение
cd familycoins
docker-compose -f backend/docker-compose.prod.yml up -d
```

## Мониторинг

VK Cloud предоставляет:
- 📊 **Встроенный мониторинг** Kubernetes
- 📝 **Логи** в реальном времени
- 🚨 **Алерты** по метрикам
- 📈 **Grafana dashboards**

---

**Преимущества VK Cloud:**
- 🇷🇺 Российская юрисдикция
- 💰 Хорошие цены
- 🆓 Длительный trial
- 📞 Поддержка на русском
- 🔧 Managed сервисы
