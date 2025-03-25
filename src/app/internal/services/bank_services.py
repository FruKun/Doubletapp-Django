from decimal import Decimal

from app.internal.models.bank_data import BankAccount, BankCard
from app.internal.models.user_data import TelegramUser


async def get_account(number: str) -> BankAccount:
    await BankAccount.objects.aget(number=number)


async def get_accounts(user: TelegramUser) -> list[BankAccount]:
    return [i async for i in BankAccount.objects.filter(user=user.id)]


async def get_card(number: str) -> BankCard:
    await BankCard.objects.aget(number=number)


async def get_cards(number: str) -> list[BankCard]:
    return [i async for i in BankCard.objects.filter(account=number)]


async def send_money(payment_sender, payee, amount, userid) -> None:
    async def get_obj(str):
        if not str.isdigit():
            response = [i async for i in BankAccount.objects.prefetch_related("user").filter(user__username=str)][0]
        elif len(str) == 16:
            response = await BankAccount.objects.prefetch_related("user").aget(bankcard=str)
        elif len(str) == 20:
            response = await BankAccount.objects.prefetch_related("user").aget(number=str)
        else:
            raise ValueError
        return response

    amount = Decimal(amount)
    if amount < 0:
        raise ValueError
    payment_sender = await get_obj(payment_sender)
    if payment_sender.user != await TelegramUser.objects.aget(id=userid):
        raise AttributeError
    payee = await get_obj(payee)
    payment_sender.balance -= amount
    payee.balance += amount
    await payment_sender.asave()
    await payee.asave()
