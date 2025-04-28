import pytest
from django.template.loader import render_to_string

from app.internal.presentation.bot.handlers import BotHandlers

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio, pytest.mark.integration]


@pytest.mark.parametrize(
    "id,username,full_name, phone_number, expected",
    [
        (
            100,
            "test100",
            "test wphone",
            "8 (800) 555-35-35",
            render_to_string(
                "command_me.html",
                context={"fullname": "test wphone", "username": "test100", "phone": "8 (800) 555-35-45"},
            ),
        ),
        (200, "test200", "test nophone", "", render_to_string("phone_error.html")),
        (404, "test404", "test noregister", "", render_to_string("register_error.html")),
    ],
)
@pytest.mark.parametrize("args", [([]), (["aboba"]), (["aboba1", "aboba2"])])
async def test_command_me_callback(update, context, id, username, full_name, phone_number, args, expected, setup_user):

    update.message.from_user.id = id
    update.message.from_user.username = username
    update.message.from_user.full_name = full_name
    context.args = args

    await BotHandlers().command_me_callback(update, context)
    update.message.reply_text.assert_called_with(expected)
