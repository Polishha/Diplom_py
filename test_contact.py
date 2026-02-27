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

contact_data = {
    "city": "Москва",
    "street": "Тверская",
    "house": "10",
    "apartment": "25",
    "phone": "+79991234567"
}

print("Создание контакта...")
response = requests.post(f"{base_url}/contacts", headers=headers, data=contact_data)
print(f"Статус: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

print("\nСписок контактов:")
response = requests.get(f"{base_url}/contacts", headers=headers)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))