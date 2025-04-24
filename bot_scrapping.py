import requests
from bs4 import BeautifulSoup
import time
import telegram

# --- CONFIG ---
URL = "https://www.e.leclerc/fp/pokemon-coffret-de-rangement-4b-0196214105973"
MAX_PRICE = 45.0
CHECK_INTERVAL = 10  # secondes

# --- TELEGRAM ---
TELEGRAM_TOKEN = "7928937259:AAHP3Hew2l3ZuPzLPi9xq8Xh4Web3mbxc0k"  # 🔁 Remplace par ton vrai token
CHAT_IDS = ["8054802768", "6515900776"]            # 🔁 Remplace par ton vrai chat ID
bot = telegram.Bot(token=TELEGRAM_TOKEN)

def get_price_and_stock():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100 Safari/537.36"
    }
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # ✅ Vérifier si le produit est en stock
    stock = soup.find("p", class_="dXuIK p-small")
    in_stock = stock and "En stock" in stock.text

    # ✅ Extraire le prix
    try:
        euros = soup.find("span", class_="vcEUR").text.strip()
        cents = soup.find("span", class_="bYgjT").text.strip()
        price = float(f"{euros}.{cents}")
    except Exception as e:
        print("❌ Erreur lors de l'extraction du prix :", e)
        price = None

    return in_stock, price

def send_alert(price):
    message = f"🛒 Produit Leclerc disponible à {price:.2f}€ !\n\n👉 {URL}"
    bot.send_message(chat_id=CHAT_ID, text=message)

def run_bot():
    while True:
        print("🔍 Vérification du produit...")
        in_stock, price = get_price_and_stock()

        if in_stock and price is not None and price <= MAX_PRICE:
            print(f"✅ Produit en stock à {price}€")
            send_alert(price)
        else:
            print("❌ Pas de disponibilité ou prix trop élevé")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run_bot()
