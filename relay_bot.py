import re
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telegram import Bot
from datetime import datetime

# ── CONFIGURAZIONE ──────────────────────────────────────
SESSION_STRING = "1BJWap1sBuxxBlgCdHYYngqVHtkPCQ7Bcc3ML-2IsYhdp0RnFbI8L4R8GtUmgCCjOaNriFHzCiM3NGvkVL-JBBd3IVKWzw9DpqpUhy6DNUDbOWzHbbsmGv2t8JGLOdiODMDVbnRbKLsD7PK0n5sF7gxffLXskC3cGonQJTcRZnpZXdT4EO0JuAzlFi3_V2Kcsk-pxIJ9cV1IIITXIOQIW86uJ6BgJkun4HmvpLM0brq7Qdxuf2oqtEkFWjsfwuS8hLfEajAIVw5h4rci8NoleK7LUdnaNPPUKmTjnHedZ5nl9U0Eq9DD3PMFmiGePHG1SYWhbKPHq0KuuWfJmof1U4pExwRgSj3Y="
API_ID        = 31137651
API_HASH      = "1831850405c78603de836ca168c6bfc7"
BOT_TOKEN     = "8450459959:AAFHOfuGK21O2HPtawwTGLxJca92VoGhbJw"
CHANNEL_OUT   = "@techprezzibassit"
AFFILIATE_TAG = "techprezzibas-21"
HOT_DISCOUNT  = 40

SOURCE_CHANNELS = [
    1415117147,
    1130941839,
    1063843030,
    1341651997,
    1279101491,
]
# ────────────────────────────────────────────────────────

already_sent = set()

# Righe da rimuovere
JUNK_PATTERNS = [
    r'.*aliensales\.it.*',
    r'.*come.si.usa.*coupon.*',
    r'.*[Ss]egnalata su.*',
    r'.*CosmoTech.*',
    r'.*disclaimer.*',
    r'.*\[#Ad.*',
    r'.*affiliat.*',
    r'.*t\.me/\+.*',
    r'.*ofclub\.click.*',
    r'.*Come si usa.*',
    r'.*per info.*',
    r'.*canale.*ufficiale.*',
]

def clean_text(text):
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        skip = False
        for pattern in JUNK_PATTERNS:
            if re.match(pattern, line, re.IGNORECASE):
                skip = True
                break
        if not skip:
            cleaned.append(line)
    result = re.sub(r'\n{3,}', '\n\n', '\n'.join(cleaned))
    return result.strip()

def extract_amazon_url(text):
    match = re.search(r'https?://(?:www\.)?amazon\.it/\S+', text)
    return match.group(0) if match else None

def add_affiliate(url):
    url = re.sub(r'[?&]tag=[^&\s]+', '', url)
    url = url.rstrip('?&')
    sep = '&' if '?' in url else '?'
    return f"{url}{sep}tag={AFFILIATE_TAG}"

def extract_prices(text):
    prices = re.findall(r'(\d+(?:[.,]\d+)?)\s*€|€\s*(\d+(?:[.,]\d+)?)', text)
    found = []
    for p in prices:
        val = p[0] or p[1]
        found.append(float(val.replace(',', '.')))
    return sorted(set(found))

def extract_discount(text):
    match = re.search(r'-\s*(\d+)\s*%|(\d+)\s*%\s*(?:di\s*)?sconto', text, re.IGNORECASE)
    if match:
        return int(match.group(1) or match.group(2))
    prices = extract_prices(text)
    if len(prices) >= 2:
        original = max(prices)
        current = min(prices)
        if original > current:
            return int(((original - current) / original) * 100)
    return 0

def extract_title(text):
    for line in text.split('\n'):
        line = line.strip()
        line = re.sub(r'[_*`]', '', line)
        if line and len(line) > 5 and not line.startswith('http'):
            return line
    return ""

def format_message(original_text, amazon_url):
    cleaned = clean_text(original_text)
    discount = extract_discount(cleaned)
    prices = extract_prices(cleaned)
    title = extract_title(cleaned)
    affiliate_url = add_affiliate(amazon_url)

    if discount >= HOT_DISCOUNT:
        header = f"🔥🔥 <b>OFFERTA BOMBA -{discount}%</b>"
    elif discount > 0:
        header = f"🔥 <b>Offerta -{discount}%</b>"
    else:
        header = "🛒 <b>Offerta Tech</b>"

    price_line = ""
    if len(prices) >= 2:
        current = min(prices)
        original = max(prices)
        price_line = f"\n💰 <b>{current:.2f}€</b>  <s>{original:.2f}€</s>"
    elif len(prices) == 1:
        price_line = f"\n💰 <b>{prices[0]:.2f}€</b>"

    title_line = f"\n\n🏷 {title}" if title else ""
    link_line = f"\n\n👉 <a href='{affiliate_url}'>Apri su Amazon</a>"
    footer = "\n\n#tech #offerta #amazon #elettronica"

    return header + price_line + title_line + link_line + footer

async def main():
    bot = Bot(token=BOT_TOKEN)
    client = TelegramClient(
        StringSession(SESSION_STRING),
        API_ID,
        API_HASH,
        catch_up=True
    )

    await client.start()
    client.flood_sleep_threshold = 60
    print("=" * 50)
    print("  Relay Bot v6 — formato pulito")
    print(f"  Monitorando {len(SOURCE_CHANNELS)} canali sorgente")
    print(f"  Soglia hot     : -{HOT_DISCOUNT}%")
    print("=" * 50)

    @client.on(events.NewMessage(chats=SOURCE_CHANNELS, incoming=True))
    async def handler(event):
        msg = event.message
        text = msg.text or ""

        if not text:
            return

        amazon_url = extract_amazon_url(text)
        if not amazon_url:
            print(f"[SKIP] Nessun link Amazon")
            return

        msg_id = f"{event.chat_id}_{msg.id}"
        if msg_id in already_sent:
            return

        formatted = format_message(text, amazon_url)

        try:
            await bot.send_message(
                chat_id=CHANNEL_OUT,
                text=formatted,
                parse_mode="HTML",
                disable_web_page_preview=False
            )
            already_sent.add(msg_id)
            discount = extract_discount(text)
            emoji = "🔥🔥" if discount >= HOT_DISCOUNT else "🔥"
            print(f"[INVIATO] {emoji} -{discount}% | {text[:50]}")
        except Exception as e:
            print(f"[ERRORE] {e}")

    print("In ascolto... (CTRL+C per fermare)")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
