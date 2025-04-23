from decimal import Decimal

from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import F

from app.internal.db.models.bank_data import BankAccount, BankCard
from app.internal.db.models.history_data import TransactionHistory
from app.internal.db.models.user_data import TelegramUser
from app.internal.domain.services import CustomErrors


async def get_account(number: str) -> BankAccount:
    return await BankAccount.objects.aget(number=number)


async def get_accounts(user: TelegramUser) -> list[BankAccount]:
    return [i async for i in BankAccount.objects.filter(user=user.id)]


async def get_card(number: str) -> BankCard:
    return await BankCard.objects.aget(number=number)


async def get_cards(number: str) -> list[BankCard]:
    return [i async for i in BankCard.objects.filter(account=number)]


@sync_to_async
def send_money(payment_sender: str, payee: str, amount: str, message_sender: TelegramUser) -> None:
    def get_obj(str):
        if not str.isdigit():
            response = BankAccount.objects.select_related("user").filter(user__username=str).first()
            if not response:
                raise TelegramUser.DoesNotExist
        elif len(str) == 16:
            response = BankAccount.objects.select_related("user").get(bankcard=str)
        elif len(str) == 20:
            response = BankAccount.objects.select_related("user").get(number=str)
        else:
            raise CustomErrors.ObjectProperties
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
        TransactionHistory.objects.create(from_account=payment_sender, to_account=payee, amount_money=amount)
