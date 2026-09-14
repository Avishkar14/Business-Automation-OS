from pydantic import BaseModel #lib used to define and validate the shape of data.
from typing import Optional, Any


class JobCreate(BaseModel):
    title: str
    description: str
    job_metadata: Optional[dict[str, Any]] = None


class JobResponse(BaseModel):
    job_id: int
    title: str
    description: str
    job_metadata: Optional[dict[str, Any]] = None
    status: str

    class Config:
        from_attributes = True