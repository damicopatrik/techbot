import re
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telegram import Bot
from datetime import datetime

# ── CONFIGURAZIONE ──────────────────────────────────────
SESSION_STRING = "1BJWap1sBuy_N9VInF2R8ghzJVJ5cpgPHSqmihOpDshsL_TIUJLr2NHyHCNWZ8xYjy-sePCK6q6srGoN88IZ6iSJHmigV2mRklOx3aqi0lCcYg_vzGKZbYAzgllCBMR36bnmNh9MnuUu6LPSR1n3b1ynwFywxo4k5GmqQrWxhDU983COLDCkXgMdXWFXvUndVEa6KBvp6GFOVs-wnU0zMGHYdUs-PXwFAJ3h9SuTNzd7O0tBSkCAFAXhA95C-nDE2UktozsFM3LKGCUnvdSrNbpdSjNhlGgjYViFKuN3ekU9pA0bFiw-kracgNfGkmIyAxK-U0Syv4XjaaweXfYn9q3L5HqRbLzI="
API_ID        = 31137651
API_HASH      = "1831850405c78603de836ca168c6bfc7"
BOT_TOKEN     = "8450459959:AAFHOfuGK21O2HPtawwTGLxJca92VoGhbJw"
CHANNEL_OUT   = "@techprezzibassit"
AFFILIATE_TAG = "techprezzibas-21"
HOT_DISCOUNT  = 40

SOURCE_CHANNELS = [
    "offerteitalia",
    "Offerte_Tech_IPhone_Pc_Cellulari",
    "ScontiTech",
    "offertepuntotech",
    "offertesmartworld",
]
# ────────────────────────────────────────────────────────

already_sent = set()

def replace_affiliate(text):
    text = re.sub(r'tag=[a-zA-Z0-9_-]+-\d+', f'tag={AFFILIATE_TAG}', text)
    def add_tag(match):
        url = match.group(0)
        if 'tag=' not in url:
            sep = '&' if '?' in url else '?'
            return f"{url}{sep}tag={AFFILIATE_TAG}"
        return url
    text = re.sub(r'https?://(?:www\.)?amazon\.it/\S+', add_tag, text)
    return text

def extract_discount(text):
    match = re.search(r'-\s*(\d+)\s*%|(\d+)\s*%\s*(?:di\s*)?sconto', text, re.IGNORECASE)
    if match:
        return int(match.group(1) or match.group(2))
    return 0

def has_amazon_link(text):
    return bool(re.search(r'amazon\.it', text, re.IGNORECASE))

def format_message(text, discount):
    if discount >= HOT_DISCOUNT:
        header = f"🔥🔥 OFFERTA BOMBA -{discount}%\n\n"
    elif discount > 0:
        header = f"🔥 Offerta -{discount}%\n\n"
    else:
        header = "🛒 Offerta tech\n\n"
    footer = "\n\n#tech #offerta #amazon #elettronica"
    return header + text + footer

async def main():
    bot = Bot(token=BOT_TOKEN)
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

    await client.start()
    print("=" * 50)
    print("  Relay Bot v3 — pubblica tutto")
    print(f"  Monitorando {len(SOURCE_CHANNELS)} canali sorgente")
    print(f"  Soglia hot     : -{HOT_DISCOUNT}% (doppia fiamma)")
    print("=" * 50)

    @client.on(events.NewMessage(chats=SOURCE_CHANNELS))
    async def handler(event):
        msg = event.message
        text = msg.text or ""

        if not text or not has_amazon_link(text):
            return

        msg_id = f"{event.chat_id}_{msg.id}"
        if msg_id in already_sent:
            return

        discount = extract_discount(text)
        new_text = replace_affiliate(text)
        formatted = format_message(new_text, discount)

        try:
            await bot.send_message(
                chat_id=CHANNEL_OUT,
                text=formatted,
                parse_mode="HTML",
                disable_web_page_preview=False
            )
            already_sent.add(msg_id)
            emoji = "🔥🔥" if discount >= HOT_DISCOUNT else "🔥"
            print(f"[{datetime.now().strftime('%H:%M')}] {emoji} | {text[:60]}")
        except Exception as e:
            print(f"Errore invio: {e}")

    print("In ascolto... (CTRL+C per fermare)")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
