import pytest
from django.template.loader import render_to_string

from app.internal.db.models.user_data import TelegramUser
from app.internal.presentation.bot.handlers import (
    command_start_callback,
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
