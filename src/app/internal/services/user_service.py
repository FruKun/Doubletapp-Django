from phonenumbers import NumberParseException, format_out_of_country_calling_number, is_valid_number, parse

from app.internal.models.user_data import TelegramUser
from app.internal.services import CustomErrors
from app.internal.services.bank_services import get_account, get_card


async def get_user(chat_id: int) -> TelegramUser:
    return await TelegramUser.objects.aget(id=chat_id)


async def save_user(chat_id: int, name: str, nickname: str) -> None:
    await TelegramUser.objects.aupdate_or_create(id=chat_id, full_name=name, username=nickname)


async def set_phone(chat_id: int, number: str, code: str) -> None:
    if is_valid_number(parse(number=number, region=code)):
        user = await get_user(chat_id)
        user.phone_number = format_out_of_country_calling_number(parse(number=number, region=code), code)
        await user.asave()
    else:
        raise NumberParseException(0, "is not valid number")


async def add_favorite(chat_id: int, favorite: str) -> None:
    user = await get_user(chat_id)
    if favorite.isdigit() and len(favorite) == 16:
        await get_card(favorite)
    elif favorite.isdigit() and len(favorite) == 20:
        await get_account(favorite)
    elif not favorite.isdigit and len(favorite) < 255:
        if favorite[0] == "@":
            favorite = favorite[1::]
        await TelegramUser.objects.aget(username=favorite)
    else:
        raise CustomErrors.ObjectProperties
    user.list_of_favourites.append(favorite)
    user.list_of_favourites = list(set(user.list_of_favourites))
    await user.asave()


async def del_favorite(chat_id: int, favorite: str) -> None:
    user = await get_user(chat_id)
    if favorite.isdigit() and not (len(favorite) == 16 or len(favorite) == 20):
        raise CustomErrors.ObjectProperties
    elif len(favorite) > 255:
        raise CustomErrors.ObjectProperties
    if favorite[0] == "@":
        favorite = favorite[1::]
    user.list_of_favourites.remove(favorite)
    user.list_of_favourites = list(set(user.list_of_favourites))
    await user.asave()
