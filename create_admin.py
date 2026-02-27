import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')

django.setup()

from backend.models import User

def create_admin():
    print("Проверяем наличие суперпользователя...")
    
    if User.objects.filter(email='admin@example.com').exists():
        admin = User.objects.get(email='admin@example.com')
        print("Пользователь admin@example.com уже существует:")
        print(f"  Email: {admin.email}")
        print(f"  Имя: {admin.first_name} {admin.last_name}")
        print(f"  Активен: {admin.is_active}")
        print(f"  Суперпользователь: {admin.is_superuser}")
        
        if not admin.is_superuser or not admin.is_active:
            admin.is_superuser = True
            admin.is_staff = True
            admin.is_active = True
            admin.save()
            print("Права пользователя обновлены до суперпользователя")
        return True
    
    try:
        print("Создаем нового суперпользователя...")
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        admin.is_active = True
        admin.save()
        print("Суперпользователь успешно создан!")
        print(f"  Email: admin@example.com")
        print(f"  Пароль: admin123")
        print(f"  Имя: Admin User")
        return True
    except Exception as e:
        print(f"Ошибка при создании: {e}")
        return False

def check_database():
    try:
        count = User.objects.count()
        print(f"Всего пользователей в базе: {count}")
        return True
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("СОЗДАНИЕ СУПЕРПОЛЬЗОВАТЕЛЯ DJANGO")
    print("=" * 60)
    
    if check_database():
        if create_admin():
            print("\n" + "=" * 60)
            print("Скрипт выполнен успешно!")
            print("=" * 60)
            print("\nТеперь вы можете войти в админку:")
            print("  URL: http://127.0.0.1:8000/admin/")
            print("  Email: admin@example.com")
            print("  Пароль: admin123")
        else:
            print("\nНе удалось создать суперпользователя")
    else:
        print("\nПроблема с подключением к базе данных")
        print("Сначала выполните миграции:")
        print("  python manage.py migrate")