from decimal import Decimal
from typing import Optional

from django.db.models import Q

from app.internal.db.models.bank_data import BankAccount
from app.internal.db.models.history_data import TransactionHistory


class TransactionHistoryRepository:
    async def aget_transactions_by_account(self, account: BankAccount) -> list[TransactionHistory]:
        return [
            i
            async for i in TransactionHistory.objects.select_related("from_account", "to_account").filter(
                Q(from_account=account) | Q(to_account=account)
            )
        ]

    def save_transaction(
        self,
        from_account: BankAccount,
        to_account: BankAccount,
        amount_money: Decimal,
        photo_name: Optional[str] = None,
    ) -> None:
        TransactionHistory.objects.create(
            from_account=from_account, to_account=to_account, amount_money=amount_money, photo_name=photo_name
        )

    async def aget_unviewed_transactions_by_account(self, account: BankAccount) -> list[TransactionHistory]:
        return [
            i
            async for i in TransactionHistory.objects.select_related("from_account", "to_account").filter(
                to_account=account, is_viewed=False
            )
        ]
