import requests
import json

base_url = "http://127.0.0.1:8000/api/v1"

print("=" * 50)
print("ТЕСТ ФИЛЬТРАЦИИ ТОВАРОВ")
print("=" * 50)

login_data = {
    "email": "buyer@example.com",
    "password": "buyer123"
}

response = requests.post(f"{base_url}/user/login", data=login_data)
token = response.json()['Token']
headers = {'Authorization': f'Token {token}'}

print("\n1. Все товары:")
response = requests.get(f"{base_url}/products", headers=headers)
print(f"Найдено: {len(response.json())}")

print("\n2. Товары категории 'Смартфоны' (category_id=1):")
response = requests.get(f"{base_url}/products?category_id=1", headers=headers)
print(f"Найдено: {len(response.json())}")

print("\n3. Товары дороже 50000:")
response = requests.get(f"{base_url}/products?price_min=50000", headers=headers)
print(f"Найдено: {len(response.json())}")

print("\n4. Поиск 'iPhone':")
response = requests.get(f"{base_url}/products?search=iPhone", headers=headers)
print(f"Найдено: {len(response.json())}")

print("\n5. Сортировка по убыванию цены:")
response = requests.get(f"{base_url}/products?ordering=-price", headers=headers)
products = response.json()
if products:
    print(f"Самый дорогой: {products[0]['product']['name']} - {products[0]['price']} руб.")