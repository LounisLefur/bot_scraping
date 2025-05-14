import requests
from bs4 import BeautifulSoup
import time
import telegram
import os
import random
from datetime import datetime
import pytz

# --- CONFIG ---
PRODUCTS = [
    {
        "url": "https://www.e.leclerc/fp/pokemon-coffret-de-rangement-4b-0196214105973",
        "max_price": 45.0,
        "silent": False
    },
    {
        "url": "https://www.e.leclerc/fp/pokemon-mini-tin-2-booster-0820650550744",
        "max_price": 20.0,
        "silent": False
    },
    {
        "url": "https://www.e.leclerc/fp/pokemon-coffret-dresseur-d-elite-pokevx5eli-0196214105140",
        "max_price": 80.0,
        "silent": False
    },
    {
        "url": "https://www.e.leclerc/fp/pokemon-bundle-6-boosters-0820650556425",
        "max_price": 50.0,
        "silent": False
    },
    {
        "url": "https://www.e.leclerc/fp/pokemon-coffret-accessoires-5b-0196214106024",
        "max_price": 55.0,
        "silent": False
    },
    {
        "url": "https://www.e.leclerc/fp/pokemon-tech-sticker-3-pack-blister-0196214105249",
        "max_price": 30.0,
        "silent": False
    },
    {
        "url": "https://www.e.leclerc/fp/pokemon-mini-tin-0196214105560?srsltid=AfmBOorSuqG5mXuj-cMO7oqRKa0oVZig00JEptbtVCqgm9XSxhcxgt6N",
        "max_price": 20.0,
        "silent": False
    },
    {
        "url": "https://www.e.leclerc/fp/pokemon-coffret-poster-0196214105423?srsltid=AfmBOorHdPJC3WylpiPQJBMEVtjYHwlnnfMUwUxoz5m3MaDSr3Ssp5OI",
        "max_price": 35.0,
        "silent": False
    },
    {
        "url": "https://www.e.leclerc/fp/pokemon-bundle-6-boosters-0196214106154",
        "max_price": 90.0,
        "silent": False
    },
]

CHECK_INTERVAL = 60  # secondes (augmente pour limiter les blocages)

# --- TELEGRAM ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_IDS = os.environ.get("CHAT_IDS", "").split(",")
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Liste de User-Agents pour simuler différents navigateurs
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
]

def get_price_and_stock(url):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "fr-FR,fr;q=0.9"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Heure actuelle en France
    now = datetime.now(pytz.timezone("Europe/Paris")).strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n⏰ [{now}] Vérification de l'URL : {url}")
    print("🔍 HTML reçu (extrait) :", response.text[:1000])

    # ✅ Vérifier si le produit est en stock
    stock = soup.find("p", class_="dXuIK p-small")
    print("📦 Bloc stock trouvé :", stock)
    in_stock = stock and "En stock" in stock.text

    # ✅ Extraire le prix
    try:
        euros_tag = soup.find("span", class_="vcEUR")
        cents_tag = soup.find("span", class_="bYgjT")
        euros = euros_tag.text.strip() if euros_tag else ""
        cents = cents_tag.text.strip() if cents_tag else "00"
        print("💶 Prix détecté :", euros, "euros et", cents, "centimes")
        price = float(f"{euros}.{cents}") if euros and cents else None
    except Exception as e:
        print("❌ Erreur lors de l'extraction du prix :", e)
        price = None

    return in_stock, price

def send_alert(price, url):
    message = f"🛒 Produit Leclerc disponible à {price:.2f}€ !\n\n👉 {url}"
    for chat_id in CHAT_IDS:
        try:
            bot.send_message(chat_id=chat_id, text=message)
            print(f"📨 Notification envoyée à {chat_id}")
        except Exception as e:
            print(f"❌ Erreur d'envoi à {chat_id} :", e)

def run_bot():
    while True:
        for product in PRODUCTS:
            url = product["url"]
            max_price = product["max_price"]
            silent = product.get("silent", False)

            in_stock, price = get_price_and_stock(url)

            if in_stock and price is not None and price <= max_price:
                print(f"✅ Produit en stock à {price}€, envoi de la notification...")
                if not silent:
                    send_alert(price, url)
                else:
                    print("🔕 Mode silencieux activé pour ce produit — pas de notification envoyée.")
            else:
                print(f"❌ Produit non conforme : en stock={in_stock}, prix={price}, limite={max_price}€")

        wait = CHECK_INTERVAL + random.randint(5, 15)  # anti-ban delay
        print(f"⏳ Attente de {wait} secondes avant prochaine vérification...")
        time.sleep(wait)

if __name__ == "__main__":
    run_bot()
