from app.internal.models.bank_data import BankAccount, BankCard
from app.internal.models.user_data import TelegramUser


async def get_accounts(user: TelegramUser) -> list[BankAccount]:
    return [i async for i in BankAccount.objects.filter(user=user.id)]


async def get_cards(number: str) -> list[BankCard]:
    return [i async for i in BankCard.objects.filter(account=number)]
