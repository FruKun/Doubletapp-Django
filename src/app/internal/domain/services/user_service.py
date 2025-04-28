from phonenumbers import NumberParseException, format_out_of_country_calling_number, is_valid_number, parse

from app.internal.db.models.bank_data import BankAccount, BankCard
from app.internal.db.models.user_data import TelegramUser
from app.internal.db.repositories.account_repository import AccountRepository
from app.internal.db.repositories.card_repository import CardRepository
from app.internal.db.repositories.user_repository import UserRepository
from app.internal.domain.services import CustomErrors


class UserService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.account_repo = AccountRepository()
        self.card_repo = CardRepository()

    async def aget_user_by_id(self, id: int) -> TelegramUser:
        if user := await self.user_repo.aget_user_by_id(id):
            return user
        raise TelegramUser.DoesNotExist

    def get_user_by_id(self, id: int) -> TelegramUser:
        if user := self.user_repo.get_user_by_id(id):
            return user
        raise TelegramUser.DoesNotExist

    async def aget_user_by_username(self, username: str) -> TelegramUser:
        if user := await self.user_repo.aget_user_by_username(username):
            return user
        raise TelegramUser.DoesNotExist

    async def aget_card_by_number(self, number: str) -> BankCard:
        if card := await self.card_repo.aget_card_by_number(number):
            return card
        raise BankCard.DoesNotExist

    async def aget_account_by_number(self, number: str) -> BankAccount:
        if account := await self.account_repo.aget_account_by_number(number):
            return account
        raise BankAccount.DoesNotExist

    def get_users(self) -> list[TelegramUser]:
        return self.user_repo.get_users()

    def get_or_create_user(self, id: int, username: str, full_name: str) -> tuple((TelegramUser, bool)):
        return self.user_repo.get_or_create_user(id, username, full_name)

    def save_user(self, id: int, username: str, full_name: str) -> None:
        return self.user_repo.save_user(id, username, full_name)

    async def asave_user(self, id: int, username: str, full_name: str) -> None:
        return await self.user_repo.asave_user(id, username, full_name)

    def delete_user_by_id(self, id: int) -> None:
        user = self.get_user_by_id(id)
        user.delete()

    async def set_phone(self, chat_id: int, number: str, code: str) -> None:
        if is_valid_number(parse(number=number, region=code)):
            user = await self.aget_user_by_id(chat_id)
            user.phone_number = format_out_of_country_calling_number(parse(number=number, region=code), code)
            await user.asave()
        else:
            raise NumberParseException(0, "is not valid number")

    async def add_favorite(self, user: TelegramUser, favorite: str) -> None:
        if favorite.isdigit() and len(favorite) == 16:
            await self.aget_card_by_number(favorite)
        elif favorite.isdigit() and len(favorite) == 20:
            await self.aget_account_by_number(favorite)
        elif not favorite.isdigit() and len(favorite) < 255:
            if favorite[0] == "@":
                favorite = favorite[1::]
            await self.aget_user_by_username(favorite)
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
