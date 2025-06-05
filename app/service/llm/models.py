from pydantic import BaseModel, Field


class SimpleAnswerResponse(BaseModel):
    text: str = Field(..., description="A text of an answer, e.g single verb")
    is_correct: bool = Field(..., description="A boolean value if answer is correct")
    reasoning: str = Field(..., description="A brief reasoning why answer is correct")


class SingleSimpleQuizResponse(BaseModel):
    text: str = Field(..., description="A text of a grammar quiz")
    answers: list[SimpleAnswerResponse] = Field(..., description="A list of answers to the quiz")


class MultipleSimpleQuizResponse(BaseModel):

    quizzes: list[SingleSimpleQuizResponse] = Field(..., description="A list of grammar quizzes")