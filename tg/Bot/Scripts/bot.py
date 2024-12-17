import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import F
from tg.Bot.Scripts.db import DBOperator
import logging
from tg.Bot.Scripts.post_status import PostStatus

logging.basicConfig(level=logging.INFO)

API_TOKEN = '7743955009:AAHjuvBY-_U_-pCql3W-4TWzAz7hbNU5A3Q'


class BotHandler:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.router = Router()
        self.operator = DBOperator()
        self.ADMINS = self.operator.get_admin_ids()
        self.setup_handlers()
        self.topic = ""
        self.posts = []

        self.start_keyboard = self.get_start_keyboard()
        self.moderation_keyboard = self.get_moderation_keyboard()
        self.continue_keyboard = self.get_continue_keyboard()
        self.return_keyboard = self.get_return_keyboard()

    def setup_handlers(self):
        self.router.message(CommandStart())(self.cmd_start)
        self.router.message(F.text == "В главное меню")(self.cmd_start)
        self.router.message(F.text == "Модерировать посты")(self.handle_moderation)
        self.router.message(F.text == "Продолжить модерацию")(self.handle_moderation)
        self.router.message(F.text == "Принять пост")(self.handle_accept)
        self.router.message(F.text == "Отклонить пост")(self.handle_decline)
        self.router.callback_query(F.data.startswith("chose"))(self.chose_topic)

    @staticmethod
    def get_start_keyboard():
        keyboard = ReplyKeyboardBuilder()
        keyboard.add(KeyboardButton(text="Модерировать посты"))
        return keyboard.as_markup(resize_keyboard=True)

    @staticmethod
    def get_moderation_keyboard():
        keyboard = ReplyKeyboardBuilder()
        keyboard.add(KeyboardButton(text="Принять пост"))
        keyboard.add(KeyboardButton(text="Отклонить пост"))
        return keyboard.as_markup(resize_keyboard=True)

    @staticmethod
    def get_continue_keyboard():
        keyboard = ReplyKeyboardBuilder()
        keyboard.add(KeyboardButton(text="Продолжить модерацию"))
        keyboard.add(KeyboardButton(text="В главное меню"))
        return keyboard.as_markup(resize_keyboard=True)

    @staticmethod
    def get_return_keyboard():
        keyboard = ReplyKeyboardBuilder()
        keyboard.add(KeyboardButton(text="В главное меню"))
        return keyboard.as_markup(resize_keyboard=True)

    def get_topics_keyboard(self):
        keyboard = InlineKeyboardBuilder()
        for topic in self.operator.topics.keys():
            keyboard.add(InlineKeyboardButton(text=topic, callback_data=f"chose_{topic}"))
        keyboard.adjust(1)
        return keyboard.as_markup()

    async def cmd_start(self, message: types.Message):
        await message.answer("Привет! Выбери тему постов:", reply_markup=self.get_topics_keyboard())

    async def chose_topic(self, callback_query: types.CallbackQuery):
        self.topic = callback_query.data.split("_", 1)[1]
        await callback_query.message.answer("Вы выбрали тему " + f"{self.topic}", reply_markup=self.continue_keyboard)
        await callback_query.answer()

    async def handle_moderation(self, message: types.Message):
        user_id = message.from_user.id
        if user_id not in self.ADMINS:
            await message.answer("Эта команда доступна только администраторам.")
            return
        if self.topic == "":
            await message.answer("Тема постов не выбрана", reply_markup=self.return_keyboard)
        else:
            self.posts = self.operator.get_posts_by_topic(self.topic)
            if self.posts:
                post = self.posts[0]
                await message.answer("Содержание поста: " + f"{post.content}", reply_markup=self.moderation_keyboard)
            else:
                await message.answer("Нет доступных постов для модерации.")

    async def handle_accept(self, message: types.Message):
        post = self.posts.pop(0)
        post.status = PostStatus.ACCEPTED
        self.operator.update_post(post)
        await message.answer("Пост принят!", reply_markup=self.continue_keyboard)

    async def handle_decline(self, message: types.Message):
        post = self.posts.pop(0)
        post.status = PostStatus.DECLINED
        self.operator.update_post(post)
        await message.answer("Пост отклонён!", reply_markup=self.continue_keyboard)

    async def run(self):
        self.dp.include_router(self.router)
        await self.dp.start_polling(self.bot)


if __name__ == "__main__":
    bot_handler = BotHandler(API_TOKEN)
    asyncio.run(bot_handler.run())
