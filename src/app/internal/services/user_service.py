from phonenumbers import NumberParseException, format_out_of_country_calling_number, is_valid_number, parse

from app.internal.models.user_data import TelegramUser
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
    if not favorite.isdigit():
        if favorite[0] == "@":
            favorite = favorite[1::]
        await TelegramUser.objects.aget(username=favorite)
        favourites = user.list_of_favourites
        favourites["usernames"].append(favorite)
        favourites["usernames"] = list(set(favourites["usernames"]))
        await TelegramUser.objects.aupdate(id=chat_id, list_of_favourites=favourites)
    elif len(favorite) == 16:
        await get_card(favorite)
        favourites = user.list_of_favourites
        favourites["cards"].append(favorite)
        favourites["cards"] = list(set(favourites["cards"]))
        await TelegramUser.objects.aupdate(id=chat_id, list_of_favourites=favourites)
    elif len(favorite) == 20:
        await get_account(favorite)
        favourites = user.list_of_favourites
        favourites["accounts"].append(favorite)
        favourites["accounts"] = list(set(favourites["accounts"]))
        await TelegramUser.objects.aupdate(id=chat_id, list_of_favourites=favourites)
    else:
        raise Exception


async def del_favorite(chat_id: int, favorite: str) -> None:
    user = await get_user(chat_id)
    if not favorite.isdigit():
        if favorite[0] == "@":
            favorite = favorite[1::]
        favourites = user.list_of_favourites
        favourites["usernames"].remove(favorite)
        favourites["usernames"] = list(set(favourites["usernames"]))
        await TelegramUser.objects.aupdate(id=chat_id, list_of_favourites=favourites)
    elif len(favorite) == 16:
        favourites = user.list_of_favourites
        favourites["cards"].remove(favorite)
        favourites["cards"] = list(set(favourites["cards"]))
        await TelegramUser.objects.aupdate(id=chat_id, list_of_favourites=favourites)
    elif len(favorite) == 20:
        favourites = user.list_of_favourites
        favourites["accounts"].remove(favorite)
        favourites["accounts"] = list(set(favourites["accounts"]))
        await TelegramUser.objects.aupdate(id=chat_id, list_of_favourites=favourites)
    else:
        raise Exception
