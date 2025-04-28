from app.internal.db.models.bank_data import BankCard
from app.internal.db.repositories.card_repository import CardRepository


class CardService:
    def __init__(self):
        self.card_repo = CardRepository()

    def get_card_by_number(self, number: str) -> BankCard:
        if card := self.card_repo.get_card_by_number(number):
            return card
        raise BankCard.DoesNotExist

    async def aget_cards_by_account_number(self, number: str) -> list[BankCard]:
        return await self.card_repo.aget_cards_by_account_number(number)

    def get_cards(self) -> list[BankCard]:
        return self.card_repo.get_cards()
