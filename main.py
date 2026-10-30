import os
import logging
import asyncio
from datetime import datetime, timezone

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "9202834177:AAEK4L7HtKmLGiSMIQjpTZUqGR3hg-sqHZk").strip()
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def get_profile_photo_file_id(user_id: int):
    """Return the largest available profile photo file_id, if the user has one."""
    try:
        response = requests.get(
            f"{API_BASE}/getUserProfilePhotos",
            params={"user_id": user_id, "limit": 1},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        if not data.get("ok") or not data.get("result", {}).get("photos"):
            return None
        # Each photo size has a different resolution; the last is generally largest.
        return data["result"]["photos"][0][-1]["file_id"]
    except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
        logger.warning("Could not fetch profile photo for %s: %s", user_id, exc)
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user is None or update.effective_message is None:
        return

    full_name = " ".join(part for part in [user.first_name, user.last_name] if part) or "Not provided"
    username = f"@{user.username}" if user.username else "Not set"
    premium = "Yes ⭐ Telegram Premium" if getattr(user, "is_premium", False) else "No / not reported"
    bot_language = user.language_code or "Not provided"

    # Telegram Bot API does not provide account creation date, phone number,
    # email, IP address, or private account details.
    created_date = "Unavailable — Telegram Bot API does not expose account creation date"

    text = (
        "👤 YOUR TELEGRAM PROFILE INFO\n\n"
        f"📝 Name: {full_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 User ID: `{user.id}`\n"
        f"⭐ Telegram Premium: {premium}\n"
        f"🌐 Language: {bot_language}\n"
        f"🤖 Bot interaction: You started this bot\n\n"
        f"📅 Account creation date: {created_date}\n\n"
        "ℹ️ This shows only information Telegram makes available to bots."
    )

    photo_file_id = await context.application.bot_data.get("unused", None) if False else None
    # The Bot API helper is synchronous; run it without blocking the async handler.
    import asyncio
    photo_file_id = await asyncio.to_thread(get_profile_photo_file_id, user.id)

    if photo_file_id:
        try:
            await update.effective_message.reply_photo(
                photo=photo_file_id,
                caption=text,
                parse_mode="Markdown",
            )
            return
        except Exception as exc:
            logger.warning("Could not send profile photo: %s", exc)

    await update.effective_message.reply_text(text, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message:
        await update.effective_message.reply_text(
            "Send /start to view the Telegram profile information available to this bot."
        )


def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN is missing. Add your Telegram bot token as an environment variable in Render."
        )

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    logger.info("Bot is starting with long polling...")
    # Python 3.14 no longer creates a default event loop automatically.
    # Create one explicitly for python-telegram-bot run_polling().
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
