from http import HTTPStatus

from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from ninja_extra import api_controller, http_delete, http_get, http_post, http_put
from ninja_extra.pagination import LimitOffsetPagination, paginate
from ninja_jwt.authentication import JWTAuth

from app.internal.db.models.user_data import TelegramUser
from app.internal.domain.schemas import error_handler
from app.internal.domain.schemas.users import (
    DeleteSchema,
    MessageUserSchema,
    PostTelegramUserSchema,
    PutTelegramUserSchema,
    TelegramUserSchema,
)
from app.internal.domain.services.user_service import UserService


@api_controller("/users", tags=["Users"], auth=JWTAuth())
class Users:
    def __init__(self):
        self.user_service = UserService()

    @http_get("/", response={HTTPStatus.OK: list[TelegramUserSchema]})
    @paginate(LimitOffsetPagination)
    def get_users(self):
        return HTTPStatus.OK, self.user_service.get_users()

    @http_get("/{id}", response={HTTPStatus.OK: TelegramUserSchema})
    def get_user(self, id: int):
        try:
            return HTTPStatus.OK, self.user_service.get_user_by_id(id)
        except TelegramUser.DoesNotExist:
            raise error_handler.TelegramUserDoesNotExistException

    @http_post("/", response={HTTPStatus.OK: MessageUserSchema})
    def post_users(self, payload: PostTelegramUserSchema):
        try:
            user, created = self.user_service.get_or_create_user(payload.id, payload.username, payload.full_name)
            if not created:
                return HTTPStatus.OK, {"message": "user already exist", "id": user.id, "username": user.username}
            return HTTPStatus.OK, {"message": "user created", "id": user.id, "username": user.username}
        except IntegrityError:
            raise error_handler.IntegrityException

    @http_put("/{id}", response={HTTPStatus.OK: MessageUserSchema})
    def put_user(self, id: int, payload: PutTelegramUserSchema):
        try:
            user, created = self.user_service.save_user(id, payload.username, payload.full_name)
            if not created:
                return HTTPStatus.OK, {"message": "user updated", "id": user.id, "username": user.username}
            return HTTPStatus.OK, {"message": "user created", "id": user.id, "username": user.username}
        except IntegrityError:
            raise error_handler.IntegrityException

    @http_delete("/{id}", response={HTTPStatus.NO_CONTENT: DeleteSchema})
    def delete_user(self, id: int):
        try:
            self.user_service.delete_user_by_id(id)
            return (HTTPStatus.NO_CONTENT,)
        except TelegramUser.DoesNotExist:
            raise error_handler.TelegramUserDoesNotExistException
        except ProtectedError:
            raise error_handler.ProtectedDeleteException
