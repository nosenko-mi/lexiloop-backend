from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import models, schemas


def get_simple_quiz(db: Session, quiz_id: int):
    return db.query(models.SimpleQuiz).filter(models.SimpleQuiz.id == quiz_id).first()


def get_simple_quiz_by_text(db: Session, text: str):
    return db.scalar(select(models.SimpleQuiz).where(models.SimpleQuiz.text == text))


def get_simple_quizzes(db: Session, skip: int = 0, limit: int = 100) -> list[models.SimpleQuiz]:
    # return db.query(models.SimpleQuiz).offset(skip).limit(limit).all()
    return db.scalars(select(models.SimpleQuiz).offset(skip).limit(limit))



def create_simple_quiz(db: Session, quiz: schemas.SimpleQuizCreate):
    db_simple_quiz = models.SimpleQuiz(text=quiz.text, type_id=quiz.type_id)
    db.add(db_simple_quiz)
    db.commit()
    db.refresh(db_simple_quiz)
    return db_simple_quiz


def get_simple_answer(db: Session, answer_id: int):
    return db.query(models.SimpleAnswer).filter(models.SimpleQuiz.id == answer_id).first()


def create_quiz_answer(db: Session, answer: schemas.SimpleAnswerCreate, quiz_id: int):
    db_answer = models.SimpleAnswer(**answer.model_dump(), quiz_id=quiz_id)
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer


def create_complete_simple_quiz(db: Session, quiz: schemas.SimpleQuizCreate, answers: list[schemas.SimpleAnswerCreate]) -> models.SimpleQuiz:
    db_quiz = create_simple_quiz(db, quiz)
    if not db_quiz:
        return
    db_answers = []
    for answer in answers:
        db_answers.append(create_quiz_answer(db, answer, db_quiz.id))

    db_quiz.answers = db_answers
    return db_quiz