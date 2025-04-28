from typing import Optional

from app.internal.db.models.bank_data import BankCard


class CardRepository:
    def get_card_by_number(self, number: str) -> Optional[BankCard]:
        return BankCard.objects.select_related("account").filter(number=number).first()

    async def aget_card_by_number(self, number: str) -> Optional[BankCard]:
        return await BankCard.objects.filter(number=number).afirst()

    def get_cards_by_account_number(self, account_number: str) -> list[BankCard]:
        return [i for i in BankCard.objects.filter(account=account_number)]

    async def aget_cards_by_account_number(self, account_number: str) -> list[BankCard]:
        return [i async for i in BankCard.objects.filter(account=account_number)]

    def get_cards(self) -> list[BankCard]:
        return [i for i in BankCard.objects.all()]
