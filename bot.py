import os
import requests
import socket
from urllib.parse import quote
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

SUB_URL = os.getenv("SUB_URL")  # لینک ساب پروکسی

PROXY_FILE = "proxies.txt"
INDEX_FILE = "index.txt"


# ===== LOAD SUB =====
def load_proxies():
    try:
        r = requests.get(SUB_URL, timeout=10)
        data = r.text.splitlines()
        return [x.strip() for x in data if x.strip()]
    except:
        return []


# ===== SAVE =====
def save_proxies(proxies):
    with open(PROXY_FILE, "w") as f:
        f.write("\n".join(proxies))

    with open(INDEX_FILE, "w") as f:
        f.write("0")


# ===== INDEX =====
def get_index():
    if not os.path.exists(INDEX_FILE):
        return 0
    return int(open(INDEX_FILE).read())


def save_index(i):
    with open(INDEX_FILE, "w") as f:
        f.write(str(i))


# ===== QUICK TEST (TCP) =====
def is_alive(proxy):
    try:
        ip, port, secret = proxy.split(":")
        s = socket.create_connection((ip, int(port)), timeout=2)
        s.close()
        return True
    except:
        return False


# ===== GET NEXT VALID PROXIES =====
def get_next_proxies():
    if not os.path.exists(PROXY_FILE):
        return []

    with open(PROXY_FILE, "r") as f:
        proxies = [p.strip() for p in f if p.strip()]

    if not proxies:
        return []

    index = get_index()

    selected = []
    checked = 0

    while len(selected) < 3 and checked < len(proxies):
        p = proxies[(index + checked) % len(proxies)]
        if is_alive(p):
            selected.append(p)
        checked += 1

    save_index((index + checked) % len(proxies))

    return selected


# ===== BUTTONS =====
def build_buttons(proxies, text):
    keyboard = []

    for p in proxies:
        try:
            ip, port, secret = p.split(":")
            url = f"https://t.me/proxy?server={ip}&port={port}&secret={secret}"
            keyboard.append([InlineKeyboardButton("🔗 اتصال", url=url)])
        except:
            continue

    share_url = f"https://t.me/share/url?text={quote(text)}"
    keyboard.append([InlineKeyboardButton("📤 Share", url=share_url)])

    return InlineKeyboardMarkup(keyboard)


# ===== SEND =====
async def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    proxies = load_proxies()

    if not proxies:
        return

    save_proxies(proxies)

    live = get_next_proxies()

    if not live:
        return

    text = "🚀 پروکسی جدید:\n\n" + "\n".join(live)

    await app.bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        reply_markup=build_buttons(live, text)
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
