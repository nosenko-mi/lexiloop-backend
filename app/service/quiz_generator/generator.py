from app.domain.quiz import AbstractQuiz
from app.service.quiz_generator.generator_strategy import QuizGenerationStrategy


class QuizGenerator:
    def __init__(self, strategy: QuizGenerationStrategy) -> None:
        self.strategy = strategy

    def generate(self, source: str, quiz_limit: int, answer_limit: int) -> AbstractQuiz | None:
        return self.strategy.generate(source, quiz_limit, answer_limit)
