import os
import asyncio
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder

# ===== SECRETS =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# ===== SUB URL =====
SUB_URL = "https://raw.githubusercontent.com/SoliSpirit/mtproto/refs/heads/master/all_proxies.txt"


# ===== LOAD PROXIES =====
def load_proxies():
    try:
        r = requests.get(SUB_URL, timeout=10)
        lines = r.text.splitlines()

        # فقط لینک‌های کامل proxy
        return [x.strip() for x in lines if "t.me/proxy" in x]

    except Exception as e:
        print("SUB ERROR:", e)
        return []


# ===== PICK 3 =====
def pick_three(proxies):
    return proxies[:3]


# ===== BUILD BUTTONS =====
def build_buttons(proxies):
    keyboard = []

    for url in proxies:
        keyboard.append([
            InlineKeyboardButton("🔗 اتصال پروکسی", url=url)
        ])

    return InlineKeyboardMarkup(keyboard)


# ===== MAIN =====
async def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    proxies = load_proxies()

    if not proxies:
        print("NO PROXIES")
        return

    selected = pick_three(proxies)

    await app.bot.send_message(
        chat_id=CHANNEL_ID,
        text="🚀 پروکسی جدید",
        reply_markup=build_buttons(selected)
    )


if __name__ == "__main__":
    asyncio.run(run())
