Инструкция по запуску проекта

Данный документ описывает требования и шаги для локального запуска проекта на Windows (с использованием PowerShell от имени администратора) или Ubuntu (через терминал Linux).

----------------------------------------
Требования
----------------------------------------
Для корректной работы проекта необходимы следующие инструменты:
- Python: версия 3.12.8 (или любая версия из ветки 3.12)
- Docker: версия 27.5.1 (желательно, но допускаются и другие версии)
- Docker Compose: версия v2.32.4 (желательно, но допускаются и другие версии)
- PostgreSQL: версия 17 (рекомендуется установить на ПК. )

----------------------------------------
Запуск проекта через Docker
----------------------------------------
1. Клонирование репозитория  
   Откройте терминал (Linux) или PowerShell (Windows, от имени администратора) и выполните команду:
   git clone https://github.com/Kairos623/test_strip_api.git

2. Переход в директорию проекта  
   Перейдите в папку проекта:
   cd test_strip_api

3. Настройка файла окружения  
   - Переименуйте файл .offenv, удалив из его названия часть "off", чтобы получилось .env.
   - Откройте файл .env и внесите следующие настройки:
     
     DB_HOST=db
     DB_PORT=5432
     DB_USER=postgres
     DB_PASSWORD=postgres
     DB_NAME=strip_db
     
     SECRET_KEY=<значение, полученное с https://djecrety.ir/>
     
     STRIPE_API_KEY_EUR=<значение, созданное в Restricted keys в Stripe с правами:
       Charges=write, Customers=write, Funding Instructions=write,
       Balance=read, Payouts=read, SetupIntents=write, Checkout Sessions=write>
     
     STRIPE_API_KEY_USD=<значение, созданное в Restricted keys в Stripe с правами:
       Charges=write, Customers=write, Funding Instructions=write,
       Balance=read, Payouts=read, SetupIntents=write, Checkout Sessions=write>
     
     STRIPE_PUBLIC_KEY=<значение, полученное из Publishable key вашего sandbox в Stripe>

4. Запуск Docker контейнеров  
   Находясь в папке test_strip_api, выполните команду:
   docker-compose up --build
   Убедитесь, что Docker запущен на вашем компьютере.

5. Проверка работы приложения  
   После успешного запуска откройте браузер и перейдите по адресу:
   http://localhost:8000/
   http://localhost:8000/admin - логин и пароль - admin

----------------------------------------
Дополнительные рекомендации
----------------------------------------
- Проверьте, что установленные версии Docker, Docker Compose и PostgreSQL соответствуют требованиям.
- Если возникают вопросы или ошибки при запуске, обратитесь к официальной документации Docker (https://docs.docker.com/) и PostgreSQL (https://www.postgresql.org/docs/).

----------------------------------------
Инструкция составлена корректно и охватывает все необходимые шаги для локального запуска проекта.
