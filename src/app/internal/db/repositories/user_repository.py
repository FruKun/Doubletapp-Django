from typing import Optional

from app.internal.db.models.user_data import TelegramUser


class UserRepository:
    def get_user_by_id(self, id: int) -> Optional[TelegramUser]:
        return TelegramUser.objects.filter(id=id).first()

    async def aget_user_by_id(self, id: int) -> Optional[TelegramUser]:
        return await TelegramUser.objects.filter(id=id).afirst()

    def get_user_by_username(self, username: str) -> Optional[TelegramUser]:
        return TelegramUser.objects.filter(username=username).first()

    async def aget_user_by_username(self, username: str) -> Optional[TelegramUser]:
        return await TelegramUser.objects.filter(username=username).afirst()

    def save_user(self, id: int, username: str, full_name: str) -> None:
        return TelegramUser.objects.update_or_create(id=id, defaults={"username": username, "full_name": full_name})

    async def asave_user(self, id: int, username: str, full_name: str) -> None:
        return await TelegramUser.objects.aupdate_or_create(
            id=id, defaults={"username": username, "full_name": full_name}
        )

    def get_or_create_user(self, id: int, username: str, full_name: str) -> tuple((TelegramUser, bool)):
        return TelegramUser.objects.get_or_create(id=id, defaults={"username": username, "full_name": full_name})

    def get_users(self) -> list[TelegramUser]:
        return TelegramUser.objects.all()
