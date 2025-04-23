from http import HTTPStatus

from ninja_extra.exceptions import APIException


class TelegramUserDoesNotExistException(APIException):
    status_code = HTTPStatus.NOT_FOUND
    default_detail = "User does not exist"


class BankAccountDoesNotExistException(APIException):
    status_code = HTTPStatus.NOT_FOUND
    default_detail = "Account does not exist"


class BankCardDoesNotExistException(APIException):
    status_code = HTTPStatus.NOT_FOUND
    default_detail = "Card does not exist"


class TokenException(APIException):
    status_code = HTTPStatus.UNPROCESSABLE_CONTENT
    default_detail = "token invalid or expired"


class RefreshRequiredException(APIException):
    status_code = HTTPStatus.BAD_REQUEST
    default_detail = "refresh required"


class IntegrityException(APIException):
    status_code = HTTPStatus.BAD_REQUEST
    default_detail = "db error"
