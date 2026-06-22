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
    return [x.strip() for x in r.text.splitlines() if x.strip()]


# ===== PICK 3 PROXIES =====
def pick_three(proxies):
    return proxies[:3]


# ===== BUILD INLINE BUTTONS =====
def build_buttons(proxies, text):
    keyboard = []

    # هر پروکسی = یک دکمه شیشه‌ای
    for p in proxies:
        try:
            ip, port, secret = p.split(":")
            url = f"https://t.me/proxy?server={ip}&port={port}&secret={secret}"
            keyboard.append([
                InlineKeyboardButton("🔗 اتصال پروکسی", url=url)
            ])
        except:
            continue

    # دکمه Share واقعی
    share_url = f"https://t.me/share/url?text={quote(text)}"
    keyboard.append([
        InlineKeyboardButton("📤 Share", url=share_url)
    ])

    return InlineKeyboardMarkup(keyboard)


# ===== MAIN RUN =====
async def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    proxies = load_proxies()

    if not proxies:
        return

    selected = pick_three(proxies)

    # متن پیام
    text = "🚀 پروکسی جدید"

    # ارسال پیام با دکمه‌ها
    await app.bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        reply_markup=build_buttons(selected, text)
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
