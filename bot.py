import os
import asyncio
import requests
import socket
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder

# ===== ENV =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

SUB_URL = "https://raw.githubusercontent.com/SoliSpirit/mtproto/refs/heads/master/all_proxies.txt"

USED_FILE = "used_proxies.txt"


# ===== LOAD PROXIES =====
def load_proxies():
    try:
        r = requests.get(SUB_URL, timeout=10)
        return [x.strip() for x in r.text.splitlines() if "t.me/proxy" in x]
    except:
        return []


# ===== USED STORAGE =====
def load_used():
    try:
        with open(USED_FILE, "r") as f:
            return set(x.strip() for x in f)
    except:
        return set()


def save_used(used):
    with open(USED_FILE, "w") as f:
        for x in used:
            f.write(x + "\n")


# ===== LIGHT CHECK =====
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
def chunks(lst, size=100):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]


# ===== FIND LIVE IN BATCHES =====
def find_live(proxies, used):
    for batch in chunks(proxies, 100):

        live = []

        for p in batch:
            if p in used:
                continue

            if is_alive(p):
                live.append(p)

            if len(live) >= 10:
                break

        if live:
            return live

    return []


# ===== PICK 3 =====
def pick_three(live):
    return live[:3]


# ===== BUTTONS (HORIZONTAL) =====
def build_buttons(proxies):
    row = [
        InlineKeyboardButton("Connect🍓", url=p)
        for p in proxies
    ]
    return InlineKeyboardMarkup([row])


# ===== MAIN =====
async def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    all_proxies = load_proxies()
    used = load_used()

    if not all_proxies:
        return

    live = find_live(all_proxies, used)

    if not live:
        print("NO LIVE PROXIES FOUND")
        return

    selected = pick_three(live)

    # mark used
    for p in selected:
        used.add(p)

    save_used(used)

    await app.bot.send_message(
        chat_id=CHANNEL_ID,
        text="🚀 ⌯𝙉𝙚𝙬 𝙋𝙧𝙤𝙭𝙮⌯",
        reply_markup=build_buttons(selected)
    )


if __name__ == "__main__":
    asyncio.run(run())
