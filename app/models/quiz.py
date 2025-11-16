from typing import List, Literal, Union
from pydantic import BaseModel, Field

from app.models.answer import AnswerDTO, ContextAnswerDTO, SequenceAnswerDTO, SimpleAnswerDTO


# class QuizDTO(BaseModel):
#     type: Literal["simple", "sequence", "voice", "context"]
#     text: str
#     answers: List[AnswerDTO]

class BaseQuizDTO(BaseModel):
    text: str


class SimpleQuizDTO(BaseQuizDTO):
    type: Literal["simple"]
    answers: List[SimpleAnswerDTO]


class SequenceQuizDTO(BaseQuizDTO):
    type: Literal["sequence"]
    answers: List[SequenceAnswerDTO]


class ContextQuizDTO(BaseQuizDTO):
    type: Literal["context"]
    answers: List[ContextAnswerDTO]
    explanation: str
    identified_grammar: str

QuizDTO = Union[SimpleQuizDTO, SequenceQuizDTO, ContextQuizDTO]