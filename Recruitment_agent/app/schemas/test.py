from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


TestStatus = Literal["DRAFT", "ACTIVE", "CLOSED"]


class TestCreate(BaseModel):
    job_id: int = Field(gt=0)

    title: str = Field(
        min_length=1,
        max_length=200
    )

    description: str | None = None

    duration_minutes: int | None = Field(
        default=None,
        gt=0
    )

    status: TestStatus = "DRAFT"


class TestResponse(BaseModel):
    test_id: int
    job_id: int
    title: str
    description: str | None
    duration_minutes: int | None
    status: TestStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }