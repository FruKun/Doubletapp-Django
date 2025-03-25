from django.conf import settings
from django.db.utils import IntegrityError
from django.template.loader import render_to_string
from phonenumbers import NumberParseException
from telegram import Update
from telegram.ext import ContextTypes

from app.internal.models.bank_data import BankAccount, BankCard
from app.internal.models.user_data import TelegramUser
from app.internal.services.bank_services import get_accounts, get_cards, send_money
from app.internal.services.user_service import add_favorite, del_favorite, get_user, save_user, set_phone


async def command_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start"""
    context.user_data["state"] = "default"
    await save_user(update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username)
    await update.message.reply_html(render_to_string("command_start.html"))


async def command_help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/help"""
    context.user_data["state"] = "default"
    await update.message.reply_html(render_to_string("command_help.html", context={}))


async def command_set_phone_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/set_phone"""
    await save_user(update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username)
    context.user_data["state"] = "default"
    try:
        if context.args:
            await set_phone(update.message.from_user.id, context.args[0], update.message.from_user.language_code)
            await update.message.reply_text("Done")
        elif update.message.contact:
            await set_phone(
                update.message.from_user.id, update.message.contact.phone_number, update.message.from_user.language_code
            )
            await update.message.reply_text("U set phone number: " + update.message.contact.phone_number)
        else:
            raise AttributeError
    except (NumberParseException, AttributeError):
        context.user_data["state"] = "set_phone"
        await update.message.reply_text("write u number below\nExample: +78005553535")


async def message_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """message handler"""
    try:
        if context.user_data["state"] == "set_phone":
            context.user_data["state"] = "default"
            await set_phone(update.message.from_user.id, update.message.text, update.message.from_user.language_code)
            await update.message.reply_text("Done")

        else:
            await update.message.reply_html(render_to_string("command_start.html"))
    except (KeyError, TelegramUser.DoesNotExist):
        await update.message.reply_text("you are not registered, enter the command /start")
    except NumberParseException:
        await update.message.reply_text(
            "try again, u can sand me your phone with command /set_phone\n" + "Example: +78005553535"
        )


async def command_me_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/me"""
    context.user_data["state"] = "default"
    try:
        user = await get_user(update.message.from_user.id)
        if not user.phone_number:
            await update.message.reply_text("u need set phone /set_phone")
        else:
            await update.message.reply_html(
                render_to_string(
                    "command_me.html",
                    context={"fullname": user.full_name, "username": user.username, "phone": user.phone_number},
                )
            )
    except TelegramUser.DoesNotExist:
        await save_user(
            update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username
        )
        await update.message.reply_text("Bot dont have information about u\nBefore u need set phone /set_phone")


async def command_me_link_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/give_me_link"""
    user_id = update.message.from_user.id
    context.user_data["state"] = "default"
    try:
        user = await get_user(user_id)
        if not user.phone_number:
            await update.message.reply_text("u need set phone /set_phone")
        else:
            await update.message.reply_text(f"http://{settings.ALLOWED_HOSTS[0]}:8000/api/get_user?user_id={user_id}")

    except TelegramUser.DoesNotExist:
        await save_user(
            update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username
        )
        await update.message.reply_text("Bot dont have information about u\nBefore u need set phone /set_phone")


async def command_accounts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/accounts"""
    context.user_data["state"] = "default"
    try:
        user = await get_user(update.message.from_user.id)
        if user.phone_number:
            accounts = await get_accounts(user)
            response = render_to_string("command_accounts.html", context={"list": accounts})
        else:
            response = "u need set phone /set_phone"
    except TelegramUser.DoesNotExist:
        response = "u not registered\nwrite /start"
    await update.message.reply_text(response)


async def command_cards_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/cards"""
    context.user_data["state"] = "default"
    try:
        user = await get_user(update.message.from_user.id)
        if not user.phone_number:
            response = "u need set phone /set_phone"
        if context.args:
            cards = await get_cards(context.args[0])
            response = render_to_string("command_cards.html", context={"list": cards})
        else:
            response = "try again\nexample: /cards 12345"
    except TelegramUser.DoesNotExist:
        response = "u not registered\nwrite /start"
    except BankAccount.DoesNotExist:
        response = "u dont have this account"
    await update.message.reply_text(response)


async def command_favourites_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/favourites"""
    context.user_data["state"] = "default"
    try:
        user = await get_user(update.message.from_user.id)
        favourites = user.list_of_favourites
        response = render_to_string(
            "command_favourites.html",
            context={
                "usernames": favourites["usernames"],
                "accounts": favourites["accounts"],
                "cards": favourites["cards"],
            },
        )
    except TelegramUser.DoesNotExist:
        response = "u not registered\nwrite /start"
    await update.message.reply_text(response)


async def command_add_favorite_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/add_favorite"""
    context.user_data["state"] = "default"
    try:
        await add_favorite(update.message.from_user.id, context.args[0])
        response = "done"
    except TelegramUser.DoesNotExist:
        response = render_to_string("favorite_error.html", context={"error": "user"})
    except BankAccount.DoesNotExist:
        response = render_to_string("favorite_error.html", context={"error": "account"})
    except BankCard.DoesNotExist:
        response = render_to_string("favorite_error.html", context={"error": "card"})
    except Exception:
        response = render_to_string("favorite_error.html", context={"error": "base"})
    await update.message.reply_text(response)


async def command_del_favorite_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/del_favorite"""
    context.user_data["state"] = "default"
    try:
        await del_favorite(update.message.from_user.id, context.args[0])
        response = "done"
    except TelegramUser.DoesNotExist:
        response = render_to_string("favorite_error.html", context={"error": "user"})
    except Exception:
        response = render_to_string("favorite_error.html", context={"error": "del"})
    await update.message.reply_text(response)


async def command_send_money_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/send_money {payment_sender} {payee} {amount}"""
    context.user_data["state"] = "default"
    try:
        await send_money(context.args[0], context.args[1], context.args[2], update.message.from_user.id)
        response = render_to_string("command_send_money.html", context={"error": ""})
    except IntegrityError:
        response = render_to_string("command_send_money.html", context={"error": "integrity"})
    except AttributeError:
        response = render_to_string("command_send_money.html", context={"error": "attribute"})
    except ValueError:
        response = render_to_string("command_send_money.html", context={"error": "value"})
    except (IndexError, TelegramUser.DoesNotExist):
        response = render_to_string("command_send_money.html", context={"error": "index"})
    except BankAccount.DoesNotExist:
        response = render_to_string("command_send_money.html", context={"error": "account"})
    await update.message.reply_text(response)
