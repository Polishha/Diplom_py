# Дипломный проект: API для автоматизации закупок

## Описание
Backend-приложение для автоматизации закупок в розничной сети. REST API для взаимодействия покупателей, поставщиков и администраторов.

## Функциональность
- **Покупатели**: регистрация, каталог товаров, корзина, заказы
- **Поставщики**: загрузка прайс-листов (YAML), управление статусами заказов
- **Администраторы**: полное управление через Django Admin

## Технологии
- Python 3.10+, Django 4.2.16, Django REST Framework
- SQLite/PostgreSQL, JWT аутентификация
- Swagger документация, YAML парсинг

## Установка и запуск

```bash
# Клонировать репозиторий
git clone https://github.com/Polishha/Diplom_py
cd Diplom_py

# Создать и активировать виртуальное окружение
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# venv\Scripts\activate   # для Windows

# Установить зависимости
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env, указав свои значения

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver