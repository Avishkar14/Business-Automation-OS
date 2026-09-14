from pydantic import BaseModel
from typing import Optional, Any


class CandidateCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    resume_text: Optional[str] = None
    resume_metadata: Optional[dict[str, Any]] = None


class CandidateResponse(BaseModel):
    candidate_id: int
    name: str
    email: str
    phone: Optional[str] = None
    resume_text: Optional[str] = None
    resume_metadata: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True