from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Candidate
from schemas.candidate import CandidateCreate, CandidateResponse

router = APIRouter(
    prefix="/api/candidates",
    tags=["Candidates"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=CandidateResponse)
def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db)
):
    new_candidate = Candidate(
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        resume_text=candidate.resume_text,
        resume_metadata=candidate.resume_metadata
    )

    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)

    return new_candidate


@router.get("/", response_model=list[CandidateResponse])
def get_candidates(db: Session = Depends(get_db)):
    return db.query(Candidate).all()


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    candidate = (
        db.query(Candidate)
        .filter(Candidate.candidate_id == candidate_id)
        .first()
    )

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    return candidate