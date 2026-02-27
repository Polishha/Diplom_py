import requests
import json

base_url = "http://127.0.0.1:8000/api/v1"

login_data = {
    "email": "buyer@example.com",
    "password": "buyer123"
}

print("1. Вход покупателя...")
response = requests.post(f"{base_url}/user/login", data=login_data)
token = response.json()['Token']
headers = {'Authorization': f'Token {token}'}
print("Успешно вошли")

print("\n2. Список товаров:")
response = requests.get(f"{base_url}/products", headers=headers)
products = response.json()
print(f"Найдено товаров: {len(products)}")

if len(products) > 0:
    print("\n3. Добавляем товар в корзину...")
    cart_data = {
        "items": [
            {
                "product_info_id": products[0]['id'],
                "quantity": 2
            }
        ]
    }
    response = requests.post(f"{base_url}/basket", headers=headers, json=cart_data)
    print(response.json())
    
    print("\n4. Содержимое корзины:")
    response = requests.get(f"{base_url}/basket", headers=headers)
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))