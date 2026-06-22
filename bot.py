import os
from urllib.parse import quote
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ===== ENV =====
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


# ===== GET PROXIES =====
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

    for p in proxies:
        try:
            server, port, secret = p.split(":")
            url = f"https://t.me/proxy?server={server}&port={port}&secret={secret}"
            keyboard.append([InlineKeyboardButton("🔗 اتصال", url=url)])
        except:
            continue

    share_url = f"https://t.me/share/url?text={quote(text)}"
    keyboard.append([InlineKeyboardButton("📤 ارسال به دیگران", url=share_url)])

    return InlineKeyboardMarkup(keyboard)


# ===== RECEIVE FILE =====
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    if not update.message.document:
        return

    # download file
    file = await context.bot.get_file(update.message.document.file_id)
    await file.download_to_drive(PROXY_FILE)

    # reset index
    save_index(0)

    # reply to admin
    await update.message.reply_text("✅ دریافت شد و ذخیره شد")

    # immediately post to channel
    await send_proxy(context)


# ===== SEND POST =====
async def send_proxy(context: ContextTypes.DEFAULT_TYPE):
    proxies = get_next_proxies()
    if not proxies:
        return

    text = "🚀 پروکسی جدید:\n\n" + "\n".join(proxies)

    buttons = build_buttons(proxies, text)

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        reply_markup=buttons
    )


# ===== MAIN =====
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # file handler
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # every 3 hours
    app.job_queue.run_repeating(send_proxy, interval=10800, first=10)

    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
