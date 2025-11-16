import logging
from app.domain.answer import SequenceAnswer, SimpleAnswer, ContextAnswer
from app.domain.quiz import ContextQuiz, SequenceQuiz, SingleAnswerQuiz
from app.models.answer import AnswerDTO, ContextAnswerDTO, SequenceAnswerDTO, SimpleAnswerDTO
from app.models.quiz import ContextQuizDTO, QuizDTO, SequenceQuizDTO, SimpleQuizDTO


logger = logging.getLogger(__name__)

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
    elif isinstance(quiz, ContextQuiz):
        try:
            logger.warning(f"--- ContextQuiz answers before mapping: {quiz.answers} ---")
            logger.warning(f"--- Types in ContextQuiz answers: {[type(a) for a in quiz.answers]} ---")

            answers_dto = [
                    ContextAnswerDTO(text=a.text, is_correct=a.is_correct, reasoning=a.reasoning)
                    for a in quiz.answers if isinstance(a, ContextAnswer)
                ]
            
            logger.warning(f"--- Mapped ContextAnswerDTOs: {answers_dto} ---")
            
            return ContextQuizDTO(
                type="context",
                text=quiz.text,
                explanation=quiz.explanation,
                identified_grammar=quiz.identified_grammar,
                answers=answers_dto 
            )
        except Exception as e:
             logger.error(f"Error mapping ContextQuiz answers: {e}", exc_info=True)
             raise
    else:
        raise ValueError(f"Unsupported quiz type: {type(quiz)}")