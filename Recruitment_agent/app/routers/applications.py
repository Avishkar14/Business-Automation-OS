from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Application, Candidate, Job
from schemas.application import ApplicationCreate, ApplicationResponse

router = APIRouter(
    prefix="/api/applications",
    tags=["Applications"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ApplicationResponse)
def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db)
):
    # Check candidate exists
    candidate = (
        db.query(Candidate)
        .filter(Candidate.candidate_id == application.candidate_id)
        .first()
    )

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    # Check job exists
    job = (
        db.query(Job)
        .filter(Job.job_id == application.job_id)
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    new_application = Application(
        candidate_id=application.candidate_id,
        job_id=application.job_id,
        status="APPLIED"
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return new_application


@router.get("/", response_model=list[ApplicationResponse])
def get_applications(db: Session = Depends(get_db)):
    return db.query(Application).all()


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    application = (
        db.query(Application)
        .filter(Application.application_id == application_id)
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return application