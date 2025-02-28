#!/bin/sh
set -e  # Останавливаем скрипт при любой ошибке

cd app
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя, если его еще нет
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin")
    print("Суперпользователь создан!")
else:
    print("Суперпользователь уже существует.")
EOF

# Используем 'exec', чтобы PID процесса сервера был PID контейнера
exec python manage.py runserver 0.0.0.0:$PORT