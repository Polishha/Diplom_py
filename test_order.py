import requests
import json

base_url = "http://127.0.0.1:8000/api/v1"

login_data = {
    "email": "buyer@example.com",
    "password": "buyer123"
}

response = requests.post(f"{base_url}/user/login", data=login_data)
token = response.json()['Token']
headers = {'Authorization': f'Token {token}'}

print("1. Добавляем товар в корзину...")
products_response = requests.get(f"{base_url}/products", headers=headers)
products = products_response.json()

if len(products) > 0:
    cart_data = {
        "items": [
            {
                "product_info_id": products[0]['id'],
                "quantity": 1
            }
        ]
    }
    requests.post(f"{base_url}/basket", headers=headers, json=cart_data)
    
    print("2. Получаем корзину...")
    cart_response = requests.get(f"{base_url}/basket", headers=headers)
    cart = cart_response.json()
    print(f"Корзина ID: {cart.get('id')}")
    
    contacts_response = requests.get(f"{base_url}/contacts", headers=headers)
    contacts = contacts_response.json()
    
    if contacts and cart.get('id'):
        print("3. Подтверждаем заказ...")
        order_data = {
            "order_id": cart['id'],
            "contact_id": contacts[0]['id']
        }
        response = requests.post(f"{base_url}/orders/confirm", headers=headers, data=order_data)
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        print("\n4. Список заказов:")
        response = requests.get(f"{base_url}/orders", headers=headers)
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))