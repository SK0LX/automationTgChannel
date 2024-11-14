import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import F
from db import DBOperator
import logging
from post_status import PostStatus

logging.basicConfig(level=logging.INFO)

API_TOKEN = '7743955009:AAHjuvBY-_U_-pCql3W-4TWzAz7hbNU5A3Q'


class BotHandler:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.operator = DBOperator()
        self.ADMINS = self.operator.get_admin_ids()
        self.setup_handlers()
        self.posts = []

    def setup_handlers(self):
        self.dp.message(CommandStart())(self.cmd_start)
        self.dp.message(F.text == "В главное меню")(self.cmd_start)
        self.dp.message(F.text == "Модерировать посты")(self.handle_moderation)
        self.dp.message(F.text == "Продолжить модерацию")(self.handle_moderation)
        self.dp.message(F.text == "Принять пост")(self.handle_accept)
        self.dp.message(F.text == "Отклонить пост")(self.handle_decline)

    def get_start_keyboard(self):
        keyboard = ReplyKeyboardBuilder()
        keyboard.add(KeyboardButton(text="Модерировать посты"))
        return keyboard.as_markup(resize_keyboard=True)

    def get_moderation_keyboard(self):
        keyboard = ReplyKeyboardBuilder()
        keyboard.add(KeyboardButton(text="Принять пост"))
        keyboard.add(KeyboardButton(text="Отклонить пост"))
        return keyboard.as_markup(resize_keyboard=True)

    def get_continue_keyboard(self):
        keyboard = ReplyKeyboardBuilder()
        keyboard.add(KeyboardButton(text="Продолжить модерацию"))
        keyboard.add(KeyboardButton(text="В главное меню"))
        return keyboard.as_markup(resize_keyboard=True)

    async def cmd_start(self, message: types.Message):
        await message.answer("Привет! Выбери команду:", reply_markup=self.get_start_keyboard())

    async def handle_moderation(self, message: types.Message):
        user_id = message.from_user.id
        if user_id not in self.ADMINS:
            await message.answer("Эта команда доступна только администраторам.")
            return
        self.posts = self.operator.get_posts()
        if self.posts:
            post = self.posts[0]
            await message.answer(f"Содержание поста: {post.content}", reply_markup=self.get_moderation_keyboard())
        else:
            await message.answer("Нет доступных постов для модерации.")

    async def handle_accept(self, message: types.Message):
        post = self.posts.pop(0)
        post.status = PostStatus.ACCEPTED
        self.operator.update_post(post)
        await message.answer("Пост принят!", reply_markup=self.get_continue_keyboard())

    async def handle_decline(self, message: types.Message):
        post = self.posts.pop(0)
        post.status = PostStatus.DECLINED
        self.operator.update_post(post)
        await message.answer("Пост отклонён!", reply_markup=self.get_continue_keyboard())

    async def run(self):
        await self.dp.start_polling(self.bot)


if __name__ == "__main__":
    bot_handler = BotHandler(API_TOKEN)
    asyncio.run(bot_handler.run())