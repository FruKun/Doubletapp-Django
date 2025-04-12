from django.db.models import Q

from app.internal.models.bank_data import BankAccount
from app.internal.models.history_data import TransactionHistory
from app.internal.models.user_data import TelegramUser
from app.internal.services import CustomErrors


async def account_history(user: TelegramUser, account_number: str) -> list[TransactionHistory]:
    if not account_number.isdigit() or not len(account_number) == 20:
        raise CustomErrors.ObjectProperties
    account = await BankAccount.objects.select_related("user").aget(number=account_number)
    if user != account.user:
        raise CustomErrors.Sender
    return [
        i
        async for i in TransactionHistory.objects.values(
            "from_account__number", "to_account__number", "amount_money", "created_at"
        ).filter(Q(from_account=account) | Q(to_account=account))[:5]
    ]


async def all_usernames(user: TelegramUser) -> list[str]:
    account_list = [
        i
        async for i in BankAccount.objects.values(
            "transactionhistory_from__to_account__user__username", "transactionhistory_to__from_account__user__username"
        ).filter(user=user)
    ]
    uniq_usernames = set()
    for account in account_list:
        uniq_usernames.add(account["transactionhistory_from__to_account__user__username"])
        uniq_usernames.add(account["transactionhistory_to__from_account__user__username"])
    uniq_usernames.remove(None)
    return uniq_usernames
