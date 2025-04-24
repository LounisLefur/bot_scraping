import requests
from bs4 import BeautifulSoup
import time
import telegram
import os
import random

# --- CONFIG ---
URL = "https://www.e.leclerc/fp/pokemon-coffret-de-rangement-4b-0196214105973"
MAX_PRICE = 45.0
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

def get_price_and_stock():
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "fr-FR,fr;q=0.9"
    }
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    print("\n🔍 HTML reçu (extrait) :")
    print(response.text[:1000])  # Affiche les 1000 premiers caractères du HTML

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

def send_alert(price):
    message = f"🛒 Produit Leclerc disponible à {price:.2f}€ !\n\n👉 {URL}"
    for chat_id in CHAT_IDS:
        try:
            bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"❌ Erreur d'envoi à {chat_id} :", e)

def run_bot():
    while True:
        print("\n🔍 Vérification du produit...")
        in_stock, price = get_price_and_stock()

        if in_stock and price is not None and price <= MAX_PRICE:
            print(f"✅ Produit en stock à {price}€")
            send_alert(price)
        else:
            print("❌ Pas de disponibilité ou prix trop élevé")

        wait = CHECK_INTERVAL + random.randint(5, 15)  # anti-ban delay
        time.sleep(wait)

if __name__ == "__main__":
    run_bot()
