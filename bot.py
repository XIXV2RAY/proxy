import os
from urllib.parse import quote
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = os.getenv("CHANNEL_ID")

PROXY_FILE = "proxies.txt"
INDEX_FILE = "index.txt"


def get_index():
    if not os.path.exists(INDEX_FILE):
        return 0
    with open(INDEX_FILE, "r") as f:
        return int(f.read())


def save_index(i):
    with open(INDEX_FILE, "w") as f:
        f.write(str(i))


def get_next_proxies():
    if not os.path.exists(PROXY_FILE):
        return []

    with open(PROXY_FILE, "r") as f:
        proxies = [p.strip() for p in f if p.strip()]

    if not proxies:
        return []

    index = get_index()

    selected = []
    for i in range(3):
        selected.append(proxies[(index + i) % len(proxies)])

    save_index((index + 3) % len(proxies))

    return selected


def build_buttons(proxies, text):
    keyboard = []

    for p in proxies:
        try:
            server, port, secret = p.split(":")
            url = f"https://t.me/proxy?server={server}&port={port}&secret={secret}"
            keyboard.append([InlineKeyboardButton("🔗 اتصال", url=url)])
        except:
            continue

    share_url = f"https://t.me/share/url?text={quote(text)}"
    keyboard.append([InlineKeyboardButton("📤 Share", url=share_url)])

    return InlineKeyboardMarkup(keyboard)


async def run_once():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    proxies = get_next_proxies()
    if not proxies:
        return

    text = "🚀 پروکسی جدید:\n\n" + "\n".join(proxies)

    await app.bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        reply_markup=build_buttons(proxies, text)
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_once())
