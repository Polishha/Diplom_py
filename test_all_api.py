import requests
import json

base_url = "http://127.0.0.1:8000/api/v1"

print("=" * 60)
print("ТЕСТИРОВАНИЕ API")
print("=" * 60)

print("\n1. Регистрация пользователя:")
register_data = {
    "email": "user@example.com",
    "password": "password123",
    "first_name": "Иван",
    "last_name": "Иванов",
    "type": "buyer"
}
response = requests.post(f"{base_url}/user/register", data=register_data)
print(f"Статус: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

print("\n2. Вход в систему:")
login_data = {
    "email": "user@example.com",
    "password": "password123"
}
response = requests.post(f"{base_url}/user/login", data=login_data)
print(f"Статус: {response.status_code}")
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))

if response.status_code == 200:
    token = result['Token']
    headers = {'Authorization': f'Token {token}'}
    
    print("\n3. Список категорий:")
    response = requests.get(f"{base_url}/categories", headers=headers)
    print(f"Статус: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    print("\n4. Список товаров:")
    response = requests.get(f"{base_url}/products", headers=headers)
    print(f"Статус: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    print("\n5. Создание контакта:")
    contact_data = {
        "city": "Москва",
        "street": "Ленина",
        "house": "10",
        "apartment": "5",
        "phone": "+79991234567"
    }
    response = requests.post(f"{base_url}/contacts", headers=headers, data=contact_data)
    print(f"Статус: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))