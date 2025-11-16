from pydantic import BaseModel, Field


class SimpleAnswerResponse(BaseModel):
    text: str = Field(..., description="A text of an answer, e.g single verb")
    is_correct: bool = Field(..., description="A boolean value if answer is correct")
    reasoning: str = Field(..., description="A brief reasoning why answer is correct")

class ContextAnswerResponse(BaseModel):
    text: str = Field(..., description="The text of the answer choice.")
    is_correct: bool = Field(..., description="A boolean value if answer is correct")
    reasoning: str = Field(..., description="A brief reasoning why answer is correct")


class SingleSimpleQuizResponse(BaseModel):
    text: str = Field(..., description="A text of a grammar quiz")
    explanation: str = Field(..., description="A brief explanation in for the correct answer")
    answers: list[SimpleAnswerResponse] = Field(..., description="A list of answers to the quiz")


class MultipleSimpleQuizResponse(BaseModel):
    quizzes: list[SingleSimpleQuizResponse] = Field(..., description="A list of grammar quizzes")

class SingleContextQuizResponse(BaseModel):
    identified_grammar: str = Field(..., description="The specific grammar concept you chose to test (e.g., 'Third Conditional', 'Phrasal Verb: look into').")
    text: str = Field(..., description="The new question you have generated.")
    explanation: str = Field(..., description="A brief explanation in for the correct answer")
    answers: list[ContextAnswerResponse] = Field(..., description="A list of answers to the quiz")

class MultipleContextQuizResponse(BaseModel):
    quizzes: list[SingleContextQuizResponse] = Field(..., description="A list of context based quizzes")