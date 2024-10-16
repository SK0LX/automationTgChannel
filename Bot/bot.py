import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import F
import logging

logging.basicConfig(level=logging.INFO)

API_TOKEN = '7743955009:AAHjuvBY-_U_-pCql3W-4TWzAz7hbNU5A3Q'
ADMINS = [927617173]

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


def get_keyboard():
    keyboard = ReplyKeyboardBuilder()

    keyboard.add(KeyboardButton(text="Команда 1"))
    keyboard.add(KeyboardButton(text="Команда 2"))

    return keyboard.as_markup(resize_keyboard=True)


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выбери команду:", reply_markup=get_keyboard())


@dp.message(F.text == "Команда 1")
async def handle_command_1(message: types.Message):
    user_id = message.from_user.id
    if user_id in ADMINS:
        await message.answer("Вы выбрали Команду 1! (Только для админов)")
    else:
        await message.answer("Эта команда доступна только администраторам.")


@dp.message(F.text == "Команда 2")
async def handle_command_2(message: types.Message):
    await message.answer("Вы выбрали Команду 2!")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
