import requests
import time
import os

def login(auth_url, username, password):
    """Авторизация"""
    payload = {
        "app": "CC",
        "app_version": "1.25.12.3",
        "username": username,
        "password": password
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(auth_url, headers=headers, json=payload)
        response.raise_for_status()

        token = response.json().get("auth_token")
        if token:
            print(f"✅ Успешная авторизация.")
            return token
        else:
            print("❌ Ошибка авторизации: токен не получен.")
            return None
    except requests.RequestException as e:
        print(f"❌ Ошибка авторизации: {e}")
        return None

def get_upload_token(get_token_url, token):
    """Получение токена загрузки"""
    try:
        response = requests.post(get_token_url, json={"app": "screen_record", "auth_token": token, "device_id": "blas"})
        response.raise_for_status()

        upload_token = response.json().get("app_token")
        if upload_token:
            print(f"✅ Токен загрузки получен.")
            return upload_token
        else:
            print("❌ Ошибка получения токена загрузки: токен не получен.")
            return None
    except requests.RequestException as e:
        print(f"❌ Ошибка получения токена загрузки: {e}")
        return None

def upload_video(upload_url, upload_token, file_path, max_attempts):
    """Загрузка видео"""
    headers = {'app-token': upload_token}
    success_count = 0

    if not os.path.exists(file_path):
        print(f"❌ Файл '{file_path}' не найден.")
        return False

    for attempt in range(max_attempts):
        try:
            with open(file_path, 'rb') as video_file:
                files = {
                    'start_date': (None, '1730120455408'),
                    'end_date': (None, '1730120459408'),
                    'file': (os.path.basename(file_path), video_file),
                    'schedule_id': (None, '404'),
                    'additional_info': (None, '[]'),
                }

                response = requests.post(upload_url, headers=headers, files=files)

                if response.status_code == 401:
                    print("❌ Ошибка авторизации (401). Повторный логин...")
                    return False  # Требуется повторная авторизация

                response.raise_for_status()  # Вызывает ошибку, если статус не 2xx

                success_count += 1
                print(f"✅ Файл успешно загружен ({success_count}/{max_attempts}).")

        except requests.RequestException as e:
            print(f"❌ Ошибка загрузки: {e}")
            return False
        except Exception as e:
            print(f"❌ Непредвиденная ошибка: {e}")
            return False

    return True

def main():
    auth_url = 'http://auth-prerelease-ru.by.mgo.su/auth/vpbx'
    get_token_url = 'http://screen-record-service-ccmo-4815-pres-ru.by.mgo.su/api/auth/get-app-token'
    upload_url = 'http://screen-record-service-ccmo-4815-pres-ru.by.mgo.su/api/screenrecord/upload'

    username = "300003463/romat"
    password = "Gw?x4?QHo8TS"
    max_upload_attempts = 1  # Количество попыток загрузки

    file_path = input("Введите путь к файлу для загрузки: ").strip()

    while True:
        print("\n=== 🔑 Авторизация ===")
        auth_token = login(auth_url, username, password)
        if not auth_token:
            print("❌ Ошибка авторизации, выход.")
            break

        upload_token = get_upload_token(get_token_url, auth_token)
        if not upload_token:
            print("❌ Ошибка получения токена загрузки, выход.")
            break

        print("\n=== 📤 Начало загрузки ===")
        if not upload_video(upload_url, upload_token, file_path, max_upload_attempts):
            print("🔄 Ошибка загрузки. Повторная авторизация...")
            continue

        print("✅ Файл успешно загружен!")
        break

if __name__ == "__main__":
    main()
