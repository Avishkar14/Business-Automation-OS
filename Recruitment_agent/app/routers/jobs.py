from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.job import JobCreate, JobResponse
from database import SessionLocal
from models import Job


router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"]
)


# Database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=JobResponse)
def create_job(
    job: JobCreate, 
    db: Session = Depends(get_db)
):
    new_job = Job(
        title=job.title,
        description=job.description,
        job_metadata=job.job_metadata
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


@router.get("/", response_model=list[JobResponse])
def get_jobs(db: Session = Depends(get_db)):

    jobs = db.query(Job).all()

    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):

    job = db.query(Job).filter(Job.job_id == job_id).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job