import pytest
from django.template.loader import render_to_string

from app.internal.presentation.bot.handlers import BotHandlers

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio, pytest.mark.integration]


@pytest.mark.parametrize(
    "id, expected",
    [
        (200, render_to_string("phone_error.html")),
        (404, render_to_string("register_error.html")),
    ],
)
@pytest.mark.parametrize(
    "args",
    [
        ([]),
        (["aboba"]),
        (["aboba", "aboba"]),
    ],
)
async def test_command_account_history_user_error(update, context, id, args, expected, setup_user):
    update.message.from_user.id = id
    context.args = args
    await BotHandlers().command_account_history_callback(update, context)
    update.message.reply_text.assert_called_with(expected)


@pytest.mark.parametrize(
    "id, username, full_name",
    [
        (10, "test10", "test user"),
    ],
)
@pytest.mark.parametrize(
    "args, expected",
    [
        ([], "/account_history {u account number}"),
        (["aboba"], "its not a account"),
        (["aboba", "aboba"], "its not a account"),
        (["12345678901234567899"], "account does not exist"),
        (["12345678901234567892"], "its not u account"),
        (
            ["12345678901234567890"],
            "Done"
        ),
    ],
)
async def test_command_account_history(update, context, id, username, full_name, args, expected, setup_db):
    update.message.from_user.id = id
    context.args = args
    await BotHandlers().command_account_history_callback(update, context)
    update.message.reply_text.assert_called_with(expected)
