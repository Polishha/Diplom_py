import requests
import json

base_url = "http://127.0.0.1:8000/api/v1"

print("=" * 50)
print("ТЕСТ ФУНКЦИЙ ПОСТАВЩИКА")
print("=" * 50)

print("\n1. Вход как поставщик...")
login_data = {
    "email": "shop@example.com",
    "password": "shop123"
}

response = requests.post(f"{base_url}/user/login", data=login_data)
print(f"Статус: {response.status_code}")

if response.status_code == 200:
    token = response.json()['Token']
    headers = {'Authorization': f'Token {token}'}
    print("Вход выполнен")
    
    print("\n2. Получение заказов магазина...")
    response = requests.get(f"{base_url}/orders", headers=headers)
    print(f"Статус: {response.status_code}")
    orders = response.json()
    print(f"Найдено заказов: {len(orders)}")
    
    if orders:
        print("\n3. Обновление статуса заказа...")
        order_id = orders[0]['id']
        print(f"Заказ #{order_id} можно отметить как 'Собран' через админку")