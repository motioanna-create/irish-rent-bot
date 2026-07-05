import os
import time
import re
import requests
from bs4 import BeautifulSoup

# Налаштування користувача
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = "1239840131"
MAX_PRICE = 1700
LOCATIONS = ["drogheda", "gormanston", "balbriggan", "swords", "dublin"]

# Список для збереження вже знайдених оголошень, щоб не спамити
seen_properties = set()

def send_telegram_message(text):
    if not TOKEN:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=data)

def check_rent_ie():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    for loc in LOCATIONS:
        try:
            # Формуємо посилання для пошуку (2+ спальні, до вказаної ціни)
            url = f"https://www.rent.ie/houses-to-let/renting_{loc}/2-beds/max_{MAX_PRICE}/"
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = soup.find_all('div', class_='search_result')
            
            for prop in search_results:
                link_tag = prop.find('a', href=True)
                if not link_tag:
                    continue
                    
                prop_url = link_tag['href']
                
                if prop_url not in seen_properties:
                    seen_properties.add(prop_url)
                    
                    text_content = prop.get_text()
                    price_match = re.search(r'€[\d,]+', text_content)
                    price = price_match.group(0) if price_match else f"до €{MAX_PRICE}"
                    
                    message = (
                        f"🏠 *Нове оголошення в {loc.capitalize()}!*\n"
                        f"💰 Ціна: {price}\n"
                        f"🔗 [Переглянути на Rent.ie]({prop_url})"
                    )
                    
                    send_telegram_message(message)
                    time.sleep(1)
                    
        except Exception as e:
            print(f"Помилка при перевірці {loc}: {e}")

if __name__ == "__main__":
    print("Бот успішно переналаштований на пошук житла!")
    send_telegram_message("🔍 Бот розпочав активний моніторинг оголошень кожні 2 хвилини.")
    
    check_rent_ie()
    print("Перша перевірка завершена. Моніторинг активовано.")
    
    while True:
        time.sleep(120)
        check_rent_ie()
