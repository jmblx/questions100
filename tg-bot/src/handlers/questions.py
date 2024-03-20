import json
import os

import aiohttp
from aiogram import Router, types, F
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton
import requests as rq
from aiogram.utils.keyboard import InlineKeyboardBuilder

user_private_router = Router()

def create_categories_keyboard(categories):
    inline_kb = InlineKeyboardBuilder()
    for cat in categories:
        callback_data = f"category:{str(cat['id'])}"
        button = InlineKeyboardButton(text=cat['name'], callback_data=callback_data)
        inline_kb.add(button)
    return inline_kb.adjust(1).as_markup()


@user_private_router.message(Command("random_question"))
async def get_random_questions(message: types.Message, state: FSMContext):
    categories_response = rq.get(f"http://{os.getenv('BACKEND')}:8000/questions/cats")
    categories_data = json.loads(categories_response.text)
    await message.answer(str(categories_data))
    await message.answer("Выберите категорию вопроса:", reply_markup=create_categories_keyboard(categories_data))


@user_private_router.callback_query(or_f(
    F.data.startswith("category:")
))
async def process_category_id(callback_query: types.CallbackQuery, state: FSMContext):
    category_id = callback_query.data.split(':')[1]
    async with aiohttp.ClientSession() as session:
        url = f"http://{os.getenv('BACKEND')}:8000/questions/get_random/{category_id}/{callback_query.from_user.id}"
        async with session.get(url) as response:
            data = await response.json()
            if response.status == 404:
                text = data.get('detail', 'No more new questions in this category')
            else:
                text = f"Вопрос: {str(data)}"
    await callback_query.message.answer(text)
    await callback_query.answer()


class UploadFileState(StatesGroup):
    waiting_for_file = State()


@user_private_router.message(Command("upload_questions"))
async def upload_file_command(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, загрузите файл с вопросами в формате .xlsx")
    await state.set_state(UploadFileState.waiting_for_file)


@user_private_router.message(UploadFileState.waiting_for_file)
async def upload_file(message: types.Message, state: FSMContext):
    if not message.document.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        await message.answer("Пожалуйста, загрузите файл в формате .xlsx")
        return

    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)
    file_path = file.file_path

    async with aiohttp.ClientSession() as session:
        url = "http://{os.getenv('BACKEND')}:8000/questions/uploadfile/"
        file_content = await message.bot.download_file(file_path)
        async with session.post(url, data={"file": file_content}) as response:
            if response.status == 200:
                await message.answer("Файл успешно загружен и обработан.")
            else:
                await message.answer("Произошла ошибка при загрузке файла.")
    await state.clear()
