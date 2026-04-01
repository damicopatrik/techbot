import requests
import schedule
import time
import re
import asyncio
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime

# ── CONFIGURAZIONE ──────────────────────────────────────
BOT_TOKEN      = "8450459959:AAFHOfuGK21O2HPtawwTGLxJca92VoGhbJw"
CHANNEL_ID     = "@techprezzibassit"
AFFILIATE_TAG  = "techprezzibas-21"
MIN_DISCOUNT   = 20    # pubblica da qui in su
HOT_DISCOUNT   = 40    # doppia fiamma da qui in su
CHECK_INTERVAL = 30    # minuti tra controlli
MAX_PER_CYCLE  = 3     # massimo post per ciclo
# ────────────────────────────────────────────────────────

# Feed offerte reali con prezzi e sconti
FEED_URLS = [
    "https://www.offerte.it/feed/?cat=elettronica",
    "https://www.hwupgrade.it/news/offerteflash/index.xml",
    "https://www.amazon.it/rss/deals/electronics",
]

already_sent = set()

def add_affiliate(url):
    if "amazon" in url:
        url = re.sub(r'tag=[^&]+', '', url)
        url = re.sub(r'[?&]$', '', url)
        sep = '&' if '?' in url else '?'
        return f"{url}{sep}tag={AFFILIATE_TAG}"
    return url

def extract_prices(text):
    """Estrae prezzi originale e scontato dal testo dell'offerta."""
    prices = re.findall(r'(\d+[.,]\d{2})\s*€|€\s*(\d+[.,]\d{2})', text)
    found = []
    for p in prices:
        val = p[0] or p[1]
        found.append(float(val.replace(',', '.')))
    return found

def calc_discount(prices):
    if len(prices) >= 2:
        original = max(prices)
        current  = min(prices)
        if original > current:
            return int(((original - current) / original) * 100), original, current
    return 0, None, None

def fetch_deals():
    deals = []
    for feed_url in FEED_URLS:
        try:
            r = requests.get(feed_url, timeout=10,
                headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.content, "xml")
            items = soup.find_all("item")

            for item in items[:30]:
                title       = item.find("title")
                link        = item.find("link")
                description = item.find("description") or item.find("summary")

                if not title or not link:
                    continue

                desc_text = description.text if description else ""
                full_text = title.text + " " + desc_text
                prices    = extract_prices(full_text)
                discount, original, current = calc_discount(prices)

                if discount < MIN_DISCOUNT:
                    continue

                url = add_affiliate(link.text.strip())
                item_id = link.text.strip()

                if item_id in already_sent:
                    continue

                deals.append({
                    "title":    title.text.strip(),
                    "url":      url,
                    "id":       item_id,
                    "discount": discount,
                    "original": original,
                    "current":  current,
                })

        except Exception as e:
            print(f"Errore feed {feed_url}: {e}")

    # ordina per sconto decrescente
    deals.sort(key=lambda x: x["discount"], reverse=True)
    return deals

def format_message(deal):
    d = deal["discount"]

    # doppia soglia 🔥
    if d >= HOT_DISCOUNT:
        emoji = "🔥🔥"
        label = f"OFFERTA BOMBA -{d}%"
    else:
        emoji = "🔥"
        label = f"Offerta -{d}%"

    # riga prezzo
    if deal["original"] and deal["current"]:
        price_line = (
            f"~~€{deal['original']:.2f}~~ → "
            f"€{deal['current']:.2f}"
        )
    else:
        price_line = ""

    msg = (
        f"{emoji} {label}\n\n"
        f"{deal['title']}\n"
    )
    if price_line:
        msg += f"\n{price_line}\n"

    msg += (
        f"\n🛒 Vedi su Amazon\n\n"
        f"#tech #offerta #amazon #elettronica"
    )
    return msg

async def send_deal(deal):
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=format_message(deal),
        parse_mode="HTML",
        disable_web_page_preview=False
    )
    emoji = "🔥🔥" if deal["discount"] >= HOT_DISCOUNT else "🔥"
    print(f"[{datetime.now().strftime('%H:%M')}] {emoji} -{deal['discount']}% | {deal['title'][:45]}")

async def check_and_post():
    print(f"\n[{datetime.now().strftime('%H:%M')}] Controllo offerte...")
    deals = fetch_deals()

    if not deals:
        print("Nessuna offerta sopra la soglia minima.")
        return

    sent = 0
    for deal in deals:
        if sent >= MAX_PER_CYCLE:
            break
        if deal["id"] not in already_sent:
            await send_deal(deal)
            already_sent.add(deal["id"])
            sent += 1
            await asyncio.sleep(8)

    print(f"Pubblicati {sent} deal questo ciclo.")

def run_bot():
    print("=" * 50)
    print("  TechPrezziBassit Bot — avviato")
    print(f"  Soglia minima : -{MIN_DISCOUNT}%")
    print(f"  Soglia hot    : -{HOT_DISCOUNT}% (doppia fiamma)")
    print(f"  Ciclo ogni    : {CHECK_INTERVAL} min")
    print("=" * 50)

    asyncio.run(check_and_post())

    schedule.every(CHECK_INTERVAL).minutes.do(
        lambda: asyncio.run(check_and_post())
    )
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_bot()
