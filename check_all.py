import os
import sys
import django

print("=" * 60)
print("ПРОВЕРКА ПРОЕКТА")
print("=" * 60)

print("\n1. ПРОВЕРКА СТРУКТУРЫ ФАЙЛОВ:")
print("-" * 40)

files_to_check = [
    'manage.py',
    'orders/settings.py',
    'orders/urls.py',
    'backend/models.py',
    'backend/serializers.py',
    'backend/urls.py',
    'backend/admin.py',
    'backend/views/__init__.py',
    'backend/views/auth_views.py',
    'backend/views/product_views.py',
    'backend/views/cart_views.py',
    'backend/views/contact_views.py',
    'backend/views/order_views.py',
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"{file_path} - найден")
    else:
        print(f"{file_path} - НЕ НАЙДЕН")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')
django.setup()

from django.apps import apps

print("\n2. ПРОВЕРКА МОДЕЛЕЙ:")
print("-" * 40)

if apps.is_installed('backend'):
    print("Приложение backend зарегистрировано")
else:
    print("Приложение backend НЕ зарегистрировано")

from backend.models import User, Shop, Category, Product, ProductInfo, Parameter, Contact, Order

models_to_check = [User, Shop, Category, Product, ProductInfo, Parameter, Contact, Order]

for model in models_to_check:
    try:
        count = model.objects.count()
        print(f"Модель {model.__name__}: {count} записей")
    except Exception as e:
        print(f"Модель {model.__name__}: ошибка - {e}")

print("\n3. ПРОВЕРКА МИГРАЦИЙ:")
print("-" * 40)

from django.db.migrations.recorder import MigrationRecorder
migrations = MigrationRecorder.Migration.objects.filter(app='backend')
if migrations.exists():
    print(f"Миграции backend применены: {migrations.count()}")
else:
    print("Миграции backend не найдены")

print("\n" + "=" * 60)
print("ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 60)