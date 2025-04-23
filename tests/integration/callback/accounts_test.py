import pytest
from django.template.loader import render_to_string

from app.internal.presentation.bot.handlers import (
    command_accounts_callback,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio, pytest.mark.integration]


@pytest.mark.parametrize(
    "id,username,full_name, expected",
    [
        (
            10,
            "test10",
            "test user",
            render_to_string(
                "command_accounts.html",
                context={
                    "list": [
                        {"number": "12345678901234567890", "balance": "10000.000"},
                        {"number": "12345678901234567891", "balance": "10000.000"},
                    ]
                },
            ),
        ),
        (100, "test100", "test wphone", render_to_string("command_accounts.html")),
        (200, "test200", "test nophone", render_to_string("phone_error.html")),
        (404, "test404", "test noregister", render_to_string("register_error.html")),
    ],
)
@pytest.mark.parametrize("args", [([]), (["aboba"]), (["aboba1", "aboba2"])])
async def test_command_accounts_callback(
    update, context, id, username, full_name, args, expected, setup_db, setup_user
):

    update.message.from_user.id = id
    update.message.from_user.username = username
    update.message.from_user.full_name = full_name
    context.args = args
    await command_accounts_callback(update, context)
    update.message.reply_text.assert_called_with(expected)
