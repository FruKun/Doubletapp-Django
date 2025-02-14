from phonenumbers import NumberParseException
from telegram import Update
from telegram.ext import ContextTypes

from app.internal.models.user_data import UserData
from app.internal.services.user_service import get_user, save_user, set_phone

# control the bot status for each user
state = {}


async def command_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start"""
    state[update.message.from_user.id] = "default"
    await save_user(update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username)
    await update.message.reply_text("Hello! You can send me your phone with command /set_phone")


async def command_set_phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/set_phone"""
    state[update.message.from_user.id] = "set_phone"
    await save_user(update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username)
    await update.message.reply_text("write u number below\nExample: +78005553535")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """message handler"""
    if state[update.message.from_user.id] == "set_phone":
        state[update.message.from_user.id] == "default"
        try:
            await set_phone(update.message.from_user.id, update.message.text, update.message.from_user.language_code)
            await update.message.reply_text("Done")
        except NumberParseException:
            await update.message.reply_text(
                "try again\nAfter writing command /set_phone\nWrite you phone number\nExample: +78005553535"
            )
        except UserData.DoesNotExist:
            await update.message.reply_text("Before, you need write command /start")
    else:
        await update.message.reply_text("echo: " + update.message.text)


async def command_me_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/me"""
    state[update.message.from_user.id] == "default"
    try:
        user = await get_user(update.message.from_user.id)
        if user.phone_number is None:
            await update.message.reply_text("u need set phone /set_phone")
        else:
            await update.message.reply_text(
                "its u:\n"
                # + str(user.id)
                # + "\n"
                + str(user.full_name)
                + "\n"
                + str(user.username)
                + "\n"
                + str(user.phone_number)
            )
    except UserData.DoesNotExist:
        await save_user(
            update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username
        )
        await update.message.reply_text("Bot dont have information about u\nBefore u need set phone /set_phone")
