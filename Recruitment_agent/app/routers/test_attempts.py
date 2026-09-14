from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import TestAttempt, Application, Test, Answer, Question
from schemas.test_attempt import ( TestAttemptCreate, TestAttemptResponse )


router = APIRouter(
    prefix="/api/test-attempts",
    tags=["Test Attempts"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=TestAttemptResponse)
def create_test_attempt(
    attempt: TestAttemptCreate,
    db: Session = Depends(get_db)
):
    # Check application exists
    application = (
        db.query(Application)
        .filter(
            Application.application_id == attempt.application_id
        )
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    # Check test exists
    test = (
        db.query(Test)
        .filter(Test.test_id == attempt.test_id)
        .first()
    )

    if test is None:
        raise HTTPException(
            status_code=404,
            detail="Test not found"
        )

    # Check that test belongs to the application's job
    if test.job_id != application.job_id:
        raise HTTPException(
            status_code=400,
            detail="Test does not belong to the application's job"
        )

    new_attempt = TestAttempt(
        application_id=attempt.application_id,
        test_id=attempt.test_id,
        status=attempt.status
    )

    # If the attempt starts immediately
    if attempt.status == "IN_PROGRESS":
        new_attempt.started_at = datetime.now(timezone.utc)

    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    return new_attempt


@router.get("/", response_model=list[TestAttemptResponse])
def get_test_attempts(
    db: Session = Depends(get_db)
):
    return db.query(TestAttempt).all()


@router.get("/{attempt_id}", response_model=TestAttemptResponse)
def get_test_attempt(
    attempt_id: int,
    db: Session = Depends(get_db)
):
    attempt = (
        db.query(TestAttempt)
        .filter(TestAttempt.attempt_id == attempt_id)
        .first()
    )

    if attempt is None:
        raise HTTPException(
            status_code=404,
            detail="Test attempt not found"
        )

    return attempt

@router.post("/{attempt_id}/submit", response_model=TestAttemptResponse)
def submit_test_attempt(
    attempt_id: int,
    db: Session = Depends(get_db)
):
    # Check attempt exists
    attempt = (
        db.query(TestAttempt)
        .filter(TestAttempt.attempt_id == attempt_id)
        .first()
    )

    if attempt is None:
        raise HTTPException(
            status_code=404,
            detail="Test attempt not found"
        )

    # Attempt must still be in progress
    if attempt.status != "IN_PROGRESS":
        raise HTTPException(
            status_code=400,
            detail="Test attempt is not in progress"
        )

    # Get all questions for this test
    questions = (
        db.query(Question)
        .filter(Question.test_id == attempt.test_id)
        .all()
    )

    # Calculate total possible marks
    total_points = sum(
        question.points or 0
        for question in questions
    )

    # Get answers submitted for this attempt
    answers = (
        db.query(Answer)
        .filter(Answer.attempt_id == attempt_id)
        .all()
    )

    # Calculate earned marks
    earned_points = sum(
        answer.points_awarded or 0
        for answer in answers
    )

    # Store earned marks
    attempt.score = earned_points
    attempt.status = "COMPLETED"
    attempt.submitted_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(attempt)

    return attempt