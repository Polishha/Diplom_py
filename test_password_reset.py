import requests
import json

base_url = "http://127.0.0.1:8000/api/v1"

print("=" * 50)
print("ТЕСТ ВОССТАНОВЛЕНИЯ ПАРОЛЯ")
print("=" * 50)

print("\n1. Запрос на сброс пароля:")
reset_data = {
    "email": "buyer@example.com"  
}

response = requests.post(f"{base_url}/password/reset", data=reset_data)
print(f"Статус: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

if response.status_code == 200:
    print("\nПисьмо отправлено! Проверьте консоль сервера.")
    print("\nВ консоли сервера вы увидите токен. Скопируйте его.")
    