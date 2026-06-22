import os
import asyncio
from urllib.parse import quote
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ====== ENV (GitHub Secrets) ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = os.getenv("CHANNEL_ID")

# ====== FILES ======
PROXY_FILE = "proxies.txt"
INDEX_FILE = "index.txt"


# ====== SAVE PROXIES ======
def save_proxies(proxies):
    with open(PROXY_FILE, "w") as f:
        for p in proxies:
            p = p.strip()
            if p:
                f.write(p + "\n")

    with open(INDEX_FILE, "w") as f:
        f.write("0")


# ====== INDEX ======
def get_index():
    if not os.path.exists(INDEX_FILE):
        return 0
    with open(INDEX_FILE, "r") as f:
        return int(f.read())


def save_index(i):
    with open(INDEX_FILE, "w") as f:
        f.write(str(i))


# ====== GET NEXT PROXIES (NO DUPLICATE) ======
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

    new_index = (index + 3) % len(proxies)
    save_index(new_index)

    return selected


# ====== BUILD BUTTONS ======
def build_buttons(proxies, text):
    keyboard = []

    # proxy buttons
    for p in proxies:
        try:
            server, port, secret = p.split(":")
            url = f"https://t.me/proxy?server={server}&port={port}&secret={secret}"
            keyboard.append([
                InlineKeyboardButton("🔗 اتصال پروکسی", url=url)
            ])
        except:
            continue

    # share button
    share_text = quote(text)
    share_url = f"https://t.me/share/url?text={share_text}"

    keyboard.append([
        InlineKeyboardButton("📤 ارسال به دیگران", url=share_url)
    ])

    return InlineKeyboardMarkup(keyboard)


# ====== RECEIVE FILE FROM ADMIN ======
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    if update.message.document:
        file = await context.bot.get_file(update.message.document.file_id)
        await file.download_to_drive("temp.txt")

        with open("temp.txt", "r") as f:
            proxies = f.readlines()

        save_proxies(proxies)

        await update.message.reply_text("✅ پروکسی‌ها ذخیره شدند و لیست ریست شد")


# ====== SEND POST TO CHANNEL ======
async def send_proxy(context: ContextTypes.DEFAULT_TYPE):
    proxies = get_next_proxies()
    if not proxies:
        return

    text = "🚀 پروکسی جدید:\n\n"
    for p in proxies:
        text += f"{p}\n"

    buttons = build_buttons(proxies, text)

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        reply_markup=buttons
    )


# ====== MAIN ======
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # هر 1 ساعت
    app.job_queue.run_repeating(send_proxy, interval=3600, first=10)

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
