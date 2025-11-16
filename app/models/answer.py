from typing import Optional
from pydantic import BaseModel, Field


class AnswerDTO(BaseModel):
    text: str
    is_correct: bool

class SimpleAnswerDTO(BaseModel):
    text: str
    is_correct: bool

class ContextAnswerDTO(BaseModel):
    text: str
    reasoning: str
    is_correct: bool

class SequenceAnswerDTO(BaseModel):
    text: str
    correct_position: int