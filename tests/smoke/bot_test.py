import pytest
from django.conf import settings
from telegram.ext import Application

from app.internal.bot import set_handlers
from app.internal.presentation.bot.handlers import BotHandlers

pytestmark = pytest.mark.smoke


@pytest.fixture
def init_bot():
    application = Application.builder().token(settings.TOKEN).build()
    set_handlers(application, BotHandlers())
    yield application


def test_bot_init(init_bot):
    assert init_bot.bot is not None
    assert len(init_bot.handlers) > 0
