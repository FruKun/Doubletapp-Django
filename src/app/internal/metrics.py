import threading
import time

from django.db.models import Sum
from prometheus_client import Gauge, start_http_server

from app.internal.db.models.bank_data import BankAccount
from app.internal.db.models.history_data import TransactionHistory
from app.internal.db.models.user_data import TelegramUser

USERS_COUNT = Gauge("users_count", "Number of users")
BALANCE_SUM = Gauge("balance_sum", "balance sum")
AMOUNT_TRANSFER = Gauge("amount_transfer", "amount of transfers")
LAST_TRANSFER = Gauge("last_transfer", "amount of last transfer")


def start_thread_metrics():
    start_http_server(9090)
    thread = threading.Thread(target=thread_cycle, daemon=True)
    thread.start()


def thread_cycle():
    while True:
        USERS_COUNT.set(TelegramUser.objects.count())
        BALANCE_SUM.set(BankAccount.objects.all().aggregate(Sum("balance"))["balance__sum"])
        AMOUNT_TRANSFER.set(TransactionHistory.objects.all().aggregate(Sum("amount_money"))["amount_money__sum"])
        time.sleep(15)
