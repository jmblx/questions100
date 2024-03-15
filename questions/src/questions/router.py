from io import BytesIO

import pandas as pd
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy import select, func, delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from questions.models import Category, Question

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(), session: AsyncSession = Depends(get_async_session)):
    if file.filename.endswith('.xlsx'):
        contents = await file.read()
        data = BytesIO(contents)
        xls = pd.ExcelFile(data)
        for sheet_name in xls.sheet_names:
            data_frame = pd.read_excel(xls, sheet_name)

            try:
                category = await session.execute(select(Category).where(Category.name == sheet_name))
                category = category.scalar_one()
            except NoResultFound:
                category = Category(name=sheet_name)
                session.add(category)
                await session.commit()

            for index, row in data_frame.iterrows():
                question = Question(
                    initials=str(row['ФИО']),
                    place=str(row['Место работы/учёбы']),
                    position=str(row['Должность/курс']),
                    text=str(row['Вопрос']),
                    category_id=category.id
                )
                session.add(question)

            await session.commit()

        return {"message": "Data uploaded successfully"}


@router.get("/get_random/{cat_id}")
async def get_random_question(cat_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        random_question_query = await session.execute(
            select(Question).where(Question.category_id == cat_id).order_by(func.random()).limit(1)
        )
        random_question = random_question_query.scalars().first()

        if random_question is None:
            raise HTTPException(status_code=404, detail="Question not found")

        stmt = (
            delete(Question).where(Question.id == random_question.id)
        )
        await session.execute(stmt)
        await session.commit()
        return {
            "id": random_question.id,
            "initials": random_question.initials,
            "place": random_question.place,
            "position": random_question.position,
            "text": random_question.text,
            "category_id": random_question.category_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cats")
async def get_cats(session: AsyncSession = Depends(get_async_session)):
    query = select(Category)
    result = await session.execute(query)
    categories = result.scalars().all()
    return [{"id": category.id, "name": category.name} for category in categories]

