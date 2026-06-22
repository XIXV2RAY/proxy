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


# ===== TEST PROXY (FAST) =====
def is_alive(url):
    try:
        import re

        server = re.search(r"server=([^&]+)", url).group(1)
        port = int(re.search(r"port=([^&]+)", url).group(1))

        socket.create_connection((server, port), timeout=1).close()
        return True
    except:
        return False


# ===== CHUNK 100 =====
def chunk_list(lst, size=100):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


# ===== PICK BEST 3 =====
def pick_best(live):
    return live[:3]


# ===== BUTTONS (ALL CONNECT) =====
def build_buttons(proxies):
    keyboard = []

    row = []
    for url in proxies:
        row.append(InlineKeyboardButton("Connect", url=url))

    keyboard.append(row)  # افقی

    return InlineKeyboardMarkup(keyboard)


# ===== FIND LIVE PROXIES =====
def find_live(proxies):
    for chunk in chunk_list(proxies, 100):

        live = []
        for p in chunk:
            if is_alive(p):
                live.append(p)

        if live:
            return live  # همون batch اول که جواب بده

    return []


# ===== MAIN =====
async def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    proxies = load_proxies()

    if not proxies:
        return

    live = find_live(proxies)

    if not live:
        print("NO LIVE PROXIES FOUND")
        return

    selected = pick_best(live)

    await app.bot.send_message(
        chat_id=CHANNEL_ID,
        text="🚀 پروکسی جدید",
        reply_markup=build_buttons(selected)
    )


if __name__ == "__main__":
    asyncio.run(run())
