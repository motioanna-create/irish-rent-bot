import os
import time
import requests

# Налаштування бота
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = "1239840131"
MAX_PRICE = 1700
LOCATIONS = ["Drogheda", "Gormanston", "Balbriggan", "Swords", "Dublin"]
MIN_BEDROOMS = 2

def send_telegram_message(text):
    if not TOKEN:
        print("Помилка: Токен не знайдено!")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, json=data)

if __name__ == "__main__":
    print("Бот запускається...")
    send_telegram_message("✅ Привіт! Твій бот для пошуку житла успішно запущений і готовий до роботи 24/7.")
    
    # Тимчасовий цикл, щоб сервер не вимикав бота (пізніше тут буде код перевірки сайтів)
    while True:
        time.sleep(3600)
