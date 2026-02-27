import requests
import json

base_url = "http://127.0.0.1:8000/api/v1"

login_data = {
    "email": "shop@example.com",
    "password": "shop123"
}

print("Вход как поставщик...")
response = requests.post(f"{base_url}/user/login", data=login_data)

if response.status_code == 200:
    token = response.json()['Token']
    headers = {'Authorization': f'Token {token}'}
    
    files = {'file': open('shop_data.yaml', 'rb')}
    
    print("Загрузка товаров...")
    response = requests.post(
        f"{base_url}/partner/update", 
        headers=headers, 
        files=files
    )
    
    print(f"Статус: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    if response.status_code == 200:
        print("\nТовары успешно загружены!")
else:
    print("Ошибка входа")