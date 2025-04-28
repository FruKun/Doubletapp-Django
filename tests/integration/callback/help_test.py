import pytest
from django.template.loader import render_to_string

from app.internal.presentation.bot.handlers import BotHandlers

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio, pytest.mark.integration]


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

    await BotHandlers().command_help_callback(update, context)
    update.message.reply_html.assert_called_with(render_to_string("command_help.html"))
