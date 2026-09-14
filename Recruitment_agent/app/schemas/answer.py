from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AnswerCreate(BaseModel):
    attempt_id: int = Field(gt=0)
    question_id: int = Field(gt=0)

    answer: Any | None = None


class AnswerResponse(BaseModel):
    answer_id: int
    attempt_id: int
    question_id: int
    answer: Any | None
    is_correct: bool | None
    points_awarded: float | None
    answered_at: datetime | None

    model_config = {
        "from_attributes": True
    }