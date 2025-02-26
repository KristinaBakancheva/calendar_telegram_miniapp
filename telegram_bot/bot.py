import logging
import settings

from telegram.ext import (Application, CommandHandler)
from telegram import (ReplyKeyboardMarkup, KeyboardButton, Update, WebAppInfo)

logging.basicConfig(filename="bot.log", level=logging.INFO)


async def start(update, context):
    telegram_id = update.message.from_user.id
    telegram = update.message.from_user.username
    logger = logging.getLogger()
    logger.debug("starting telegram bot")
    app_url = (f"{settings.APP_URL}?telegram_id={telegram_id}"
               f"&telegram={telegram}")
    await update.message.reply_text(
        "Hello. I am a calendar-app for Mentors and People who would like to "
        "find a mentor.\n\n Click the button below to open the app.",
        parse_mode="HTML", reply_markup=ReplyKeyboardMarkup.from_button(
                KeyboardButton("Calendar app", web_app=WebAppInfo(url=app_url)
                               ), resize_keyboard=True
        ))


def main():
    application = Application.builder().token(settings.API_KEY).build()
    application.add_handler(CommandHandler("start", start))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
