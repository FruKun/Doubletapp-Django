from http import HTTPStatus

from ninja_extra import api_controller, http_post
from ninja_jwt.tokens import RefreshToken, TokenError

from app.internal.db.models.user_data import TelegramUser
from app.internal.domain.schemas import error_handler
from app.internal.domain.schemas.auth import (
    LoginPayloadSchema,
    MyTokenObtainPairOutputSchema,
    MyTokenRefreshOutputSchema,
    RefreshPayloadSchema,
)


@api_controller(
    "/token",
    tags=["Auth"],
)
class Tokens:
    @http_post(
        "/login/",
        response={
            HTTPStatus.OK: MyTokenObtainPairOutputSchema,
        },
    )
    def login(self, payload: LoginPayloadSchema):
        id = payload.id
        try:
            user = TelegramUser.objects.get(id=id)
            refresh = RefreshToken.for_user(user)
            return HTTPStatus.OK, {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

        except TelegramUser.DoesNotExist:
            raise error_handler.TelegramUserDoesNotExistException
        except TokenError:
            raise error_handler.TokenException

    @http_post(
        "/refresh/",
        response={
            HTTPStatus.OK: MyTokenRefreshOutputSchema,
        },
    )
    def refresh_token(self, payload: RefreshPayloadSchema):
        refresh = payload.refresh
        if not refresh:
            raise error_handler.RefreshRequiredException
        try:

            refresh = RefreshToken(refresh)
            return HTTPStatus.OK, {
                "access": str(refresh.access_token),
            }
        except TokenError:
            raise error_handler.TokenException
