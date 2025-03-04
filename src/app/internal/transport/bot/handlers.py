from phonenumbers import NumberParseException
from telegram import Update
from telegram.ext import ContextTypes

from app.internal.models.user_data import TelegramUser
from app.internal.services.user_service import get_user, save_user, set_phone


async def command_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start"""
    context.user_data["state"] = "default"
    await save_user(update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username)
    await update.message.reply_text(
        "Hello! You can send me your phone with command /set_phone\n"
        + "Or give me phone number in line /set_phone +78005553535"
    )


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
            await update.message.reply_text(
                "You can send me your phone with command /set_phone\n"
                + "Or give me phone number in line /set_phone +78005553535"
            )
    except (KeyError, TelegramUser.DoesNotExist):
        await update.message.reply_text("you are not registered, enter the command /start")
    except NumberParseException:
        await update.message.reply_text(
            "try again, u can sand me your phone with comman /set_phone\n" + "Example: +78005553535"
        )


async def command_me_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/me"""
    context.user_data["state"] = "default"
    try:
        user = await get_user(update.message.from_user.id)
        if not user.phone_number:
            await update.message.reply_text("u need set phone /set_phone")
        else:
            text = f"{update.message.from_user.id}: {user.full_name}\nyour accounts:\n"
            async for i in user.bankaccount_set.all():
                text += f"{i.number},\tbalance: {i.balance}\ncards:\n"
                async for j in i.bankcard_set.all():
                    text += f"\t\t\t{j.number}\n"
            await update.message.reply_text(
                "its u:\n"
                + f"full name: {str(user.full_name)}\n"
                + f"username: {str(user.username)}\n"
                + f"phone number: {str(user.phone_number)}\n"
                + text
                + "u can use /give_me_link"
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
            await update.message.reply_text(f"http://192.168.0.178:8000/api/get_user?user_id={user_id}")

    except TelegramUser.DoesNotExist:
        await save_user(
            update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username
        )
        await update.message.reply_text("Bot dont have information about u\nBefore u need set phone /set_phone")
