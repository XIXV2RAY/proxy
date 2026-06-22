import os
import requests
from urllib.parse import quote
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

PROXY_URL = "https://raw.githubusercontent.com/SoliSpirit/mtproto/refs/heads/master/all_proxies.txt"


# ===== LOAD PROXIES =====
def load_proxies():
    r = requests.get(PROXY_URL, timeout=10)
    lines = [x.strip() for x in r.text.splitlines() if x.strip()]
    return lines


# ===== PICK 3 =====
def pick_three(proxies):
    return proxies[:3]  # ساده و سریع


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

    proxies = load_proxies()

    if not proxies:
        return

    selected = pick_three(proxies)

    text = "🚀 پروکسی جدید:\n\n" + "\n".join(selected)

    await app.bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        reply_markup=build_buttons(selected, text)
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
