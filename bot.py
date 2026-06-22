import os
from urllib.parse import quote
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ===== ENV (GitHub Secrets) =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = os.getenv("CHANNEL_ID")

# ===== FILES =====
PROXY_FILE = "proxies.txt"
INDEX_FILE = "index.txt"


# ===== SAVE PROXIES =====
def save_proxies(proxies):
    with open(PROXY_FILE, "w") as f:
        for p in proxies:
            p = p.strip()
            if p:
                f.write(p + "\n")

    with open(INDEX_FILE, "w") as f:
        f.write("0")


# ===== INDEX =====
def get_index():
    if not os.path.exists(INDEX_FILE):
        return 0
    with open(INDEX_FILE, "r") as f:
        return int(f.read())


def save_index(i):
    with open(INDEX_FILE, "w") as f:
        f.write(str(i))


# ===== GET NEXT PROXIES =====
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


# ===== BUTTONS =====
def build_buttons(proxies, text):
    keyboard = []

    # proxy buttons
    for p in proxies:
        try:
            server, port, secret = p.split(":")
            url = f"https://t.me/proxy?server={server}&port={port}&secret={secret}"
            keyboard.append([InlineKeyboardButton("🔗 اتصال", url=url)])
        except:
            continue

    # share button
    share_url = f"https://t.me/share/url?text={quote(text)}"
    keyboard.append([InlineKeyboardButton("📤 Share", url=share_url)])

    return InlineKeyboardMarkup(keyboard)


# ===== RECEIVE FILE FROM ADMIN =====
async def handle_file(update: ContextTypes.DEFAULT_TYPE, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    if not update.message.document:
        return

    file = await context.bot.get_file(update.message.document.file_id)
    await file.download_to_drive(PROXY_FILE)

    # reset index
    save_index(0)

    # reply to admin
    await update.message.reply_text("✅ فایل دریافت شد")

    # immediately send to channel
    await send_proxy(context)


# ===== SEND TO CHANNEL =====
async def send_proxy(context: ContextTypes.DEFAULT_TYPE):
    proxies = get_next_proxies()
    if not proxies:
        return

    text = "🚀 پروکسی جدید:\n\n" + "\n".join(proxies)

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        reply_markup=build_buttons(proxies, text)
    )


# ===== MAIN (NO JOBQUEUE) =====
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # فقط run once (برای GitHub Actions)
    await send_proxy(app)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
