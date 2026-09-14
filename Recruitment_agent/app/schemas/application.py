from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApplicationCreate(BaseModel):
    candidate_id: int
    job_id: int


class ApplicationResponse(BaseModel):
    application_id: int
    candidate_id: int
    job_id: int
    status: str
    applied_at: datetime

    model_config = ConfigDict(from_attributes=True)