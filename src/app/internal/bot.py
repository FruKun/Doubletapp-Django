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
    command_account_history_callback,
    command_accounts_callback,
    command_add_favorite_callback,
    command_all_users_callback,
    command_cards_callback,
    command_del_favorite_callback,
    command_favourites_callback,
    command_help_callback,
    command_me_callback,
    command_me_link_callback,
    command_send_money_callback,
    command_set_phone_callback,
    command_start_callback,
    message_callback,
)

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [
            ("start", "Starts the bot"),
            ("help", "bot help"),
            ("set_phone", "set phone"),
            ("me", "get info"),
            ("give_me_link", "get url for info"),
            ("accounts", "get bank accounts"),
            ("cards", "get bank cards"),
            ("favourites", "list of favourites"),
            ("add_favorite", "add favorite choice"),
            ("del_favorite", "del favorite choice"),
            ("send_money", "send money from u account to another"),
            ("account_history", "transaction history"),
            ("all_users", "all usernames"),
        ]
    )


def set_handlers(application: Application) -> None:
    application.add_handler(CommandHandler("start", command_start_callback))
    application.add_handler(CommandHandler("help", command_help_callback))
    application.add_handler(CommandHandler("set_phone", command_set_phone_callback))
    application.add_handler(CommandHandler("me", command_me_callback))
    application.add_handler(CommandHandler("accounts", command_accounts_callback))
    application.add_handler(CommandHandler("cards", command_cards_callback))
    application.add_handler(CommandHandler("favourites", command_favourites_callback))
    application.add_handler(CommandHandler("add_favorite", command_add_favorite_callback))
    application.add_handler(CommandHandler("del_favorite", command_del_favorite_callback))
    application.add_handler(CommandHandler("send_money", command_send_money_callback))
    application.add_handler(CommandHandler("give_me_link", command_me_link_callback))
    application.add_handler(CommandHandler("account_history", command_account_history_callback))
    application.add_handler(CommandHandler("all_users", command_all_users_callback))
    application.add_handler(MessageHandler(filters.TEXT, message_callback))


def run_bot() -> None:
    application = Application.builder().token(settings.TOKEN).post_init(post_init).build()
    set_handlers(application)
    if settings.DEBUG:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    else:
        application.run_webhook(
            listen="0.0.0.0",
            port=settings.PORT,
            secret_token=settings.WEBHOOK_SECRET_TOKEN,
            url_path="webhook",
            webhook_url=f"https://{settings.DOMAIN_URL}/webhook/",
        )
