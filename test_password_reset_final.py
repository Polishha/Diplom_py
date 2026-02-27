import requests
import json
import time

base_url = "http://127.0.0.1:8000/api/v1"

print("=" * 50)
print("ТЕСТ ВОССТАНОВЛЕНИЯ ПАРОЛЯ")
print("=" * 50)

print("\n1. Отправляем запрос на сброс пароля...")
reset_data = {
    "email": "buyer@example.com"
}

response = requests.post(f"{base_url}/password/reset", data=reset_data)
print(f"Статус: {response.status_code}")
print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if response.status_code == 200:
    print("\nЗапрос отправлен!")
    print("Проверьте консоль сервера - там должно быть письмо с токеном")
    print("\nСкопируйте токен из консоли сервера")
    
    token = input("\nВставьте токен из письма: ")
    
    print("\n2. Подтверждаем сброс пароля...")
    confirm_data = {
        "token": token,
        "password": "newpassword123"
    }
    
    response = requests.post(f"{base_url}/password/reset/confirm", data=confirm_data)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("\nПароль успешно изменен!")
        
        print("\n3. Проверяем вход с новым паролем...")
        login_data = {
            "email": "buyer@example.com",
            "password": "newpassword123"
        }
        response = requests.post(f"{base_url}/user/login", data=login_data)
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            print("Вход выполнен успешно!")
            print(f"Token: {response.json()['Token'][:20]}...")