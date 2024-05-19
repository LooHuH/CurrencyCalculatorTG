from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, BotCommand, BotCommandScopeDefault
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from modules.config import ADMIN_IDS
from modules.utils import user_from, answer_and_delete, convert_to_currency
from modules.data import Data
from modules.rate_parser import get_rate


async def set_up(dp: Dispatcher, bot: Bot):
    commands = BotCommands(dp, bot)
    await bot.set_my_commands(commands.list, BotCommandScopeDefault())
    dp.startup.register(log_bot_start)
    dp.message.register(commands.start, Command(commands=['start']))
    dp.callback_query.register(commands.main_menu_callback_handler, F.data.startswith('main_menu_'))
    dp.callback_query.register(commands.admin_menu_callback_handler, F.data.startswith('admin_menu_'))


def log_bot_start():
    print('Bot started!')


class BotCommands:
    def __init__(self, dp: Dispatcher, bot: Bot):
        self.dp = dp
        self.bot = bot
        self.list = [
            BotCommand(
                command='start',
                description='Start menu'
            )
        ]

    def remove_temp_handlers(self):
        if len(self.dp.message.handlers) > 1:
            self.dp.message.handlers.pop()

    async def start(self, message: Message = None, user_id: int = None):
        self.remove_temp_handlers()
        if user_id is None:
            user_id = user_from(message)
        builder = InlineKeyboardBuilder()
        builder.button(
            text='💴 Калькулятор валют 💴',
            callback_data='main_menu_calculator'
        )
        if user_id in ADMIN_IDS:
            builder.button(
                text='🕶 Админ панель 🕶',
                callback_data='main_menu_admin_menu'
            )
        builder.adjust(1)
        markup = builder.as_markup()
        await message.answer(
            text=f"Привет, рандомный чел! 👋\n"
                 f'🔽 Выбери из опций ниже 🔽',
            reply_markup=markup
        )

    async def main_menu_callback_handler(self, callback: CallbackQuery):
        self.remove_temp_handlers()
        if callback.data == 'main_menu_calculator':
            await self.calculator(callback)
        if (callback.data == 'main_menu_admin_menu'
                and user_from(callback) in ADMIN_IDS):
            await self.admin_menu(callback)

    async def calculator(self, callback: CallbackQuery):
        self.remove_temp_handlers()

        temp_message = await callback.message.answer(
            text='⌨️ Введи цену в Юанях ⌨️'
        )

        @self.dp.message()
        async def input_handler(message: Message):
            try:
                entered_price = float(message.text)
                data = Data()
                converted_price = (entered_price * data.rate) + data.fee
                await message.answer(
                    text=f'Цена в Юанях - {convert_to_currency(entered_price, currency="¥")} \n'
                         f'Цена в Рублях - {convert_to_currency(converted_price, currency="₽")}'
                )
                self.remove_temp_handlers()
                await callback.message.delete()
            except TypeError:
                await send_not_number_error(message)
            await temp_message.delete()
            await message.delete()

        async def send_not_number_error(message: Message):
            await answer_and_delete(
                message=message,
                delete_after=1,
                text='❗️ Введи число ❗️',
            )

    async def admin_menu(self, callback: CallbackQuery):
        self.remove_temp_handlers()
        builder = InlineKeyboardBuilder()
        builder.button(
            text='🧮 Изменить курс юаня 🧮',
            callback_data='admin_menu_change_rate'
        )
        builder.button(
            text='🧮 Изменить наценку в рублях 🧮',
            callback_data='admin_menu_change_fee'
        )
        builder.button(
            text='❌ Сбросить курс ❌',
            callback_data='admin_menu_reset_rate'
        )
        builder.button(
            text='❌ Сбросить наценку ❌',
            callback_data='admin_menu_reset_fee'
        )
        data = Data()
        rate = convert_to_currency(data.rate, currency='₽')
        if data.fee:
            fee = convert_to_currency(data.fee, currency='₽')
        else:
            fee = 'Отсутствует'
        builder.button(
            text='◀️ Назад',
            callback_data='admin_menu_back'
        )
        builder.adjust(1)
        markup = builder.as_markup()
        text = (f'🕶 Админ панель 🕶 \n'
                f'Курс для 1-ого юаня - {rate} \n'
                f'Наценка - {fee}')
        try:
            await callback.message.edit_text(
                text=text,
                reply_markup=markup
            )
        except Exception:
            await callback.message.answer(
                text=text,
                reply_markup=markup
            )

    async def admin_menu_callback_handler(self, callback: CallbackQuery):
        self.remove_temp_handlers()
        if user_from(callback) in ADMIN_IDS:
            if callback.data == 'admin_menu_change_rate':
                temp_message = await callback.message.answer(
                    text='⌨️ Введи курс в Юанях ⌨️'
                )

                @self.dp.message()
                async def input_handler(message: Message):
                    try:
                        rate = float(message.text)
                        self.remove_temp_handlers()
                        data = Data()
                        if rate == data.rate:
                            await callback.message.delete()
                        data.set_rate(rate)
                        await self.admin_menu(callback)
                    except TypeError:
                        await send_not_number_error(message)
                        return
                    except Exception:
                        pass
                    try:
                        await temp_message.delete()
                        await message.delete()
                    except Exception:
                        pass

                async def send_not_number_error(message: Message):
                    await answer_and_delete(
                        message=message,
                        delete_after=1,
                        text='❗️ Введи число ❗️',
                    )

            elif callback.data == 'admin_menu_change_fee':
                temp_message = await callback.message.answer(
                    text='⌨️ Введи наценку в рублях ⌨️'
                )

                @self.dp.message()
                async def input_handler(message: Message):
                    try:
                        fee = float(message.text)
                        self.remove_temp_handlers()
                        data = Data()
                        if fee == data.fee:
                            await callback.message.delete()
                        data.set_fee(fee)
                        await self.admin_menu(callback)
                    except TypeError:
                        await send_not_number_error(message)
                        return
                    except Exception:
                        pass
                    try:
                        await temp_message.delete()
                        await message.delete()
                    except Exception:
                        pass

                async def send_not_number_error(message: Message):
                    await answer_and_delete(
                        message=message,
                        delete_after=1,
                        text='❗️ Введи число ❗️',
                    )

            elif callback.data == 'admin_menu_reset_rate':
                Data().set_rate(0)
                await callback.message.delete()
                await self.admin_menu(callback)

            elif callback.data == 'admin_menu_reset_fee':
                Data().set_fee(0)
                await callback.message.delete()
                await self.admin_menu(callback)

            elif callback.data == 'admin_menu_back':
                await callback.message.delete()
                await self.start(callback.message, user_from(callback))
