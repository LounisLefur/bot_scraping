import requests
from bs4 import BeautifulSoup
import time
import telegram
import os
import random

# --- CONFIG ---
LECLERC_PRODUCTS = [
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
        "url": "https://www.e.leclerc/fp/pokemon-coffret-dresseur-d-elite-q2-2024-0820650558696",
        "max_price": 80.0,
        "silent": True
    },
    {
        "url": "https://www.e.leclerc/fp/pokemon-bundle-6-boosters-0196214106154?srsltid=AfmBOor8T7Dr1tY7BmJ2eT6cyFUui2mUD4wFHtjCooP22Hgb7wrxnMt0",
        "max_price": 50.0,
        "silent": False
    },
    {
        "url": "https://www.e.leclerc/fp/pokemon-portfolio-a4-9-pochettes-5-boosters-0196214105096",
        "max_price": 60.0,
        "silent": False
    },
    {
        "url": "https://www.e.leclerc/fp/pokemon-coffret-dresseur-d-elite-pokevx5eli-0196214105140",
        "max_price": 80.0,
        "silent": False
    },
    {
        "url": "https://www.e.leclerc/fp/pokemon-ev09-coffret-dresseur-d-elite-0196214108097",
        "max_price": 80.0,
        "silent": False
    },
    {
        "url": "https://www.e.leclerc/fp/pokemon-coffret-accessoires-5b-0196214106024",
        "max_price": 45.0,
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
        "max_price": 30.0,
        "silent": False
    },
    {
        "url": "https://www.e.leclerc/fp/pokemon-coffret-ex-mars-0196214106598",
        "max_price": 60.0,
        "silent": True
    },
]

JOUECLUB_PRODUCTS = [
    {
        "url": "https://www.joueclub.fr/pokemon/pokemon-coffret-accessoires-5-boosters-sac-de-rangement-0196214106024.html",
        "max_price": 50.0,
        "silent": False
    },
    {
        "url": "https://www.joueclub.fr/pokemon/pokemon-deck-de-combat-q2-0820650558207.html",
        "max_price": 50.0,
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

def get_price_and_stock_leclerc(url):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "fr-FR,fr;q=0.9"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    print("\n🔍 [Leclerc] URL testée :", url)

    stock = soup.find("p", class_="dXuIK p-small")
    print("📦 Bloc stock trouvé :", stock)
    in_stock = stock and "En stock" in stock.text

    try:
        euros_tag = soup.find("span", class_="vcEUR")
        cents_tag = soup.find("span", class_="bYgjT")
        euros = euros_tag.text.strip() if euros_tag else ""
        cents = cents_tag.text.strip() if cents_tag else "00"
        price = float(f"{euros}.{cents}") if euros and cents else None
        print("💶 Prix détecté :", euros, "euros et", cents, "centimes")
    except Exception as e:
        print("❌ Erreur lors de l'extraction du prix (Leclerc) :", e)
        price = None

    return in_stock, price

def get_price_and_stock_joueclub(url):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "fr-FR,fr;q=0.9"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    print("\n🔍 [JouéClub] URL testée :", url)

    availability_block = soup.find("div", class_="c-product-add-to-cart-block__avaibility")
    print("📦 Bloc disponibilité trouvé :", availability_block)
    in_stock = availability_block and "stock" in availability_block.text.lower()

    try:
        price_block = soup.find("strong", class_="scalapay-price") or soup.find("div", class_="scalapay-price")
        print("💶 Bloc prix trouvé :", price_block)
        price_text = price_block.text.strip().replace("\xa0€", "").replace("€", "").replace(",", ".") if price_block else ""
        price = float(price_text)
        print("💶 Prix détecté :", price)
    except Exception as e:
        print("❌ Erreur lors de l'extraction du prix (JouéClub) :", e)
        price = None

    return in_stock, price

def send_alert(price, url):
    message = f"🛒 Produit disponible à {price:.2f}€ !\n\n👉 {url}"
    for chat_id in CHAT_IDS:
        try:
            bot.send_message(chat_id=chat_id, text=message)
            print(f"📨 Notification envoyée à {chat_id}")
        except Exception as e:
            print(f"❌ Erreur d'envoi à {chat_id} :", e)

def run_bot():
    while True:
        for i in range(max(len(LECLERC_PRODUCTS), len(JOUECLUB_PRODUCTS))):
            if i < len(LECLERC_PRODUCTS):
                p = LECLERC_PRODUCTS[i]
                in_stock, price = get_price_and_stock_leclerc(p["url"])
                if in_stock and price is not None and price <= p["max_price"]:
                    print(f"✅ [Leclerc] Produit en stock à {price}€")
                    if not p.get("silent", False):
                        send_alert(price, p["url"])
                    else:
                        print("🔕 [Leclerc] Mode silencieux — pas de notification envoyée.")
                else:
                    print(f"❌ [Leclerc] Non conforme : en stock={in_stock}, prix={price}, max={p['max_price']}")

            if i < len(JOUECLUB_PRODUCTS):
                p = JOUECLUB_PRODUCTS[i]
                in_stock, price = get_price_and_stock_joueclub(p["url"])
                if in_stock and price is not None and price <= p["max_price"]:
                    print(f"✅ [JouéClub] Produit en stock à {price}€")
                    if not p.get("silent", False):
                        send_alert(price, p["url"])
                    else:
                        print("🔕 [JouéClub] Mode silencieux — pas de notification envoyée.")
                else:
                    print(f"❌ [JouéClub] Non conforme : en stock={in_stock}, prix={price}, max={p['max_price']}")

        wait = CHECK_INTERVAL + random.randint(5, 15)
        print(f"⏳ Attente de {wait} secondes...")
        time.sleep(wait)

if __name__ == "__main__":
    run_bot()
