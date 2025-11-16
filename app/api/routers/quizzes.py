import random
import logging
from typing import List, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
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
from app.service.quiz_generator.generator_strategy import SequenceQuizStrategy, SimpleQuizStrategy
from app.service.quiz_generator.strategies import ContextQuizStrategyLLM
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

class GenerateContextQuizBody(BaseModel):
    input: str = Field(
        ..., 
        min_length=15, 
        description="The user-highlighted text from the e-reader."
    )
    quiz_type: Literal[
        "grammar_mimicry", 
        "clause_connector", 
        "phrasal_verb", 
        "voice_transformation"
    ] = Field(
        default="grammar_mimicry",
        description="The specific type of context quiz to generate."
    )
    native_language: str = Field(..., description="User's native language used in explanations")
    language: Literal["en"] = Field(..., description="In which language to generate quizzes")
    limit: int = Field(
        default=1,
        gt=0,
        le=5,
        description="The maximum number of quizzes to generate from the text."
    )
    number_of_answers: int = Field(
        default=4,
        gt=2,
        le=5,
        description="The number of answer choices for each quiz."
    )

class GenerateSessionQuizBody(BaseModel):
    input_sentences: List[str] = Field(..., min_length=1, description="A list of clean sentences from the user's reading history.")
    limit: int = Field(default=10, gt=0, le=20, description="The total number of quizzes to generate.")
    number_of_answers: int = Field(default=4, gt=2, le=5)

    @model_validator(mode='after')
    def validate_limit_against_sentences(self) -> 'GenerateSessionQuizBody':
        num_sentences = len(self.input_sentences)
        if self.limit > num_sentences:
            self.limit = num_sentences
        return self

class GenerateFromTextResponse(BaseModel):
    quizzes: List[QuizDTO]


class GenerateContextQuizResponse(BaseModel):
    quizzes: List[QuizDTO]

@router.get("/")
async def get_quiz_batch(simple: int = 10, voice: int = 0, sequence: int = 0, context: int = 0, db: Session = Depends(get_db)):
    return {"message": "get batch of different quizzes"}


@router.post("/session/from-text", response_model=GenerateFromTextResponse)
def create_session_quiz_from_text(
    body: GenerateSessionQuizBody,
) -> GenerateFromTextResponse:
    """
    Generates a "quiz session" from a block of user's read text.
    This combines simple and sequence quizzes (non-LLM) and shuffles them.
    """
    try:
        all_quizzes = []
        tokenizer = EnglishTokenizer()

        # --- Re-join the list of sentences into a perfect paragraph ---
        # This gives the tokenizer clean data to work with.
        text_block = ". ".join(body.input_sentences) + "."

        # --- Calculate 1/3 and 2/3 proportions ---
        total_limit = body.limit
        # Integer division for 1/3
        sequence_limit = total_limit // 3 
        # The rest go to simple quizzes (handles remainders)
        simple_limit = total_limit - sequence_limit 

        logger.info(f"Generating session quiz: {simple_limit} simple, {sequence_limit} sequence")

        # 1. Generate Simple Quizzes
        if simple_limit > 0:
            simple_strategy = SimpleQuizStrategy(tokenizer=tokenizer)
            simple_quizzes = simple_strategy.generate_many(
                text_block,  # Use the joined text block
                simple_limit, 
                body.number_of_answers
            )
            all_quizzes.extend(simple_quizzes)
        
        # 2. Generate Sequence Quizzes
        if sequence_limit > 0:
            sequence_strategy = SequenceQuizStrategy(tokenizer=tokenizer)
            sequence_quizzes = sequence_strategy.generate_many(
                text_block,  # Use the joined text block
                sequence_limit, 
                body.number_of_answers
            )
            all_quizzes.extend(sequence_quizzes)

        # 3. Shuffle the combined list
        random.shuffle(all_quizzes)

        # 4. Map to DTOs
        quiz_dtos = [quiz_to_dto(q) for q in all_quizzes]
        
        if not quiz_dtos:
            raise HTTPException(
                status_code=400, 
                detail="Could not generate any quizzes from the provided text. Read more to build your sentence bank."
            )

        return GenerateFromTextResponse(quizzes=quiz_dtos)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error generating session quiz: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred during quiz generation.")


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


@router.post("/context/from-text", response_model=GenerateContextQuizResponse)
async def create_context_quiz_from_text(body: GenerateContextQuizBody) -> GenerateContextQuizResponse:
    try:
        strategy = ContextQuizStrategyLLM(native_language=body.native_language, target_language=body.language)
        
        quizzes = await strategy.generate_many(
            source=body.input,
            quiz_limit=body.limit,
            answer_limit=body.number_of_answers,
        )

        if not quizzes:
            raise HTTPException(
                status_code=400, 
                detail="Could not identify a testable grammatical structure in the provided text."
            )

        quiz_dtos = [quiz_to_dto(q) for q in quizzes]

        return GenerateContextQuizResponse(
            quizzes=quiz_dtos
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error generating context quiz: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred...")