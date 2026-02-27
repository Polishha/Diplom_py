import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')

django.setup()

from django.contrib.auth import get_user_model
from backend.models import User

def main():
    print("=" * 50)
    print("ПРОВЕРКА МОДЕЛИ USER")
    print("=" * 50)
    
    UserModel = get_user_model()
    print(f"Модель пользователя: {UserModel.__name__}")
    print(f"Таблица в БД: {UserModel._meta.db_table}")
    print(f"Приложение: {UserModel._meta.app_label}")
    
    print("\nПоля модели:")
    for field in UserModel._meta.fields:
        print(f"  - {field.name}: {field.get_internal_type()}")
    
    print(f"\nКоличество пользователей: {UserModel.objects.count()}")
    
    if UserModel.objects.count() > 0:
        print("\nСписок пользователей:")
        for user in UserModel.objects.all():
            print(f"  ID: {user.id}, Email: {user.email}, Активен: {user.is_active}, Тип: {getattr(user, 'type', 'не указан')}")
    
    superusers = UserModel.objects.filter(is_superuser=True)
    print(f"\nСуперпользователей: {superusers.count()}")
    
    try:
        admin = UserModel.objects.get(email='admin@example.com')
        print(f"\nПользователь admin@example.com найден!")
        print(f"  ID: {admin.id}")
        print(f"  Активен: {admin.is_active}")
        print(f"  Суперпользователь: {admin.is_superuser}")
        print(f"  Персонал: {admin.is_staff}")
    except UserModel.DoesNotExist:
        print("\nПользователь admin@example.com не найден")
        
        print("\nСоздаем суперпользователя...")
        try:
            admin = UserModel.objects.create_superuser(
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            admin.is_active = True
            admin.save()
            print(f"Суперпользователь создан!")
        except Exception as e:
            print(f"Ошибка при создании: {e}")

if __name__ == '__main__':
    main()