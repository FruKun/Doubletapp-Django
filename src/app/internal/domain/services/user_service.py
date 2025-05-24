from phonenumbers import NumberParseException, format_out_of_country_calling_number, is_valid_number, parse

from app.internal.db.models.bank_data import BankAccount, BankCard
from app.internal.db.models.user_data import TelegramUser
from app.internal.domain.services import CustomErrors


class UserService:
    def get_users(self) -> list[TelegramUser]:
        return [i for i in TelegramUser.objects.all()]

    def save_user(self, id: int, username: str, full_name: str) -> (TelegramUser, bool):
        return TelegramUser.objects.update_or_create(id=id, defaults={"username": username, "full_name": full_name})

    async def asave_user(self, id: int, username: str, full_name: str) -> (TelegramUser, bool):
        return await TelegramUser.objects.aupdate_or_create(
            id=id, defaults={"username": username, "full_name": full_name}
        )

    def delete_user_by_id(self, id: int) -> None:
        user = TelegramUser.objects.get(id=id)
        user.delete()

    async def set_phone(self, chat_id: int, number: str, code: str) -> None:
        if is_valid_number(parse(number=number, region=code)):
            user = await TelegramUser.objects.aget(id=chat_id)
            user.phone_number = format_out_of_country_calling_number(parse(number=number, region=code), code)
            await user.asave()
        else:
            raise NumberParseException(0, "is not valid number")

    async def add_favorite(self, user: TelegramUser, favorite: str) -> None:
        if favorite.isdigit() and len(favorite) == 16:
            await BankCard.objects.aget(number=favorite)
        elif favorite.isdigit() and len(favorite) == 20:
            await BankAccount.objects.aget(number=favorite)
        elif not favorite.isdigit() and len(favorite) < 255:
            if favorite[0] == "@":
                favorite = favorite[1::]
            await TelegramUser.objects.aget(username=favorite)
        else:
            raise CustomErrors.InvalidFieldValue
        user.list_of_favourites.append(favorite)
        user.list_of_favourites = list(set(user.list_of_favourites))
        await user.asave()

    async def del_favorite(self, user: TelegramUser, favorite: str) -> None:
        if favorite.isdigit() and not (len(favorite) == 16 or len(favorite) == 20):
            raise CustomErrors.InvalidFieldValue
        elif len(favorite) > 255:
            raise CustomErrors.InvalidFieldValue
        if favorite[0] == "@":
            favorite = favorite[1::]
        user.list_of_favourites.remove(favorite)
        user.list_of_favourites = list(set(user.list_of_favourites))
        await user.asave()
