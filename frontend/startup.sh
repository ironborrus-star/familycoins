#!/bin/sh

# Устанавливаем дефолтный порт если PORT не задан
export PORT=${PORT:-80}
echo "Starting nginx on port $PORT"

# Подставляем PORT в конфигурацию
envsubst '$PORT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# Показываем итоговую конфигурацию для отладки
echo "Generated nginx config:"
cat /etc/nginx/conf.d/default.conf

# Запускаем nginx
exec nginx -g 'daemon off;'
