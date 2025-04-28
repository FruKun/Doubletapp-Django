from http import HTTPStatus

from ninja_extra import api_controller, http_get
from ninja_jwt.authentication import JWTAuth

from app.internal.db.models.bank_data import BankCard
from app.internal.domain.schemas import error_handler
from app.internal.domain.schemas.cards import BankCardSchema
from app.internal.domain.services.card_service import CardService


@api_controller("/cards", tags=["Cards"], auth=JWTAuth())
class Cards:
    def __init__(self):
        self.card_service = CardService()

    @http_get("/", response={HTTPStatus.OK: list[BankCardSchema]})
    def get_cards(self):
        return HTTPStatus.OK, self.card_service.get_cards()

    @http_get("/{number}", response={HTTPStatus.OK: BankCardSchema})
    def get_card(self, number: str):
        try:
            return HTTPStatus.OK, self.card_service.get_card_by_number(number)
        except BankCard.DoesNotExist:
            raise error_handler.BankCardDoesNotExistException
