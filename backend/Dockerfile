# Dockerfile для Railway deployment
# Cache invalidation: v3
FROM python:3.11-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование и установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Создание пользователя без root прав
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port (Railway автоматически настроит $PORT)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:' + str(__import__('os').environ.get('PORT', '8000')) + '/health')" || exit 1

# Запуск приложения с динамическим портом
CMD ["python", "-c", "import os; import subprocess; port = os.environ.get('PORT', '8000'); subprocess.run(['uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', port, '--workers', '1'])"]