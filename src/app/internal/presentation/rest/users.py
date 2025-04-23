from http import HTTPStatus

from django.db import IntegrityError
from ninja_extra import api_controller, http_delete, http_get, http_post, http_put
from ninja_jwt.authentication import JWTAuth

from app.internal.db.models.user_data import TelegramUser
from app.internal.domain.schemas import error_handler
from app.internal.domain.schemas.users import DeleteUserSchema, MessageUserSchema, TelegramUserSchema


@api_controller("/users", tags=["Users"], auth=JWTAuth())
class Users:
    @http_get("/", response={HTTPStatus.OK: list[TelegramUserSchema]})
    def get_users(self):
        return HTTPStatus.OK, TelegramUser.objects.all()

    @http_get("/{id}", response={HTTPStatus.OK: TelegramUserSchema})
    def get_user(self, id: int):
        try:
            return HTTPStatus.OK, TelegramUser.objects.get(id=id)
        except TelegramUser.DoesNotExist:
            raise error_handler.TelegramUserDoesNotExistException

    @http_post("/", response={HTTPStatus.OK: MessageUserSchema})
    def post_users(self, payload: TelegramUserSchema):
        try:
            user, created = TelegramUser.objects.get_or_create(
                id=payload.id,
                defaults={
                    "username": payload.username,
                    "full_name": payload.full_name,
                    "phone_number": payload.phone_number,
                    "list_of_favourites": payload.list_of_favourites,
                },
            )
            if not created:
                return HTTPStatus.OK, {"message": "user already exist", "id": user.id, "username": user.username}
            return HTTPStatus.OK, {"message": "user created", "id": user.id, "username": user.username}
        except IntegrityError:
            raise error_handler.IntegrityException

    @http_put("/{id}", response={HTTPStatus.OK: MessageUserSchema})
    def put_user(self, id: int, payload: TelegramUserSchema):
        try:
            user, created = TelegramUser.objects.update_or_create(
                id=id,
                defaults={
                    "username": payload.username,
                    "full_name": payload.full_name,
                    "phone_number": payload.phone_number,
                    "list_of_favourites": payload.list_of_favourites,
                },
            )
            if not created:
                return HTTPStatus.OK, {"message": "user updated", "id": user.id, "username": user.username}
            return HTTPStatus.OK, {"message": "user created", "id": user.id, "username": user.username}
        except IntegrityError:
            raise error_handler.IntegrityException

    @http_delete("/{id}", response={HTTPStatus.OK: DeleteUserSchema})
    def delete_user(self, id: int):
        try:
            user = TelegramUser.objects.get(id=id)
            user.delete()
            return HTTPStatus.OK, {"message": f"user {id} deleted"}
        except TelegramUser.DoesNotExist:
            raise error_handler.TelegramUserDoesNotExistException
