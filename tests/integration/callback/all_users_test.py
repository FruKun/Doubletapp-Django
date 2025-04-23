import pytest
from django.template.loader import render_to_string

from app.internal.presentation.bot.handlers import (
    command_all_users_callback,
)

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
async def test_command_all_users_user_error(update, context, id, args, expected, setup_user):
    update.message.from_user.id = id
    context.args = args
    await command_all_users_callback(update, context)
    update.message.reply_text.assert_called_with(expected)


@pytest.mark.parametrize(
    "id, expected",
    [
        (10, render_to_string("command_all_users.html")),
        (100, render_to_string("command_all_users.html")),
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
async def test_command_all_users(update, context, id, args, expected, setup_db, setup_user):
    update.message.from_user.id = id
    context.args = args
    await command_all_users_callback(update, context)
    update.message.reply_text.assert_called_with(expected)
