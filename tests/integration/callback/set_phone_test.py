import pytest

from app.internal.db.models.user_data import TelegramUser
from app.internal.presentation.bot.handlers import BotHandlers

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio, pytest.mark.integration]


@pytest.mark.parametrize("id,username,full_name", [(100, "test100", "test wphone")])
@pytest.mark.parametrize(
    "args, expected, expected2",
    [
        (["+78005553535"], "Done", "8 (800) 555-35-35"),
        (["+78005553535", "aboba"], "Done", "8 (800) 555-35-35"),
        ([], "try again /set_phone +78005553535", "8 (800) 555-35-45"),
        (["aboba"], "try again /set_phone +78005553535", "8 (800) 555-35-45"),
        (["aboba", "+78005553535"], "try again /set_phone +78005553535", "8 (800) 555-35-45"),
        (["123"], "try again /set_phone +78005553535", "8 (800) 555-35-45"),
        (["+71000000000"], "try again /set_phone +78005553535", "8 (800) 555-35-45"),
    ],
)
async def test_command_set_phone_callback(
    update, context, id, username, full_name, args, expected, expected2, setup_user
):
    update.message.from_user.id = id
    update.message.from_user.username = username
    update.message.from_user.full_name = full_name
    context.args = args
    await BotHandlers().command_set_phone_callback(update, context)
    update.message.reply_text.assert_called_with(expected)
    user = await TelegramUser.objects.aget(id=100)
    assert user.phone_number == expected2
