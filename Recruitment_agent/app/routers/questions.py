from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Question, Test
from schemas.question import QuestionCreate, QuestionResponse


router = APIRouter(
    prefix="/api/questions",
    tags=["Questions"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=QuestionResponse)
def create_question(
    question: QuestionCreate,
    db: Session = Depends(get_db)
):
    # Verify that the test exists
    test = (
        db.query(Test)
        .filter(Test.test_id == question.test_id)
        .first()
    )

    if test is None:
        raise HTTPException(
            status_code=404,
            detail="Test not found"
        )

    new_question = Question(
        test_id=question.test_id,
        question_text=question.question_text,
        question_type=question.question_type,
        options=question.options,
        correct_answer=question.correct_answer,
        points=question.points,
        question_order=question.question_order
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return new_question


@router.get("/", response_model=list[QuestionResponse])
def get_questions(
    db: Session = Depends(get_db)
):
    return db.query(Question).all()


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    question = (
        db.query(Question)
        .filter(Question.question_id == question_id)
        .first()
    )

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    return question