#!/bin/sh
set -e  # Останавливаем скрипт при любой ошибке

cd app
python manage.py makemigrations
python manage.py migrate

# Используем 'exec', чтобы PID процесса сервера был PID контейнера
exec python manage.py runserver 0.0.0.0:8000