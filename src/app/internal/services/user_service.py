from phonenumbers import NumberParseException, format_out_of_country_calling_number, is_valid_number, parse

from app.internal.models.user_data import UserData


async def get_user(chat_id) -> UserData:
    return await UserData.objects.aget(id=chat_id)


async def save_user(chat_id, name, nickname) -> None:
    await UserData.objects.aupdate_or_create(id=chat_id, full_name=name, username=nickname)


async def set_phone(chat_id: int, number: str, code: str) -> None:
    if is_valid_number(parse(number=number, region=code)):
        await UserData.objects.aupdate(
            id=chat_id,
            phone_number=format_out_of_country_calling_number(parse(number=number, region=code), code),
        )
    else:
        raise NumberParseException(0, "it's not base error:is not valid number")
