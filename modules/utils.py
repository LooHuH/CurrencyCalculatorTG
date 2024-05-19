import asyncio
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup


def user_from(source):
    return source.from_user.id


async def answer_and_delete(
        message: Message,
        delete_after: int,
        text: str,
        reply_markup: ReplyKeyboardMarkup = None
):
    temp_message = await message.answer(
        text=text,
        reply_markup=reply_markup
    )
    await asyncio.sleep(delete_after)
    await temp_message.delete()


def convert_to_currency(
        value,
        currency: str = '$',
        thousand_separator: str = ',',
        float_separator: str = '.'
):
    value_split = str(format(value, '.16f')).split('.')
    main_part = None
    float_part = None
    if len(value_split) > 1:
        main_part = value_split[0]
        float_part = value_split[1][:2]
    else:
        main_part = value_split
    main_part_len = len(main_part)
    if main_part_len > 1:
        for i in range(main_part_len):
            index = main_part_len - i
            if (i % 3 == 0
                    and index != main_part_len):
                main_part = main_part[:index] + thousand_separator + main_part[index:]
    output = currency + main_part
    if float_part is not None:
        output += float_separator + float_part

    return output
