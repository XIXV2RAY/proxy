import os
import requests
from telegram.ext import ApplicationBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SUB_URL = os.getenv("SUB_URL")


def load_proxies():
    print("SUB_URL =", SUB_URL)

    try:
        r = requests.get(SUB_URL, timeout=10)
        print("HTTP STATUS =", r.status_code)

        lines = r.text.splitlines()
        print("RAW LINES =", len(lines))

        proxies = [x.strip() for x in lines if ":" in x]

        print("VALID PROXIES =", len(proxies))
        return proxies

    except Exception as e:
        print("ERROR LOAD:", e)
        return []


def pick_three(proxies):
    return proxies[:3]


def build_buttons(proxies):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = []

    for p in proxies:
        try:
            parts = p.split(":")
            if len(parts) < 3:
                print("SKIP BAD:", p)
                continue

            ip, port = parts[0], parts[1]
            secret = ":".join(parts[2:])

            url = f"https://t.me/proxy?server={ip}&port={port}&secret={secret}"

            keyboard.append([InlineKeyboardButton("🔗 پروکسی", url=url)])

        except Exception as e:
            print("BUTTON ERROR:", e)

    print("BUTTONS =", len(keyboard))

    return InlineKeyboardMarkup(keyboard)


async def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    proxies = load_proxies()

    if not proxies:
        print("NO PROXIES → EXIT")
        return

    selected = pick_three(proxies)

    if not selected:
        print("NO SELECTED → EXIT")
        return

    text = "🚀 پروکسی جدید"

    try:
        await app.bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            reply_markup=build_buttons(selected)
        )
        print("MESSAGE SENT")

    except Exception as e:
        print("SEND ERROR:", e)


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
