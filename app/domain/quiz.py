from abc import ABC, abstractmethod
from app.db import schemas
from app.domain.answer import AbstractAnswer, SequenceAnswer, SimpleAnswer

class AbstractQuiz(ABC):

    def __init__(self, text= "", answers: list[AbstractAnswer] = []) -> None:
        self.text: str = text
        self.answers: list = answers

    def set_question(self, text: str) -> None:
        self.text = text

    def add_answer(self, answer: AbstractAnswer) -> None:
        self.answers.append(answer)

    def __str__(self) -> str:
        res = f"{self.text}\n"
        for i, a in enumerate(self.answers):
            res += f"{i+1}. {a}\n"
        return res
    
    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def get_correct_answers(self):
        pass

    @abstractmethod
    def to_create_schema(self):
        pass


class SingleAnswerQuiz(AbstractQuiz):

    def __init__(self, text: str, answers: list) -> None:
        super().__init__(text, answers)

    def is_valid(self) -> bool:
        correct_answers = [a for a in self.answers if isinstance(a, SimpleAnswer) and a.is_correct]
        return self.text is not None and len(correct_answers) == 1 and all(a.text for a in self.answers)

    def get_correct_answers(self) -> list[SimpleAnswer]:
        if not self.is_valid():
            return []
        return [a for a in self.answers if a.is_correct]

    def to_create_schema(self) -> tuple[schemas.SimpleQuizCreate, list[schemas.SimpleAnswerCreate]]:
        quiz_schema = schemas.SimpleQuizCreate(text=self.text)
        answer_schemas = [
            schemas.SimpleAnswerCreate(text=a.text, is_correct=a.is_correct)
            for a in self.answers if isinstance(a, SimpleAnswer)
        ]
        return quiz_schema, answer_schemas


class SequenceQuiz(AbstractQuiz):

    def __init__(self, text: str, answers: list) -> None:
        super().__init__(text, answers)

    def is_valid(self) -> bool:
        if self.text is None or not self.answers:
            return False
        positions = [a.correct_position for a in self.answers if isinstance(a, SequenceAnswer)]
        return sorted(positions) == list(range(len(self.answers)))  # Must be 0-based contiguous sequence

    def get_correct_answers(self) -> list[SequenceAnswer]:
        if not self.is_valid():
            return []
        return sorted(
            [a for a in self.answers if isinstance(a, SequenceAnswer)],
            key=lambda a: a.correct_position
        )

    def to_create_schema(self) -> tuple[schemas.SequenceQuizCreate, list[schemas.SequenceAnswerCreate]]:
        quiz_schema = schemas.SequenceQuizCreate(text=self.text)
        answer_schemas = [
            schemas.SequenceAnswerCreate(text=a.text, position=a.correct_position)
            for a in self.answers if isinstance(a, SequenceAnswer)
        ]
        return quiz_schema, answer_schemas