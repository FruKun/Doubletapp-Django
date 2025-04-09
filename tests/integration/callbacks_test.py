from decimal import Decimal

import pytest
from django.conf import settings
from django.template.loader import render_to_string

from app.internal.models.bank_data import BankAccount
from app.internal.models.user_data import TelegramUser
from app.internal.transport.bot.handlers import (
    command_account_history_callback,
    command_accounts_callback,
    command_add_favorite_callback,
    command_all_users_callback,
    command_cards_callback,
    command_del_favorite_callback,
    command_favourites_callback,
    command_help_callback,
    command_me_callback,
    command_me_link_callback,
    command_send_money_callback,
    command_set_phone_callback,
    command_start_callback,
    message_callback,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio, pytest.mark.integration]


@pytest.mark.parametrize("id,username,full_name", [(1, "test1", "test wphone"), (2, "test2", "test nophone")])
@pytest.mark.parametrize("args", [([]), (["aboba"]), (["aboba1", "aboba2"])])
async def test_command_start_callback(update, context, id, username, full_name, args):

    update.message.from_user.id = id
    update.message.from_user.username = username
    update.message.from_user.full_name = full_name
    context.args = args

    await command_start_callback(update, context)
    update.message.reply_html.assert_called_with(render_to_string("command_start.html"))
    user = await TelegramUser.objects.aget(id=id)
    assert user.username == username


@pytest.mark.parametrize(
    "id,username,full_name",
    [(100, "test100", "test wphone"), (200, "test200", "test nophone"), (404, "test404", "test noregister")],
)
@pytest.mark.parametrize("args", [([]), (["aboba"]), (["aboba1", "aboba2"])])
async def test_command_help_callback(update, context, id, username, full_name, args):

    update.message.from_user.id = id
    update.message.from_user.username = username
    update.message.from_user.full_name = full_name
    context.args = args

    await command_help_callback(update, context)
    update.message.reply_html.assert_called_with(render_to_string("command_help.html"))


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
    await command_set_phone_callback(update, context)
    update.message.reply_text.assert_called_with(expected)
    user = await TelegramUser.objects.aget(id=100)
    assert user.phone_number == expected2


@pytest.mark.parametrize(
    "id,username,full_name",
    [(100, "test100", "test wphone"), (200, "test200", "test nophone"), (404, "test404", "test noregister")],
)
@pytest.mark.parametrize("args", [([]), (["aboba"]), (["aboba1", "aboba2"])])
async def test_message_callback(update, context, id, username, full_name, args):

    update.message.from_user.id = id
    update.message.from_user.username = username
    update.message.from_user.full_name = full_name
    context.args = args

    await message_callback(update, context)
    update.message.reply_html.assert_called_with(render_to_string("command_start.html"))


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

    await command_me_callback(update, context)
    update.message.reply_text.assert_called_with(expected)


@pytest.mark.parametrize(
    "id,username,full_name, expected",
    [
        (100, "test100", "test wphone", f"https://{settings.DOMAIN_URL}/api/get_user?user_id=100"),
        (200, "test200", "test nophone", render_to_string("phone_error.html")),
        (404, "test404", "test noregister", render_to_string("register_error.html")),
    ],
)
@pytest.mark.parametrize("args", [([]), (["aboba"]), (["aboba1", "aboba2"])])
async def test_command_me_link_callback(update, context, id, username, full_name, args, expected, setup_user):

    update.message.from_user.id = id
    update.message.from_user.username = username
    update.message.from_user.full_name = full_name
    context.args = args

    await command_me_link_callback(update, context)
    update.message.reply_text.assert_called_with(expected)


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


@pytest.mark.parametrize(
    "id,username,full_name,expected",
    [
        (
            10,
            "test10",
            "test user",
            render_to_string(
                "command_favourites.html",
                context={
                    "list": [
                        "test11",
                        "12345678901234567891",
                        "12345678901234567892",
                        "1234567890123450",
                        "1234567890123458",
                    ]
                },
            ),
        ),
        (
            100,
            "test100",
            "test wphone",
            render_to_string(
                "command_favourites.html",
                context={"list": []},
            ),
        ),
        (
            200,
            "test200",
            "test nophone",
            render_to_string(
                "command_favourites.html",
                context={"list": []},
            ),
        ),
        (404, "test404", "test noregister", render_to_string("register_error.html")),
    ],
)
@pytest.mark.parametrize("args", [([]), (["aboba"]), (["aboba1", "aboba2"])])
async def test_command_favourites_callback(
    update, context, id, username, full_name, args, expected, setup_db, setup_user
):

    update.message.from_user.id = id
    update.message.from_user.username = username
    update.message.from_user.full_name = full_name
    context.args = args
    await command_favourites_callback(update, context)
    update.message.reply_text.assert_called_with(expected)


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
    await command_add_favorite_callback(update, context)
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
    await command_add_favorite_callback(update, context)
    update.message.reply_text.assert_called_with(render_to_string("favorite_error.html", context={"error": "user"}))


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
        (["aboba", "aboba", "100"], render_to_string("register_error.html")),
        (["123", "aboba", "100"], render_to_string("command_send_money.html", context={"error": "object"})),
        (
            ["123456789012345678901", "aboba", "100"],
            render_to_string("command_send_money.html", context={"error": "object"}),
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
            render_to_string("command_send_money.html", context={"error": ""}),
        ),
        (
            ["12345678901234567890", "12345678901234567891", "100000"],
            render_to_string("command_send_money.html", context={"error": "integrity"}),
        ),
    ],
)
async def test_command_send_money_callback(update, context, id, username, full_name, args, expected, setup_db):

    update.message.from_user.id = id
    update.message.from_user.username = username
    update.message.from_user.full_name = full_name
    context.args = args

    await command_send_money_callback(update, context)
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

    update.message.from_user.id = id
    context.args = args
    await command_send_money_callback(update, context)
    update.message.reply_text.assert_called_with(expected)


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
    await command_account_history_callback(update, context)
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
            render_to_string("account_history.html", context={"history": [], "self": "12345678901234567890"}),
        ),
    ],
)
async def test_command_account_history(update, context, id, username, full_name, args, expected, setup_db):
    update.message.from_user.id = id
    context.args = args
    await command_account_history_callback(update, context)
    update.message.reply_text.assert_called_with(expected)


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
