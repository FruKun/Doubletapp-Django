from ninja import ModelSchema, Schema

from app.internal.db.models.user_data import TelegramUser


class TelegramUserSchema(ModelSchema):
    class Meta:
        model = TelegramUser
        fields = ["id", "username", "full_name", "phone_number", "list_of_favourites"]
        fields_optional = ["full_name", "phone_number", "list_of_favourites"]


class PostTelegramUserSchema(Schema):
    id: int
    username: str
    full_name: str


class PutTelegramUserSchema(Schema):
    username: str
    full_name: str


class MessageUserSchema(Schema):
    message: str
    id: int
    username: str


class DeleteSchema(Schema):
    pass
