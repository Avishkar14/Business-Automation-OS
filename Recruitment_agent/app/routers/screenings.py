from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import ScreeningRecord, Application
from schemas.screening import ScreeningCreate, ScreeningResponse


router = APIRouter(
    prefix="/api/screenings",
    tags=["Screenings"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ScreeningResponse)
def create_screening(
    screening: ScreeningCreate,
    db: Session = Depends(get_db)
):
    # Check that the application exists
    application = (
        db.query(Application)
        .filter(
            Application.application_id == screening.application_id
        )
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    # One application can have only one screening record
    existing_screening = (
        db.query(ScreeningRecord)
        .filter(
            ScreeningRecord.application_id == screening.application_id
        )
        .first()
    )

    if existing_screening is not None:
        raise HTTPException(
            status_code=409,
            detail="Screening already exists for this application"
        )

    new_screening = ScreeningRecord(
        application_id=screening.application_id,
        score=screening.score,
        decision=screening.decision,
        matched_skills=screening.matched_skills,
        missing_skills=screening.missing_skills,
        experience_match=screening.experience_match.model_dump(), #model dump conv pydantic model/obj into py dictionary.
        # (expMatch created from schema : ScreeningCreate which has prop : expMatch which is creating 
        # it from class ExpMatch that exists into that schema) 
        reason=screening.reason
    )

    db.add(new_screening)
    db.commit()
    db.refresh(new_screening)

    return new_screening


@router.get( "/{screening_id}", response_model=ScreeningResponse)
def get_screening(
    screening_id: int,
    db: Session = Depends(get_db)
):
    screening = (
        db.query(ScreeningRecord)
        .filter(
            ScreeningRecord.screening_id == screening_id
        )
        .first()
    )

    if screening is None:
        raise HTTPException(
            status_code=404,
            detail="Screening not found"
        )

    return screening


@router.get( "/application/{application_id}", response_model=ScreeningResponse)
def get_screening_by_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    screening = (
        db.query(ScreeningRecord)
        .filter(
            ScreeningRecord.application_id == application_id
        )
        .first()
    )

    if screening is None:
        raise HTTPException(
            status_code=404,
            detail="Screening not found for this application"
        )

    return screening