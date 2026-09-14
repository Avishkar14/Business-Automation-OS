from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Test, Job
from schemas.test import TestCreate, TestResponse


router = APIRouter(
    prefix="/api/tests",
    tags=["Tests"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=TestResponse)
def create_test(
    test: TestCreate,
    db: Session = Depends(get_db)
):
    # Verify that the job exists
    job = (
        db.query(Job)
        .filter(Job.job_id == test.job_id)
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    new_test = Test(
        job_id=test.job_id,
        title=test.title,
        description=test.description,
        duration_minutes=test.duration_minutes,
        status=test.status
    )

    db.add(new_test)
    db.commit()
    db.refresh(new_test)

    return new_test


@router.get("/", response_model=list[TestResponse])
def get_tests(
    db: Session = Depends(get_db)
):
    return db.query(Test).all()


@router.get("/{test_id}", response_model=TestResponse)
def get_test(
    test_id: int,
    db: Session = Depends(get_db)
):
    test = (
        db.query(Test)
        .filter(Test.test_id == test_id)
        .first()
    )

    if test is None:
        raise HTTPException(
            status_code=404,
            detail="Test not found"
        )

    return test