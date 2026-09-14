from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Answer, TestAttempt, Question
from schemas.answer import AnswerCreate, AnswerResponse


router = APIRouter(
    prefix="/api/answers",
    tags=["Answers"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=AnswerResponse)
def create_answer(
    answer: AnswerCreate,
    db: Session = Depends(get_db)
):
    # Check attempt exists
    attempt = (
        db.query(TestAttempt)
        .filter(
            TestAttempt.attempt_id == answer.attempt_id
        )
        .first()
    )

    if attempt is None:
        raise HTTPException(
            status_code=404,
            detail="Test attempt not found"
        )
    if attempt.status != "IN_PROGRESS":
        raise HTTPException(
            status_code=400,
            detail="Test attempt is not in progress"
        )

    # Check question exists
    question = (
        db.query(Question)
        .filter(
            Question.question_id == answer.question_id
        )
        .first()
    )

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    # Check question belongs to the test being attempted
    if question.test_id != attempt.test_id:
        raise HTTPException(
            status_code=400,
            detail="Question does not belong to this test"
        )
    existing_answer = (
        db.query(Answer)
        .filter(
            Answer.attempt_id == answer.attempt_id,
            Answer.question_id == answer.question_id
        )
        .first()
    )

    if existing_answer is not None:
        raise HTTPException(
            status_code=409,
            detail="Answer already exists for this question in this attempt"
        )

    # Evaluate the answer
    is_correct = answer.answer == question.correct_answer

    points_awarded = question.points if is_correct else 0

    new_answer = Answer(
        attempt_id=answer.attempt_id,
        question_id=answer.question_id,
        answer=answer.answer,
        is_correct=is_correct,
        points_awarded=points_awarded,
        answered_at=datetime.now(timezone.utc)
    )

    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)

    return new_answer


@router.get("/", response_model=list[AnswerResponse])
def get_answers(
    db: Session = Depends(get_db)
):
    return db.query(Answer).all()


@router.get("/{answer_id}", response_model=AnswerResponse)
def get_answer(
    answer_id: int,
    db: Session = Depends(get_db)
):
    answer = (
        db.query(Answer)
        .filter(Answer.answer_id == answer_id)
        .first()
    )

    if answer is None:
        raise HTTPException(
            status_code=404,
            detail="Answer not found"
        )

    return answer