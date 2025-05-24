from app.internal.db.models.bank_data import BankCard


class CardService:
    async def aget_cards_by_account_number(self, account_number: str, start: int = 0, end: int = 10) -> list[BankCard]:
        return [i async for i in BankCard.objects.filter(account=account_number)[start:end]]

    def get_cards(self) -> list[BankCard]:
        return [i for i in BankCard.objects.all()]
