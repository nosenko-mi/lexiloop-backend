from typing import List, Literal, Union
from pydantic import BaseModel

from app.models.answer import AnswerDTO, SequenceAnswerDTO, SimpleAnswerDTO


# class QuizDTO(BaseModel):
#     type: Literal["simple", "sequence", "voice", "context"]
#     text: str
#     answers: List[AnswerDTO]

# === Base Quiz DTO (for inheritance) ===

class BaseQuizDTO(BaseModel):
    text: str


# === Specific Quiz DTOs ===

class SimpleQuizDTO(BaseQuizDTO):
    type: Literal["simple"]
    answers: List[SimpleAnswerDTO]

class SequenceQuizDTO(BaseQuizDTO):
    type: Literal["sequence"]
    answers: List[SequenceAnswerDTO]

QuizDTO = Union[SimpleQuizDTO, SequenceQuizDTO]