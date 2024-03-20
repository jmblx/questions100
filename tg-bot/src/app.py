import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from dotenv import find_dotenv, load_dotenv

from kbds.reply import default_kb

from handlers.questions import user_private_router as delete_recipe_router


load_dotenv(find_dotenv())

ALLOWED_UPDATES = ['message, edited_message']

bot_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(default=bot_properties, token=os.getenv('TOKEN'))
bot.my_admins_list = []

storage = MemoryStorage()

dp = Dispatcher(storage=storage)

dp.include_router(delete_recipe_router)


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(
        """
Привет! Я могу отправить вопросы по категории и получать их от других пользователей.
        """,
        reply_markup=default_kb
    )


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

asyncio.run(main())
