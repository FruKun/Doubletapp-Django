from django.db.models import Q

from app.internal.db.models.bank_data import BankAccount
from app.internal.db.models.history_data import TransactionHistory
from app.internal.db.models.user_data import TelegramUser
from app.internal.domain.services import CustomErrors


class TransactionService:
    async def account_history(self, user: TelegramUser, account_number: str) -> list[TransactionHistory]:
        if not account_number.isdigit() or not len(account_number) == 20:
            raise CustomErrors.InvalidFieldValue
        account = await BankAccount.objects.select_related("user").aget(number=account_number)
        if user != account.user:
            raise CustomErrors.Sender
        return [
            i
            async for i in TransactionHistory.objects.select_related("from_account", "to_account").filter(
                Q(from_account=account) | Q(to_account=account)
            )
        ]

    async def all_usernames(self, user: TelegramUser) -> list[str]:
        list = []
        [
            list.extend(i)
            async for i in BankAccount.objects.values_list(
                "transactionhistory_from__to_account__user__username",
                "transactionhistory_to__from_account__user__username",
            )
            .filter(user=user)
            .distinct()
        ]
        list = set(list)
        list.remove(None)
        return list

    async def unseen_receipts(self, user: TelegramUser) -> list[TransactionHistory]:
        accounts = [i async for i in BankAccount.objects.filter(user=user.id)]
        histories = []
        for account in accounts:
            extend = [
                i
                async for i in TransactionHistory.objects.select_related("from_account", "to_account").filter(
                    to_account=account, is_viewed=False
                )
            ]
            histories.extend(extend)
        return histories

    async def amark_is_viewed(self, history: TransactionHistory):
        history.is_viewed = True
        await history.asave()
