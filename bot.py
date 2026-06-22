import os
import asyncio
import requests
import socket
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

SUB_URL = "https://raw.githubusercontent.com/XIXV2RAY/XIXproxy/refs/heads/main/PROXY.txt"

USED_FILE = "used_proxies.txt"
AD_FILE = "ad.txt"


# ================= LOAD PROXIES =================
def load_proxies():
    try:
        r = requests.get(SUB_URL, timeout=10)
        return [x.strip() for x in r.text.splitlines() if "t.me/proxy" in x]
    except:
        return []


# ================= USED STORAGE =================
def load_used():
    try:
        with open(USED_FILE, "r", encoding="utf-8") as f:
            return set(x.strip() for x in f)
    except:
        return set()


def save_used(used):
    with open(USED_FILE, "w", encoding="utf-8") as f:
        for x in used:
            f.write(x + "\n")


# ================= AD =================
def load_ad():
    try:
        with open(AD_FILE, "r", encoding="utf-8") as f:
            lines = [x.strip() for x in f.readlines() if x.strip()]

        if len(lines) < 2:
            return None, None

        return lines[0], lines[1]
    except:
        return None, None


# ================= CHECK LIVE =================
def is_alive(url):
    try:
        import re

        server = re.search(r"server=([^&]+)", url).group(1)
        port = int(re.search(r"port=([^&]+)", url).group(1))

        socket.create_connection((server, port), timeout=1).close()
        return True
    except:
        return False


# ================= CHUNK =================
def chunks(lst, size=100):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]


# ================= FIND LIVE =================
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


# ================= PICK 3 =================
def pick_three(live):
    return live[:3]


# ================= BUTTONS =================
def build_buttons(proxies, ad_name=None, ad_link=None):
    keyboard = []

    # CONNECT ROW (افقی)
    row = [
        InlineKeyboardButton("Connect 🍓", url=p)
        for p in proxies
    ]
    keyboard.append(row)

    # AD BUTTON
    if ad_name and ad_link:
        keyboard.append([
            InlineKeyboardButton(ad_name, url=ad_link)
        ])

    return InlineKeyboardMarkup(keyboard)


# ================= MAIN =================
async def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    all_proxies = load_proxies()
    used = load_used()

    ad_name, ad_link = load_ad()

    if not all_proxies:
        return

    live = find_live(all_proxies, used)

    if not live:
        print("NO LIVE PROXIES")
        return

    selected = pick_three(live)

    # mark used
    for p in selected:
        used.add(p)

    save_used(used)

    await app.bot.send_message(
    chat_id=CHANNEL_ID,
    text="🚀 ⌯𝙉𝙚𝙬 𝙋𝙧𝙤𝙭𝙮⌯\n\n𝕗𝕠𝕣 𝕗𝕣𝕖𝕖𝕕𝕠𝕞",
    reply_markup=build_buttons(selected, ad_name, ad_link)
)


if __name__ == "__main__":
    asyncio.run(run())
