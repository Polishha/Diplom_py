import requests
import json

url = "http://127.0.0.1:8000/api/v1/user/register"
data = {
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "Тест",
    "last_name": "Тестов",
    "type": "buyer"
}

response = requests.post(url, data=data)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))