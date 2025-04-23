import pytest
from django.template.loader import render_to_string

from app.internal.presentation.bot.handlers import (
    command_cards_callback,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio, pytest.mark.integration]


@pytest.mark.parametrize(
    "id,username,full_name,accounts",
    [
        (10, "test10", "test user", ["12345678901234567890"]),
        (100, "test100", "test wphone", []),
    ],
)
@pytest.mark.parametrize(
    "args",
    [
        ([]),
    ],
)
async def test_command_cards_callback_no_args(
    update, context, id, username, full_name, args, accounts, setup_db, setup_user
):

    update.message.from_user.id = id
    update.message.from_user.username = username
    update.message.from_user.full_name = full_name
    context.args = args
    await command_cards_callback(update, context)
    update.message.reply_text.assert_called_with("try again\nexample: /cards 12345")


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
        (["12345678901234567890"]),
        (["12345678901234567892"]),
        (["1234567890123456"]),
        (["aboba"]),
        (["aboba1", "aboba2"]),
    ],
)
async def test_command_cards_callback_user_error(update, context, id, args, expected, setup_db, setup_user):

    update.message.from_user.id = id
    context.args = args
    await command_cards_callback(update, context)
    update.message.reply_text.assert_called_with(expected)


@pytest.mark.parametrize(
    "id,username,full_name,accounts",
    [
        (10, "test10", "test user", ["12345678901234567890"]),
        (100, "test100", "test wphone", []),
    ],
)
@pytest.mark.parametrize(
    "args",
    [
        (["1234567890123456"]),
        (["aboba"]),
        (["aboba1", "aboba2"]),
    ],
)
async def test_command_cards_callback_bankaccount_does_not_exist(
    update, context, id, username, full_name, args, accounts, setup_db, setup_user
):

    update.message.from_user.id = id
    update.message.from_user.username = username
    update.message.from_user.full_name = full_name
    context.args = args
    await command_cards_callback(update, context)
    update.message.reply_text.assert_called_with("account does not exist")


@pytest.mark.parametrize(
    "id,username,full_name,accounts",
    [
        (10, "test10", "test user", ["12345678901234567890"]),
        (100, "test100", "test wphone", []),
    ],
)
@pytest.mark.parametrize(
    "args",
    [
        (["12345678901234567890"]),
        (["12345678901234567892"]),
    ],
)
async def test_command_cards_callback_accounts(
    update, context, id, username, full_name, args, accounts, setup_db, setup_user
):
    update.message.from_user.id = id
    update.message.from_user.username = username
    update.message.from_user.full_name = full_name
    context.args = args
    await command_cards_callback(update, context)
    if accounts == args:
        update.message.reply_text.assert_called_with(
            render_to_string(
                "command_cards.html",
                context={"list": [{"number": "1234567890123456"}, {"number": "1234567890123457"}]},
            )
        )
    else:
        update.message.reply_text.assert_called_with("its not u account")
