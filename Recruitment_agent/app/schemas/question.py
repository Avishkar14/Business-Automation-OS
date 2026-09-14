from typing import Any, Literal

from pydantic import BaseModel, Field


QuestionType = Literal["MCQ", "MSQ", "CODING", "TEXT"]


class QuestionCreate(BaseModel):
    test_id: int = Field(gt=0)

    question_text: str = Field(
        min_length=1
    )

    question_type: QuestionType

    options: list[str] | None = None

    correct_answer: list[str] | None = None

    points: int = Field(
        gt=0
    )

    question_order: int = Field(
        gt=0
    )


class QuestionResponse(BaseModel):
    question_id: int
    test_id: int
    question_text: str
    question_type: QuestionType
    options: list[str] | None
    correct_answer: list[str] | None
    points: int
    question_order: int

    model_config = {
        "from_attributes": True
    }