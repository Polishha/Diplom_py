# Дипломный проект: API для автоматизации закупок

## Описание
Backend-приложение для автоматизации закупок в розничной сети.

## Установка и запуск

```bash
# Клонировать репозиторий
git clone https://github.com/Polishha/Diplom_py

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows

# Установить зависимости
pip install -r requirements.txt

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver