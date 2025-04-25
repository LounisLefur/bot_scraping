import requests
from bs4 import BeautifulSoup
import asyncio
from telegram import Bot

# === Telegram ===
BOT_TOKEN = "7991436239:AAFjrOpbQtt1RCs0nxX1MNUU6ZpD1u2XfQw"
CHAT_IDS = ["6515900776", "8054802768"]
bot = Bot(token=BOT_TOKEN)

# === Produits ===
products = [
    {
        "name": "Bundle 6 Boosters Évolutions Prismatiques",
        "url": "https://www.cultura.com/p-bundle-6-boosters-evolutions-primastiques-pokemon-11841902.html",
        "max_price": 50,
        "unavailable_class": "stock color-red"
    },
    {
        "name": "Coffret Pochette Evoli Évolutions Prismatiques",
        "url": "https://www.cultura.com/p-coffret-pokemon-collection-speciale-pochette-a-accessoires-evoli-evolutions-prismatiques-11860027.html",
        "max_price": 50,
        "unavailable_class": None
    },
    {
        "name": "Coffret Premium Eaux Florissantes",
        "url": "https://www.cultura.com/p-coffret-12-boosters-pokemon-ecarlate-et-violet-collection-premium-eaux-florissantes-11860026.html",
        "max_price": 120,
        "unavailable_class": None
    }
]

def get_price_from_soup(soup):
    try:
        bloc = soup.select_one("div.price.price--big.color-bluedark")
        euros_raw = bloc.contents[0] if bloc else ""
        euros = ''.join(filter(str.isdigit, euros_raw)) if euros_raw else ""
        cents_tag = bloc.select_one("span.price__cents") if bloc else None
        cents = cents_tag.text.strip().replace("€", "").replace(",", "") if cents_tag else "00"

        if euros == "":
            return None  # prix invalide
        return float(f"{euros}.{cents}")
    except:
        return None

async def check_product(product):
    try:
        response = requests.get(product["url"], timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Vérifie si le produit est disponible
        if product["unavailable_class"]:
            unavailable_tag = soup.find("p", class_=product["unavailable_class"])
            is_available = unavailable_tag is None
        else:
            is_available = soup.select_one("button.addToCartPdp") is not None

        if not is_available:
            print(f"{product['name']} : ❌ Indisponible")
            return  # ne continue pas si indisponible

        # Récupère le prix
        price = get_price_from_soup(soup)
        if price is None:
            print(f"{product['name']} : Prix non détecté")
            return

        # Vérifie si le prix est dans la limite
        if price <= product["max_price"]:
            message = f"""📦 *{product['name']}*
✅ DISPONIBLE | 💰 {price:.2f}€ (sous {product['max_price']}€)
🔗 {product['url']}"""
            for chat_id in CHAT_IDS:
                await bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
            print(f"{product['name']} : ✅ Notification envoyée")
        else:
            print(f"{product['name']} : Prix {price:.2f}€ au-dessus de la limite ({product['max_price']}€)")

    except Exception as e:
        print(f"Erreur pour {product['name']}: {e}")

async def main_loop():
    while True:
        print("\n--- Nouvelle vérification ---")
        tasks = [check_product(p) for p in products]
        await asyncio.gather(*tasks)
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main_loop())
