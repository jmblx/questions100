from io import BytesIO

import pandas as pd
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy import select, func, delete, and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from redis_config import get_redis
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


@router.get("/get_random/{cat_id}/{user_id}")
async def get_random_question(
        cat_id: int,
        user_id: str,
        session: AsyncSession = Depends(get_async_session),
        redis=Depends(get_redis)
):
    try:
        redis_key = f"{user_id}:{cat_id}"

        viewed_questions = await redis.smembers(redis_key)
        viewed_questions = {int(q) for q in viewed_questions if q.isdigit()}
        random_question_query = await session.execute(
            select(Question)
            .where(and_(Question.category_id == cat_id, ~Question.id.in_(viewed_questions)))
            .order_by(func.random())
            .limit(1)
        )
        random_question = random_question_query.scalars().first()
        await redis.sadd(redis_key, str(random_question.id))
        if random_question is None:
            await redis.delete(redis_key)
            raise HTTPException(status_code=404, detail="No more new questions in this category")

        await redis.sadd(redis_key, str(random_question.id))

        return {
            "id": random_question.id,
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

