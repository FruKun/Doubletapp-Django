import logging

from django.conf import settings
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.internal.transport.bot.handlers import (
    command_me_handler,
    command_me_link_handler,
    command_set_phone_handler,
    command_start_handler,
    message_handler,
)

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
# logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [
            ("start", "Starts the bot"),
            ("set_phone", "set phone"),
            ("me", "get info"),
            ("give_me_link", "get url for info"),
        ]
    )


def run_bot() -> None:
    application = Application.builder().token(settings.TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", command_start_handler))
    application.add_handler(CommandHandler("set_phone", command_set_phone_handler))
    application.add_handler(CommandHandler("me", command_me_handler))
    application.add_handler(CommandHandler("give_me_link", command_me_link_handler))
    application.add_handler(MessageHandler(filters.TEXT, message_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
