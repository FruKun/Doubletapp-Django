import logging
from decimal import Decimal
from typing import Optional

from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import F

from app.internal.db.models.bank_data import BankAccount
from app.internal.db.models.history_data import TransactionHistory
from app.internal.db.models.user_data import TelegramUser
from app.internal.domain.services import CustomErrors
from app.internal.metrics import LAST_TRANSFER


class AccountService:
    def __init__(self):
        self.logger = logging.getLogger("root")

    def get_account_by_user_id(self, id: int) -> BankAccount:
        if account := BankAccount.objects.select_related("user").filter(user=id).first():
            return account
        raise BankAccount.DoesNotExist

    def get_account_by_user_username(self, username: str) -> BankAccount:
        if account := BankAccount.objects.select_related("user").filter(user__username=username).first():
            return account
        raise BankAccount.DoesNotExist

    async def aget_accounts_by_user(self, user: TelegramUser, start: int = 0, end: int = 10) -> list[BankAccount]:
        return [i async for i in BankAccount.objects.select_related("user").filter(user=user)[start:end]]

    def get_accounts(self) -> list[BankAccount]:
        return [i for i in BankAccount.objects.select_related("user").all()]

    @sync_to_async
    def send_money(
        self,
        payment_sender: str,
        payee: str,
        amount: str,
        message_sender: TelegramUser,
        photo: Optional[ContentFile] = None,
    ) -> None:
        def get_obj(obj):
            if len(obj) == 16 and obj.isdigit():
                response = BankAccount.objects.select_related("user").get(bankcard=obj)
            elif len(obj) == 20 and obj.isdigit():
                response = BankAccount.objects.select_related("user").get(number=obj)
            elif obj.isdigit():
                response = self.get_account_by_user_id(int(obj))
            else:
                response = self.get_account_by_user_username(obj)
            return response

        amount = Decimal(amount)
        if amount < 0:
            raise CustomErrors.AmountMoney
        payment_sender = get_obj(payment_sender)
        if payment_sender.user != message_sender:
            raise CustomErrors.Sender
        payee = get_obj(payee)
        with transaction.atomic():
            payment_sender.balance = F("balance") - amount
            payee.balance = F("balance") + amount
            payment_sender.save()
            payee.save()
            TransactionHistory.objects.create(
                from_account=payment_sender, to_account=payee, amount_money=amount, photo=photo
            )
            self.logger.info(f"send money success. payment sender:{payment_sender} payee: {payee} amount: {amount}")
            self.logger.info(f"created new transaction {payment_sender}, {payee}, {amount}, {photo}")
            LAST_TRANSFER.set(amount)
