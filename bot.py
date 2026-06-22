import os
import requests
from urllib.parse import quote
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

SUB_URL = os.getenv("SUB_URL")


# ===== LOAD PROXIES FROM SUB =====
def load_proxies():
    try:
        r = requests.get(SUB_URL, timeout=10)
        lines = r.text.splitlines()

        proxies = []
        for x in lines:
            x = x.strip()
            if not x:
                continue
            if ":" not in x:
                continue
            proxies.append(x)

        return proxies

    except Exception as e:
        print("SUB ERROR:", e)
        return []


# ===== PICK 3 PROXIES =====
def pick_three(proxies):
    return proxies[:3]


# ===== BUILD INLINE BUTTONS =====
def build_buttons(proxies):
    keyboard = []

    for p in proxies:
        try:
            p = p.strip()
            parts = p.split(":")

            if len(parts) < 3:
                continue

            ip = parts[0].strip()
            port = parts[1].strip()
            secret = ":".join(parts[2:]).strip()

            url = f"https://t.me/proxy?server={ip}&port={port}&secret={secret}"

            keyboard.append([
                InlineKeyboardButton("🔗 اتصال پروکسی", url=url)
            ])

        except:
            continue

    return InlineKeyboardMarkup(keyboard)


# ===== MAIN =====
async def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    proxies = load_proxies()

    if not proxies:
        print("NO PROXIES FOUND")
        return

    selected = pick_three(proxies)

    text = "🚀 پروکسی جدید\n\n" + "\n".join(selected)

    await app.bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        reply_markup=build_buttons(selected)
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
