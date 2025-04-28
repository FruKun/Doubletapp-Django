import pytest
from django.template.loader import render_to_string

from app.internal.db.models.user_data import TelegramUser
from app.internal.presentation.bot.handlers import BotHandlers

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio, pytest.mark.integration]


@pytest.mark.parametrize(
    "id,username,full_name",
    [
        (100, "test100", "test wphone"),
        (200, "test200", "test nophone"),
    ],
)
@pytest.mark.parametrize(
    "args, expected",
    [
        ([], render_to_string("favorite_error.html", context={"error": "base"})),
        (["aboba"], render_to_string("favorite_error.html", context={"error": "user"})),
        (["aboba1", "aboba2"], render_to_string("favorite_error.html", context={"error": "user"})),
        (["123"], render_to_string("favorite_error.html", context={"error": "base"})),
        (["12345678901234567890123"], render_to_string("favorite_error.html", context={"error": "base"})),
        (["12345678901239567890"], render_to_string("favorite_error.html", context={"error": "account"})),
        (["1234567899123456"], render_to_string("favorite_error.html", context={"error": "card"})),
        (["1" * 256], render_to_string("favorite_error.html", context={"error": "base"})),
        (["a" * 256], render_to_string("favorite_error.html", context={"error": "base"})),
        (["test10"], "done"),
        (["12345678901234567890"], "done"),
        (["1234567890123456"], "done"),
    ],
)
async def test_command_add_favorite_callback(
    update, context, id, username, full_name, args, expected, setup_db, setup_user
):

    update.message.from_user.id = id
    update.message.from_user.username = username
    update.message.from_user.full_name = full_name
    context.args = args
    await BotHandlers().command_add_favorite_callback(update, context)
    update.message.reply_text.assert_called_with(expected)
    if expected == "done":
        user = await TelegramUser.objects.aget(id=id)
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
        (["12345678901239567890"]),
        (["1234567899123456"]),
        (["1" * 256]),
        (["a" * 256]),
        (["test10"]),
        (["12345678901234567890"]),
        (["1234567890123456"]),
    ],
)
async def test_command_add_favorite_callback_no_register(update, context, id, args):

    update.message.from_user.id = id
    context.args = args
    await BotHandlers().command_add_favorite_callback(update, context)
    update.message.reply_text.assert_called_with(render_to_string("favorite_error.html", context={"error": "user"}))
