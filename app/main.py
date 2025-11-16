from contextlib import asynccontextmanager
import logging
from fastapi import Depends, FastAPI

from app.api.routers import data, quizzes, auth, user_settings
from app.db import models
from app.db.database import engine
# import nltk

# nltk.download('punkt')
# nltk.download('punkt_tab')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('averaged_perceptron_tagger_eng')

logging.basicConfig(
    level=2,
    format="%(asctime)-15s %(levelname)-8s %(message)s"
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield

app = FastAPI()

app.include_router(quizzes.router)
app.include_router(data.router)
app.include_router(auth.router)
app.include_router(user_settings.router)

@app.get("/")
async def root():
    return {"message": "Simple quiz generator, inspired by Duolingo. Uses public domain data to create quizzes."}


# how to run:
# *D:\dev\quiz_generator>* uvicorn app.main:app --reload