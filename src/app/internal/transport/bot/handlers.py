from django.conf import settings
from django.db.utils import IntegrityError
from django.template.loader import render_to_string
from phonenumbers import NumberParseException
from telegram import Update
from telegram.ext import ContextTypes

from app.internal.models.bank_data import BankAccount, BankCard
from app.internal.models.user_data import TelegramUser
from app.internal.services import CustomErrors
from app.internal.services.bank_services import get_accounts, get_cards, send_money
from app.internal.services.user_service import add_favorite, del_favorite, get_user, save_user, set_phone


async def command_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start"""
    await save_user(update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username)
    await update.message.reply_html(render_to_string("command_start.html"))


async def command_help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/help"""
    await update.message.reply_html(render_to_string("command_help.html", context={}))


async def command_set_phone_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/set_phone"""
    await save_user(update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username)
    try:
        await set_phone(update.message.from_user.id, context.args[0], update.message.from_user.language_code)
        response = "Done"
    except TelegramUser.DoesNotExist:
        response = render_to_string("register_error.html")
    except (NumberParseException, AttributeError, IndexError):
        response = "try again /set_phone +78005553535"
    await update.message.reply_text(response)


async def message_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """message handler"""
    await update.message.reply_html(render_to_string("command_start.html"))


async def command_me_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/me"""
    try:
        user = await get_user(update.message.from_user.id)
        if not user.phone_number:
            raise CustomErrors.PhoneError
        response = render_to_string(
            "command_me.html",
            context={"fullname": user.full_name, "username": user.username, "phone": user.phone_number},
        )
    except TelegramUser.DoesNotExist:
        response = render_to_string("register_error.html")
    except CustomErrors.PhoneError:
        response = render_to_string("phone_error.html")
    await update.message.reply_text(response)


async def command_me_link_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/give_me_link"""
    user_id = update.message.from_user.id
    try:
        user = await get_user(user_id)
        if not user.phone_number:
            raise CustomErrors.PhoneError
        response = f"https://{settings.DOMAIN_URL}/api/get_user?user_id={user_id}"

    except TelegramUser.DoesNotExist:
        response = render_to_string("register_error.html")
    except CustomErrors.PhoneError:
        response = render_to_string("phone_error.html")
    await update.message.reply_text(response)


async def command_accounts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/accounts"""
    try:
        user = await get_user(update.message.from_user.id)
        if not user.phone_number:
            raise CustomErrors.PhoneError
        accounts = await get_accounts(user)
        response = render_to_string("command_accounts.html", context={"list": accounts})
    except TelegramUser.DoesNotExist:
        response = render_to_string("register_error.html")
    except CustomErrors.PhoneError:
        response = render_to_string("phone_error.html")
    await update.message.reply_text(response)


async def command_cards_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/cards"""
    try:
        user = await get_user(update.message.from_user.id)
        if not user.phone_number:
            raise CustomErrors.PhoneError
        if context.args:
            cards = await get_cards(context.args[0])
            response = render_to_string("command_cards.html", context={"list": cards})
        else:
            response = "try again\nexample: /cards 12345"
    except TelegramUser.DoesNotExist:
        response = render_to_string("register_error.html")
    except BankAccount.DoesNotExist:
        response = "u dont have this account"
    except CustomErrors.PhoneError:
        response = render_to_string("phone_error.html")
    await update.message.reply_text(response)


async def command_favourites_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/favourites"""
    try:
        user = await get_user(update.message.from_user.id)
        favourites = user.list_of_favourites
        response = render_to_string(
            "command_favourites.html",
            context={"list": favourites},
        )
    except TelegramUser.DoesNotExist:
        response = render_to_string("register_error.html")
    except CustomErrors.PhoneError:
        response = render_to_string("phone_error.html")
    await update.message.reply_text(response)


async def command_add_favorite_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/add_favorite"""
    try:
        await add_favorite(update.message.from_user.id, context.args[0])
        response = "done"
    except TelegramUser.DoesNotExist:
        response = render_to_string("favorite_error.html", context={"error": "user"})
    except BankAccount.DoesNotExist:
        response = render_to_string("favorite_error.html", context={"error": "account"})
    except BankCard.DoesNotExist:
        response = render_to_string("favorite_error.html", context={"error": "card"})
    except CustomErrors.ObjectProperties:
        response = render_to_string("favorite_error.html", context={"error": "base"})
    except CustomErrors.PhoneError:
        response = render_to_string("phone_error.html")
    await update.message.reply_text(response)


async def command_del_favorite_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/del_favorite"""
    try:
        await del_favorite(update.message.from_user.id, context.args[0])
        response = "done"
    except TelegramUser.DoesNotExist:
        response = render_to_string("favorite_error.html", context={"error": "user"})
    except (CustomErrors.ObjectProperties, ValueError):
        response = render_to_string("favorite_error.html", context={"error": "del"})
    except CustomErrors.PhoneError:
        response = render_to_string("phone_error.html")
    await update.message.reply_text(response)


async def command_send_money_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/send_money {payment_sender} {payee} {amount}"""
    try:
        user = await get_user(update.message.from_user.id)
        if not user.phone_number:
            raise CustomErrors.PhoneError
        await send_money(context.args[0], context.args[1], context.args[2], user)
        response = render_to_string("command_send_money.html", context={"error": ""})
    except IntegrityError:
        response = render_to_string("command_send_money.html", context={"error": "integrity"})
    except CustomErrors.ObjectProperties:
        response = render_to_string("command_send_money.html", context={"error": "object"})
    except CustomErrors.Sender:
        response = render_to_string("command_send_money.html", context={"error": "sender"})
    except IndexError:
        response = render_to_string("command_send_money.html", context={"error": "index"})
    except BankAccount.DoesNotExist:
        response = render_to_string("command_send_money.html", context={"error": "account"})
    except TelegramUser.DoesNotExist:
        response = render_to_string("register_error.html")
    except CustomErrors.PhoneError:
        response = render_to_string("phone_error.html")
    await update.message.reply_text(response)
