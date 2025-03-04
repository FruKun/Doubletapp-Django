from app.internal.models.bank_data import BankAccount, BankCard
from app.internal.models.user_data import TelegramUser


async def get_accounts(user: TelegramUser) -> list[BankAccount]:
    return [i async for i in user.bankaccount_set.all()]


async def get_cards(number: str) -> list[BankCard]:
    bankaccount = await BankAccount.objects.aget(number=number)
    return [i async for i in bankaccount.bankcard_set.all()]
