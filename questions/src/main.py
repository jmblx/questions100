from fastapi import FastAPI

from questions.router import router as questions_router

app = FastAPI(title="requests proceed API")

app.include_router(questions_router)
