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

# Загальна база знайдених оголошень
seen_properties = set()

def send_telegram_message(text):
    if not TOKEN:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=data, timeout=10)
    except Exception as e:
        print(f"Помилка надсилання в Telegram: {e}")

def check_rent_ie():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    for loc in LOCATIONS:
        try:
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
                        f"🏠 *Нове оголошення на Rent.ie!*\n"
                        f"📍 Локація: {loc.capitalize()}\n"
                        f"💰 Ціна: {price}\n"
                        f"🔗 [Переглянути оголошення]({prop_url})"
                    )
                    send_telegram_message(message)
                    time.sleep(1)
        except Exception as e:
            print(f"Помилка Rent.ie ({loc}): {e}")

def check_property_ie():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    for loc in LOCATIONS:
        try:
            # Формуємо лінк пошуку для Property.ie
            url = f"https://www.property.ie/property-to-let/{loc}/beds_2/price_unspecified-{MAX_PRICE}/"
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Шукаємо всі посилання на житло
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # Відсіюємо лише прямі лінки на об'єкти оренди
                if "/property-to-let/" in href and not any(x in href for x in ["beds_2", "price_unspecified", "page", "?"]):
                    if href not in seen_properties:
                        seen_properties.add(href)
                        
                        message = (
                            f"🏢 *Нове оголошення на Property.ie!*\n"
                            f"📍 Локація: {loc.capitalize()}\n"
                            f"💰 Бюджет: до €{MAX_PRICE}\n"
                            f"🔗 [Переглянути оголошення]({href})"
                        )
                        send_telegram_message(message)
                        time.sleep(1)
        except Exception as e:
            print(f"Помилка Property.ie ({loc}): {e}")

if __name__ == "__main__":
    print("Бот оновлений! Запуск подвійного моніторингу...")
    send_telegram_message("🚀 *Бот оновлено!* Тепер я одночасно шукаю житло на *Rent.ie* та *Property.ie* (покриття бази Daft) кожні 2 хвилини.")
    
    # Перше сканування для заповнення бази старими оголошеннями
    check_rent_ie()
    check_property_ie()
    print("Первинний збір даних завершено. Моніторинг активний.")
    
    # Цикл перевірки кожні 2 хвилини
    while True:
        time.sleep(120)
        check_rent_ie()
        check_property_ie()
