from http import HTTPStatus

from ninja_extra import api_controller, http_get
from ninja_jwt.authentication import JWTAuth

from app.internal.db.models.bank_data import BankCard
from app.internal.domain.schemas import error_handler
from app.internal.domain.schemas.cards import BankCardSchema


@api_controller("/cards", tags=["Cards"], auth=JWTAuth())
class Cards:
    @http_get("/", response={HTTPStatus.OK: list[BankCardSchema]})
    def get_cards(self):

        return 200, BankCard.objects.select_related("account").all()

    @http_get("/{number}", response={HTTPStatus.OK: BankCardSchema})
    def get_card(self, number: int):
        try:
            return HTTPStatus.OK, BankCard.objects.select_related("account").get(number=number)
        except BankCard.DoesNotExist:
            raise error_handler.BankCardDoesNotExistException
