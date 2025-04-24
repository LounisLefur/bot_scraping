import requests
from bs4 import BeautifulSoup
import time
import telegram
import os
import random

# --- CONFIG ---
PRODUCTS = [
    {
        "url": "https://www.e.leclerc/fp/pokemon-coffret-de-rangement-4b-0196214105973",
        "max_price": 45.0
    },
    {
        "url": "https://www.e.leclerc/fp/pokemon-mini-tin-2-booster-0820650550744",
        "max_price": 50.0
    }
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

    print("\n🔍 URL testée :", url)
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
            print("\n🔁 Vérification du produit :", url)
            in_stock, price = get_price_and_stock(url)

            if in_stock and price is not None and price <= max_price:
                print(f"✅ Produit en stock à {price}€, envoi de la notification...")
                send_alert(price, url)
            else:
                print(f"❌ Produit non conforme : en stock={in_stock}, prix={price}, limite={max_price}€")

        wait = CHECK_INTERVAL + random.randint(5, 15)  # anti-ban delay
        print(f"⏳ Attente de {wait} secondes avant prochaine vérification...")
        time.sleep(wait)

if __name__ == "__main__":
    run_bot()
