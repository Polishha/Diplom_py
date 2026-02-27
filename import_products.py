import requests
import json

login_url = "http://127.0.0.1:8000/api/v1/user/login"
login_data = {
    "email": "shop@example.com",
    "password": "shop123"
}

print("Вход в систему...")
response = requests.post(login_url, data=login_data)
print(f"Статус: {response.status_code}")

if response.status_code == 200:
    token = response.json()['Token']
    headers = {'Authorization': f'Token {token}'}
    
    import_url = "http://127.0.0.1:8000/api/v1/partner/update"
    import_data = {
        "url": "https://raw.githubusercontent.com/your-repo/shop_data.yaml"
    }
    
    response = requests.post(import_url, headers=headers, data=import_data)
    print(f"Импорт товаров: {response.status_code}")
    print(response.json())
else:
    print("Ошибка входа")