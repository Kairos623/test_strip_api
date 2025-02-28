#!/bin/sh
set -e

cd app
python manage.py makemigrations
python manage.py migrate


python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin")
    print("Суперпользователь создан!")
else:
    print("Суперпользователь уже существует.")
EOF


exec python manage.py runserver 0.0.0.0:${PORT:-8000}