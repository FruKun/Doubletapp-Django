from decimal import Decimal

import pytest
from django.template.loader import render_to_string

from app.internal.db.models.bank_data import BankAccount
from app.internal.presentation.bot.handlers import BotHandlers

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
        ([], render_to_string("command_send_money.html", context={"error": "object"})),
        (["aboba"], render_to_string("command_send_money.html", context={"error": "object"})),
        (["aboba", "aboba"], render_to_string("command_send_money.html", context={"error": "object"})),
        (["aboba", "aboba", "aboba"], render_to_string("command_send_money.html", context={"error": "decimal"})),
        (["aboba", "aboba", "-100"], render_to_string("command_send_money.html", context={"error": "decimal"})),
        (["aboba", "aboba", "100"], render_to_string("command_send_money.html", context={"error": "account"})),
        (["123", "aboba", "100"], render_to_string("command_send_money.html", context={"error": "account"})),
        (
            ["123456789012345678901", "aboba", "100"],
            render_to_string("command_send_money.html", context={"error": "account"}),
        ),
        (
            ["09874563211236547890", "aboba", "100"],
            render_to_string("command_send_money.html", context={"error": "account"}),
        ),
        (
            ["1234567890123450", "aboba", "100"],
            render_to_string("command_send_money.html", context={"error": "sender"}),
        ),
        (
            ["12345678901234567892", "aboba", "100"],
            render_to_string("command_send_money.html", context={"error": "sender"}),
        ),
        (
            ["12345678901234567890", "12345678901234567891", "100"],
            "Done"
        ),
        (
            ["12345678901234567890", "12345678901234567891", "100000"],
            render_to_string("command_send_money.html", context={"error": "integrity"}),
        ),
    ],
)
async def test_command_send_money_callback(update, context, id, username, full_name, args, expected, setup_db):
    update.message.photo=None
    update.message.caption=None
    update.message.from_user.id = id
    update.message.from_user.username = username
    update.message.from_user.full_name = full_name
    context.args = args

    await BotHandlers().command_send_money_callback(update, context)
    update.message.reply_text.assert_called_with(expected)
    if expected == render_to_string("command_send_money.html", context={"error": ""}):
        payment_sender = await BankAccount.objects.aget(number=args[0])
        payee = await BankAccount.objects.aget(number=args[1])
        assert payment_sender.balance == (Decimal(10000) - Decimal(args[2]))
        assert payee.balance == (Decimal(10000) + Decimal(args[2]))


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
        (["aboba", "aboba", "aboba"]),
        (["aboba", "aboba", "-100"]),
        (["aboba", "aboba", "100"]),
        (["123", "aboba", "100"]),
        (["123456789012345678901", "aboba", "100"],),
        (["09874563211236547890", "aboba", "100"],),
        (["1234567890123450", "aboba", "100"],),
        (["12345678901234567892", "aboba", "100"],),
        (["12345678901234567890", "12345678901234567891", "100"],),
        (["12345678901234567890", "12345678901234567891", "100000"],),
    ],
)
async def test_command_send_money_callback_user_error(update, context, id, args, expected, setup_user):
    update.message.photo=None
    update.message.caption=None
    update.message.from_user.id = id
    context.args = args
    await BotHandlers().command_send_money_callback(update, context)
    update.message.reply_text.assert_called_with(expected)
