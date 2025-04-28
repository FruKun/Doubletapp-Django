from http import HTTPStatus

from django.db.utils import IntegrityError
from ninja_extra import api_controller, http_get, http_post
from ninja_extra.pagination import LimitOffsetPagination, paginate
from ninja_jwt.authentication import JWTAuth

from app.internal.db.models.bank_data import BankAccount
from app.internal.db.models.user_data import TelegramUser
from app.internal.domain.schemas import error_handler
from app.internal.domain.schemas.accounts import BankAccountSchema, MessageAccountSchema, PostBankAccountSchema
from app.internal.domain.services.account_service import AccountService


@api_controller("/accounts", tags=["Accounts"], auth=JWTAuth())
class Accounts:
    def __init__(self):
        self.account_service = AccountService()

    @http_get("/", response={HTTPStatus.OK: list[BankAccountSchema]})
    @paginate(LimitOffsetPagination)
    def get_accounts(self):
        return HTTPStatus.OK, self.account_service.get_accounts()

    @http_get("/{number}", response={HTTPStatus.OK: BankAccountSchema})
    def get_account(self, number: str):
        try:
            return HTTPStatus.OK, self.account_service.get_account_by_number(number)
        except BankAccount.DoesNotExist:
            raise error_handler.BankAccountDoesNotExistException

    @http_post("/", response={HTTPStatus.OK: MessageAccountSchema})
    def post_accounts(self, payload: PostBankAccountSchema):
        try:
            account, created = self.account_service.get_or_create_account(
                payload.number, payload.user_id, payload.balance
            )
            if not created:
                return HTTPStatus.OK, {"message": "account already exist", "number": account.number}
            return HTTPStatus.OK, {"message": "account created", "number": account.number}
        except IntegrityError:
            raise error_handler.IntegrityException
        except TelegramUser.DoesNotExist:
            raise error_handler.TelegramUserDoesNotExistException
