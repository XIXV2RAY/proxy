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

USED_FILE = "used_proxies.txt"


# ===== LOAD ALL =====
def load_proxies():
    try:
        r = requests.get(SUB_URL, timeout=10)
        return [x.strip() for x in r.text.splitlines() if "t.me/proxy" in x]
    except:
        return []


# ===== LOAD USED =====
def load_used():
    if not os.path.exists(USED_FILE):
        return set()

    with open(USED_FILE, "r", encoding="utf-8") as f:
        return set(x.strip() for x in f if x.strip())


# ===== SAVE USED =====
def save_used(used):
    with open(USED_FILE, "w", encoding="utf-8") as f:
        for x in used:
            f.write(x + "\n")


# ===== CHECK LIVE =====
def is_alive(url):
    try:
        import re

        server = re.search(r"server=([^&]+)", url).group(1)
        port = int(re.search(r"port=([^&]+)", url).group(1))

        socket.create_connection((server, port), timeout=1).close()
        return True
    except:
        return False


# ===== FIND NEW PROXIES =====
def get_new_proxies(all_proxies, used):
    return [p for p in all_proxies if p not in used]


# ===== PICK LIVE =====
def find_live(proxies, used):
    live = []

    for p in proxies:
        if p in used:
            continue

        if is_alive(p):
            live.append(p)

        if len(live) >= 10:  # برای سرعت
            break

    return live


# ===== PICK 3 =====
def pick_three(live):
    return live[:3]


# ===== BUTTONS (HORIZONTAL) =====
def build_buttons(proxies):
    keyboard = []

    row = []
    for url in proxies:
        row.append(InlineKeyboardButton("Connect", url=url))

    keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


# ===== MAIN =====
async def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    all_proxies = load_proxies()
    used = load_used()

    if not all_proxies:
        return

    new_proxies = get_new_proxies(all_proxies, used)

    live = find_live(new_proxies, used)

    if not live:
        print("NO NEW LIVE PROXIES")
        return

    selected = pick_three(live)

    # mark as used
    for p in selected:
        used.add(p)

    save_used(used)

    await app.bot.send_message(
        chat_id=CHANNEL_ID,
        text="🚀 پروکسی جدید",
        reply_markup=build_buttons(selected)
    )


if __name__ == "__main__":
    asyncio.run(run())
