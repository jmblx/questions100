import json
import os

import aiohttp
from aiogram import Router, F, types
from aiogram.filters import Command, or_f
from aiogram.fsm import state
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import requests as rq

user_private_router = Router()

categories_response = rq.get("http://localhost:8000/troubles/get_all_categories")
categories_data = json.loads(categories_response.text)


def create_categories_message(categories):
    message_text = "Выберите категорию проблемы:\n"
    for value in categories:
        message_text += f"{value['id']}) {value['name']}\n"
    return message_text


class GetQuestion(StatesGroup):
    cat = State()


@user_private_router.message(
    or_f(
        Command("random_question"),
        (F.text.lower().contains("вопрос"))
    )
)
async def get_random_questions(message: types.Message, state: FSMContext):
    await message.answer(create_categories_message(categories_data))
    await state.set_state(GetQuestion.cat)


@user_private_router.message(GetQuestion.cat, F.text)
async def process_category_id(message: types.Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:8000/questions/get_random/{message.text}"
        async with session.get(url) as response:
            data = await response.json()
    await message.answer(f"Вопрос: {data.get('text')}")
    await state.clear()
