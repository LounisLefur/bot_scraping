import requests
from bs4 import BeautifulSoup
import time
import telegram
import os

# --- CONFIG ---
URL = "https://www.e.leclerc/fp/pokemon-coffret-de-rangement-4b-0196214105973"
MAX_PRICE = 45.0
CHECK_INTERVAL = 10  # secondes

# --- TELEGRAM ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_IDS = os.environ.get("CHAT_IDS", "").split(",")
bot = telegram.Bot(token=TELEGRAM_TOKEN)

def get_price_and_stock():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100 Safari/537.36"
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
        cents = cents_tag.text.strip() if cents_tag else ""
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

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run_bot()
