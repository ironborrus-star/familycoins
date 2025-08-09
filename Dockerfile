# Многоэтапная сборка для оптимизации размера образа
FROM python:3.11-slim as builder

# Установка зависимостей для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Создание виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование и установка Python зависимостей
COPY backend/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Финальный образ
FROM python:3.11-slim

# Создание пользователя без root прав
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Копирование виртуального окружения из builder стадии
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Установка рабочей директории
WORKDIR /app

# Копирование кода приложения
COPY --chown=appuser:appuser backend/ .

# Переключение на пользователя без root прав
USER appuser

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Запуск приложения с поддержкой динамического порта (для Railway/Heroku)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
