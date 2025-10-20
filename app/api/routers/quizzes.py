import random
import logging
from typing import List, Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import quiz_crud, text_crud, schemas
from app.db.database import SessionLocal
from app.domain.quiz import SequenceQuiz, SingleAnswerQuiz
from app.models.mappings import quiz_to_dto
from app.models.quiz import QuizDTO
from app.service.auth.dependencies import get_current_user_or_api_key
from app.service.quiz_generator.generator import QuizGenerator
from app.service.quiz_generator.generator_llm import SimpleQuizStrategyLLM
from app.service.quiz_generator.generator_strategy import SequenceQuizStrategy, SimpleQuizStrategy
from app.service.quiz_generator.tokenizer import EnglishTokenizer


router = APIRouter(
    prefix="/api/quizzes",
    tags=["quizzes"],
    dependencies=[Depends(get_current_user_or_api_key)]
)

logger = logging.getLogger(name="quizzes_router")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_data_db():
    db_texts = SessionLocal()
    try:
        yield db_texts
    finally:
        db_texts.close()


class GenerateFromTextBody(BaseModel):
    input: str = Field(..., description="A source text to generate quiz from. Text is expected to be a paragraph with correct punctuation.")
    limit: int = Field(..., description="A maximum number of quizzes to generate. Endpoint may return less if there is no reasonable quiz to generate from given text.")
    number_of_answers: int = Field(..., description="A maximum number of answers in quiz. Endpoint may return less if there is no reasonable answer to generate from given text.")
    type: Literal["simple", "sequence", "simple_llm"] = Field(..., description="A type of quizzes to generate")
    language: Literal["en"] = Field(..., description="In which language to generate quizzes")

class GenerateFromTextResponse(BaseModel):
    quizzes: List[QuizDTO]

@router.get("/")
async def get_quiz_batch(simple: int = 10, voice: int = 0, sequence: int = 0, context: int = 0, db: Session = Depends(get_db)):
    return {"message": "get batch of different quizzes"}


@router.post("/simple/from-text", response_model=GenerateFromTextResponse)
def create_simple_quiz_from_text(body: GenerateFromTextBody) -> GenerateFromTextResponse:
    try:
        strategy = SimpleQuizStrategy(tokenizer=EnglishTokenizer())
        print(body.limit, body.number_of_answers)
        quizzes = strategy.generate_many(body.input, body.limit, body.number_of_answers)
        quiz_dtos = [quiz_to_dto(q) for q in quizzes]
        print([q.model_dump() for q in quiz_dtos])

        return GenerateFromTextResponse(quizzes=quiz_dtos)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encountered error: {e}")


@router.post("/sequence/from-text")
async def get_sequence_quiz(body: GenerateFromTextBody) -> GenerateFromTextResponse:
    try:
        strategy = SequenceQuizStrategy(tokenizer=EnglishTokenizer())
        quizzes = strategy.generate_many(body.input, body.limit, body.number_of_answers)
        quiz_dtos = [quiz_to_dto(q) for q in quizzes]
        print([q.model_dump() for q in quiz_dtos])

        return GenerateFromTextResponse(quizzes=quiz_dtos)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encountered error: {e}")


@router.post("/simple/llm/from-text", response_model=GenerateFromTextResponse)
async def create_simple_quiz_from_text_using_llm(body: GenerateFromTextBody) -> GenerateFromTextResponse:
    try:
        strategy = SimpleQuizStrategyLLM()
        quizzes = await strategy.generate_many(body.input, body.limit, body.number_of_answers)
        quiz_dtos = [quiz_to_dto(q) for q in quizzes]
        print([q.model_dump() for q in quiz_dtos])
        return GenerateFromTextResponse(quizzes=quiz_dtos)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encountered error: {e}")
    

@router.get("/voice/from-text")
async def get_voice_quiz():
    return {"message": "generate voice quiz"}


@router.get("/context/from-text")
async def get_context_quiz():
    return {"message": "generate context quiz"}
