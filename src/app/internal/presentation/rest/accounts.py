from http import HTTPStatus

from django.db.utils import IntegrityError
from ninja_extra import api_controller, http_get, http_post
from ninja_jwt.authentication import JWTAuth

from app.internal.db.models.bank_data import BankAccount
from app.internal.db.models.user_data import TelegramUser
from app.internal.domain.schemas import error_handler
from app.internal.domain.schemas.accounts import BankAccountSchema, MessageAccountSchema, PostBankAccountSchema


@api_controller("/accounts", tags=["Accounts"], auth=JWTAuth())
class Accounts:
    @http_get("/", response={HTTPStatus.OK: list[BankAccountSchema]})
    def get_accounts(self):

        return HTTPStatus.OK, BankAccount.objects.select_related("user").all()

    @http_get("/{number}", response={HTTPStatus.OK: BankAccountSchema})
    def get_account(self, number: int):
        try:
            return HTTPStatus.OK, BankAccount.objects.select_related("user").get(number=number)
        except BankAccount.DoesNotExist:
            raise error_handler.BankAccountDoesNotExistException

    @http_post("/", response={HTTPStatus.OK: MessageAccountSchema})
    def post_accounts(self, payload: PostBankAccountSchema):
        try:
            account, created = BankAccount.objects.get_or_create(
                number=payload.number,
                defaults={"user": TelegramUser.objects.get(id=payload.user_id), "balance": payload.balance},
            )
            if not created:
                return HTTPStatus.OK, {"message": "account already exist", "number": account.number}
            return HTTPStatus.OK, {"message": "account created", "number": account.number}
        except IntegrityError:
            raise error_handler.IntegrityException
        except TelegramUser.DoesNotExist:
            raise error_handler.TelegramUserDoesNotExistException
