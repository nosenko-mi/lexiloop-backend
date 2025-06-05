from abc import ABC, abstractmethod


class AbstractAnswer(ABC):

    def __init__(self, text: str) -> None:
        self.text = text

    def equals(self, x) -> bool:
        return self.text == x.text

    def __str__(self) -> str:
        return f"{self.text}"
    

class SimpleAnswer(AbstractAnswer):

    def __init__(self, text: str, is_correct: bool) -> None:
        super().__init__(text)
        self.is_correct = is_correct

    def __str__(self) -> str:
        return f"{self.text} [Correct = {self.is_correct}]"
    

class SequenceAnswer(AbstractAnswer):

    def __init__(self, text: str, correct_position: int) -> None:
        super().__init__(text)
        self.correct_position = correct_position

    def __str__(self) -> str:
        return f"{self.text} [Correct position = {self.correct_position}]"
