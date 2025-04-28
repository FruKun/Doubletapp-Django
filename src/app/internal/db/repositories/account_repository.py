from decimal import Decimal
from typing import Optional

from app.internal.db.models.bank_data import BankAccount
from app.internal.db.models.user_data import TelegramUser


class AccountRepository:
    def get_account_by_number(self, number: str) -> Optional[BankAccount]:
        return BankAccount.objects.select_related("user").filter(number=number).first()

    async def aget_account_by_number(self, number: str) -> Optional[BankAccount]:
        return await BankAccount.objects.select_related("user").filter(number=number).afirst()

    def get_account_by_card_number(self, number: str) -> Optional[BankAccount]:
        return BankAccount.objects.select_related("user").filter(bankcard=number).first()

    def get_account_by_user_id(self, id: int) -> Optional[BankAccount]:
        return BankAccount.objects.select_related("user").filter(user=id).first()

    def get_account_by_user_username(self, username: str) -> Optional[BankAccount]:
        return BankAccount.objects.select_related("user").filter(user__username=username).first()

    async def aget_accounts_by_user_id(self, id: int) -> list[BankAccount]:
        return [i async for i in BankAccount.objects.select_related("user").filter(user=id)]

    async def aget_usernames_by_user_id(self, id: int) -> list[dict]:
        return [
            i
            async for i in BankAccount.objects.values(
                "transactionhistory_from__to_account__user__username",
                "transactionhistory_to__from_account__user__username",
            ).filter(user=id)
        ]

    def get_accounts(self) -> list[BankAccount]:
        return [i for i in BankAccount.objects.select_related("user").all()]

    def get_or_create_account(self, number: str, user: TelegramUser, balance: Decimal) -> tuple((BankAccount, bool)):
        return BankAccount.objects.get_or_create(number=number, defaults={"user": user, "balance": balance})
