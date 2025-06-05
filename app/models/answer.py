from pydantic import BaseModel


class AnswerDTO(BaseModel):
    text: str
    is_correct: bool

class SimpleAnswerDTO(BaseModel):
    text: str
    is_correct: bool

class SequenceAnswerDTO(BaseModel):
    text: str
    correct_position: int