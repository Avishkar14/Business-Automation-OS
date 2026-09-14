from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


AttemptStatus = Literal[
    "NOT_STARTED",
    "IN_PROGRESS",
    "COMPLETED",
    "EVALUATED"
]


class TestAttemptCreate(BaseModel):
    application_id: int = Field(gt=0)
    test_id: int = Field(gt=0)

    status: AttemptStatus = "NOT_STARTED"


class TestAttemptResponse(BaseModel):
    attempt_id: int
    application_id: int
    test_id: int
    status: AttemptStatus
    started_at: datetime | None
    submitted_at: datetime | None
    score: float | None

    model_config = {
        "from_attributes": True
    }