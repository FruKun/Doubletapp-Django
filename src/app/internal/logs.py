from logging import Handler

import requests
from django.conf import settings


class TelegramHandler(Handler):
    def emit(self, record) -> None:
        message = f"{record.asctime} - {record.filename} - {record.levelname}- {record.message}"
        requests.get(f"https://api.telegram.org/bot{settings.TOKEN}/sendMessage?chat_id=-4640831807&text={message}")
