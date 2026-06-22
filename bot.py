import os
import requests
import socket
from urllib.parse import quote
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder

# ===== ENV =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SUB_URL = os.getenv("SUB_URL")

PROXY_FILE = "proxies.txt"
INDEX_FILE = "index.txt"
LOG_FILE = "log.txt"


# ===== LOG =====
def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


# ===== LOAD SUB =====
def load_proxies():
    try:
        r = requests.get(SUB_URL, timeout=10)
        data = [x.strip() for x in r.text.splitlines() if x.strip()]
        log(f"[LOAD] total={len(data)}")
        return data
    except Exception as e:
        log(f"[ERROR LOAD] {e}")
        return []


# ===== TCP CHECK =====
def is_alive(proxy):
    try:
        ip, port, secret = proxy.split(":")
        socket.create_connection((ip, int(port)), timeout=2).close()
        return True
    except:
        return False


# ===== GET LIVE =====
def get_live(proxies):
    live = [p for p in proxies if is_alive(p)]
    log(f"[LIVE] total={len(live)}")
    return live


# ===== SAVE INDEX =====
def get_index():
    if not os.path.exists(INDEX_FILE):
        return 0
    return int(open(INDEX_FILE).read() or 0)


def save_index(i):
    with open(INDEX_FILE, "w") as f:
        f.write(str(i))


# ===== PICK 3 =====
def pick_3(proxies):
    index = get_index()
    selected = []

    for i in range(3):
        selected.append(proxies[(index + i) % len(proxies)])

    save_index((index + 3) % len(proxies))
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


# ===== MAIN =====
async def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    log("=== RUN START ===")

    proxies = load_proxies()
    if not proxies:
        log("NO PROXIES")
        return

    live = get_live(proxies)
    if not live:
        log("NO LIVE PROXIES")
        return

    selected = pick_3(live)

    text = "🚀 پروکسی جدید:\n\n" + "\n".join(selected)

    await app.bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        reply_markup=build_buttons(selected, text)
    )

    log(f"SENT {len(selected)} PROXIES")
    log("=== RUN END ===\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
