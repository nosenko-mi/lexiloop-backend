

from app.domain.answer import SequenceAnswer, SimpleAnswer
from app.domain.quiz import SequenceQuiz, SingleAnswerQuiz
from app.models.answer import AnswerDTO, SequenceAnswerDTO, SimpleAnswerDTO
from app.models.quiz import QuizDTO, SequenceQuizDTO, SimpleQuizDTO


def answer_to_dto(answer) -> AnswerDTO:
    
    return AnswerDTO(text=answer.text, is_correct=answer.is_correct)

# def quiz_to_dto(quiz) -> QuizDTO:
#     answers = [answer_to_dto(a) for a in quiz.answers]
#     return QuizDTO(text=quiz.text, answers=answers)

def quiz_to_dto(quiz) -> QuizDTO:
    if isinstance(quiz, SingleAnswerQuiz):
        return SimpleQuizDTO(
            type="simple",
            text=quiz.text,
            answers=[
                SimpleAnswerDTO(text=a.text, is_correct=a.is_correct)
                for a in quiz.answers if isinstance(a, SimpleAnswer)
            ]
        )
    elif isinstance(quiz, SequenceQuiz):
        return SequenceQuizDTO(
            type="sequence",
            text=quiz.text,
            answers=[
                SequenceAnswerDTO(text=a.text, correct_position=a.correct_position)
                for a in quiz.answers if isinstance(a, SequenceAnswer)
            ]
        )
    else:
        raise ValueError(f"Unsupported quiz type: {type(quiz)}")