from phonenumbers import NumberParseException
from telegram import Update
from telegram.ext import ContextTypes

from app.internal.models.user_data import UserData
from app.internal.services.user_service import get_user, save_user, set_phone, state


async def command_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start"""
    state[update.message.from_user.id] = "default"
    await save_user(update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username)
    await update.message.reply_text(
        "Hello! You can send me your phone with command /set_phone\n"
        + "Or give me phone number in line /set_phone +78005553535"
    )


async def command_set_phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/set_phone"""
    await save_user(update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username)
    try:
        if update.message.contact:
            await set_phone(
                update.message.from_user.id, update.message.contact.phone_number, update.message.from_user.language_code
            )
            state[update.message.from_user.id] = "default"
            await update.message.reply_text("U set phone number: " + update.message.contact.phone_number)
        elif context.args:
            await set_phone(update.message.from_user.id, context.args[0], update.message.from_user.language_code)
            state[update.message.from_user.id] = "default"
            await update.message.reply_text("Done")
        else:
            raise AttributeError
    except (NumberParseException, AttributeError):
        state[update.message.from_user.id] = "set_phone"
        await update.message.reply_text("write u number below\nExample: +78005553535")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """message handler"""
    if state[update.message.from_user.id] == "set_phone":
        state[update.message.from_user.id] = "default"
        try:
            await set_phone(update.message.from_user.id, update.message.text, update.message.from_user.language_code)
            await update.message.reply_text("Done")
        except NumberParseException:
            await update.message.reply_text(
                "try again\nAfter writing command /set_phone\nWrite you phone number\nExample: +78005553535"
            )
        except UserData.DoesNotExist:
            await save_user(
                update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username
            )
            await update.message.reply_text("Try again /set_phone")
    else:
        await update.message.reply_text(
            "You can send me your phone with command /set_phone\n"
            + "Or give me phone number in line /set_phone +78005553535"
        )


async def command_me_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/me"""
    state[update.message.from_user.id] = "default"
    try:
        user = await get_user(update.message.from_user.id)
        if not user.phone_number:
            await update.message.reply_text("u need set phone /set_phone")
        else:
            await update.message.reply_text(
                "its u:\n"
                + f"full name: {str(user.full_name)}\n"
                + f"username: {str(user.username)}\n"
                + f"phone number: {str(user.phone_number)}\n"
                + "u can use /give_me_link"
            )
    except UserData.DoesNotExist:
        await save_user(
            update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username
        )
        await update.message.reply_text("Bot dont have information about u\nBefore u need set phone /set_phone")


async def command_me_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/give_me_link"""
    user_id = update.message.from_user.id
    state[user_id] = "default"
    try:
        user = await get_user(user_id)
        if not user.phone_number:
            await update.message.reply_text("u need set phone /set_phone")
        else:
            await update.message.reply_text(f"http://127.0.0.1:8000/api/get_user?user_id={user_id}")

    except UserData.DoesNotExist:
        await save_user(
            update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username
        )
        await update.message.reply_text("Bot dont have information about u\nBefore u need set phone /set_phone")
