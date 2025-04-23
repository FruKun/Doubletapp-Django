import pytest
from django.template.loader import render_to_string

from app.internal.db.models.user_data import TelegramUser
from app.internal.presentation.bot.handlers import (
    command_del_favorite_callback,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio, pytest.mark.integration]


@pytest.mark.parametrize(
    "id,username,full_name",
    [
        (10, "test10", "test user"),
    ],
)
@pytest.mark.parametrize(
    "args, expected",
    [
        ([], render_to_string("favorite_error.html", context={"error": "del"})),
        (["aboba"], render_to_string("favorite_error.html", context={"error": "del"})),
        (["aboba1", "aboba2"], render_to_string("favorite_error.html", context={"error": "del"})),
        (["123"], render_to_string("favorite_error.html", context={"error": "del"})),
        (["12345678901234567890123"], render_to_string("favorite_error.html", context={"error": "del"})),
        (["1" * 256], render_to_string("favorite_error.html", context={"error": "del"})),
        (["a" * 256], render_to_string("favorite_error.html", context={"error": "del"})),
        (["test11"], "done"),
        (["12345678901234567891"], "done"),
        (["1234567890123450"], "done"),
    ],
)
async def test_command_del_favorite_callback(
    update, context, id, username, full_name, args, expected, setup_db, setup_user
):

    update.message.from_user.id = id
    update.message.from_user.username = username
    update.message.from_user.full_name = full_name
    context.args = args

    await command_del_favorite_callback(update, context)
    update.message.reply_text.assert_called_with(expected)
    if expected == "done":
        user = await TelegramUser.objects.aget(id=id)
        with pytest.raises(ValueError):
            user.list_of_favourites.index(args[0])


@pytest.mark.parametrize(
    "id",
    [
        (404),
    ],
)
@pytest.mark.parametrize(
    "args",
    [
        ([]),
        (["aboba"]),
        (["aboba1", "aboba2"]),
        (["123"]),
        (["12345678901234567890123"]),
        (["1" * 256]),
        (["a" * 256]),
        (["test10"]),
        (["12345678901234567890"]),
        (["1234567890123456"]),
    ],
)
async def test_command_del_favorite_callback_user_error(update, context, id, args):
    update.message.from_user.id = id
    context.args = args

    await command_del_favorite_callback(update, context)
    update.message.reply_text.assert_called_with(render_to_string("favorite_error.html", context={"error": "user"}))
