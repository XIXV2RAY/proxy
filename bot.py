import os
import asyncio
import requests
import socket
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder

# ===== SECRETS =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

SUB_URL = "https://raw.githubusercontent.com/SoliSpirit/mtproto/refs/heads/master/all_proxies.txt"


# ===== LOAD =====
def load_proxies():
    try:
        r = requests.get(SUB_URL, timeout=10)
        return [x.strip() for x in r.text.splitlines() if "t.me/proxy" in x]
    except:
        return []


# ===== QUICK TEST =====
def is_alive(url):
    try:
        # استخراج server و port از لینک
        import re

        server = re.search(r"server=([^&]+)", url).group(1)
        port = int(re.search(r"port=([^&]+)", url).group(1))

        socket.create_connection((server, port), timeout=2).close()
        return True
    except:
        return False


# ===== FILTER LIVE =====
def get_live(proxies):
    live = []
    for p in proxies:
        if is_alive(p):
            live.append(p)
    return live


# ===== PICK 3 =====
def pick_three(proxies):
    return proxies[:3]


# ===== HORIZONTAL BUTTONS =====
def build_buttons(proxies):
    keyboard = []

    row = []
    for i, url in enumerate(proxies):
        row.append(InlineKeyboardButton(f"🔗 {i+1}", url=url))

    keyboard.append(row)  # همه تو یک ردیف

    return InlineKeyboardMarkup(keyboard)


# ===== MAIN =====
async def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    proxies = load_proxies()

    if not proxies:
        return

    live = get_live(proxies)

    if not live:
        return

    selected = pick_three(live)

    await app.bot.send_message(
        chat_id=CHANNEL_ID,
        text="🚀 پروکسی جدید",
        reply_markup=build_buttons(selected)
    )


if __name__ == "__main__":
    asyncio.run(run())
