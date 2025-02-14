import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from django.conf import settings

# Enable logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
# logging.getLogger("httpx").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)


async def command_start_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await update.message.reply_text("aboba")


async def command_set_phone_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await update.message.reply_text("all done")


async def command_me_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await update.message.reply_text(
        "its u:\n"
        + str(update.message.from_user.id)
        + "\n"
        + update.message.from_user.full_name
        + "\n"
        + update.message.from_user.username
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("echo: " + update.message.text)


def run_bot() -> None:
    application = Application.builder().token(settings.TOKEN).build()
    application.add_handler(CommandHandler("start", command_start_handler))
    application.add_handler(CommandHandler(
        "set_phone", command_set_phone_handler))
    application.add_handler(CommandHandler("me", command_me_handler))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)
