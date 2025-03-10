from phonenumbers import NumberParseException, format_out_of_country_calling_number, is_valid_number, parse

from app.internal.models.user_data import TelegramUser


async def get_user(chat_id: int) -> TelegramUser:
    return await TelegramUser.objects.aget(id=chat_id)


async def save_user(chat_id: int, name: str, nickname: str) -> None:
    await TelegramUser.objects.aupdate_or_create(id=chat_id, full_name=name, username=nickname)


async def set_phone(chat_id: int, number: str, code: str) -> None:
    if is_valid_number(parse(number=number, region=code)):
        await TelegramUser.objects.aupdate(
            id=chat_id,
            phone_number=format_out_of_country_calling_number(parse(number=number, region=code), code),
        )
    else:
        raise NumberParseException(0, "it's not base error:is not valid number")
