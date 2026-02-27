import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')
django.setup()

from django.apps import apps
from backend.models import (
    User, Shop, Category, Product, ProductInfo,
    Parameter, ProductParameter, Contact, Order, OrderItem, ConfirmEmailToken
)

def check_model(model_class):
    name = model_class.__name__
    try:
        count = model_class.objects.count()
        print(f"  {name}: {count} записей")
        return True
    except Exception as e:
        print(f"  {name}: Ошибка - {e}")
        return False

def main():
    print("=" * 60)
    print("ПРОВЕРКА ВСЕХ МОДЕЛЕЙ")
    print("=" * 60)
    
    models_to_check = [
        User, Shop, Category, Product, ProductInfo,
        Parameter, ProductParameter, Contact, Order, OrderItem, ConfirmEmailToken
    ]
    
    print("\nПроверка наличия таблиц и записей:")
    print("-" * 40)
    
    success_count = 0
    for model in models_to_check:
        if check_model(model):
            success_count += 1
    
    print("-" * 40)
    print(f"\nРезультат: {success_count}/{len(models_to_check)} моделей доступны")
    
    print("\n" + "=" * 60)
    print("ПРОВЕРКА СВЯЗЕЙ")
    print("=" * 60)
    
    shops = Shop.objects.all()
    print(f"\nМагазины ({shops.count()}):")
    for shop in shops:
        print(f"  - {shop.name} (user: {shop.user.email if shop.user else 'нет'})")
    
    categories = Category.objects.all()
    print(f"\nКатегории ({categories.count()}):")
    for cat in categories:
        shops_count = cat.shops.count()
        print(f"  - {cat.name} (магазинов: {shops_count})")
    
    products = Product.objects.all()
    print(f"\nТовары ({products.count()}):")
    for prod in products:
        print(f"  - {prod.name} (категория: {prod.category.name if prod.category else 'нет'})")
    
    product_infos = ProductInfo.objects.all()
    print(f"\nИнформация о товарах ({product_infos.count()}):")
    for pi in product_infos:
        print(f"  - {pi.product.name} в {pi.shop.name}: {pi.price} руб., {pi.quantity} шт.")

if __name__ == '__main__':
    main()