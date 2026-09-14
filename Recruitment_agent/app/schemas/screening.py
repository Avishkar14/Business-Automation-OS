from typing import Literal #Any,

from pydantic import BaseModel, Field


class ExperienceMatch(BaseModel):
    required_years: float = Field(ge=0)
    candidate_years: float = Field(ge=0)
    match: bool


class ScreeningResult(BaseModel):
    score: float = Field(ge=0, le=100)

    decision: Literal["PASS", "REJECT", "REVIEW"]

    matched_skills: list[str] = Field(default_factory=list)

    missing_skills: list[str] = Field(default_factory=list)

    experience_match: ExperienceMatch

    reason: str = Field(min_length=1)
    
# Later will need ? -> stores : model_name , model_version , prompt_version
    # ai_result: dict[str, Any] = Field(default_factory=dict)


class ScreeningCreate(BaseModel):
    application_id: int
    score: float = Field(ge=0, le=100)
    decision: Literal["PASS", "REJECT", "REVIEW"]
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    experience_match: ExperienceMatch
    reason: str = Field(min_length=1)

class ScreeningResponse(BaseModel):
    screening_id: int
    application_id: int
    score: float
    decision: Literal["PASS", "REJECT", "REVIEW"]
    matched_skills: list[str]
    missing_skills: list[str]
    experience_match: ExperienceMatch
    reason: str

# Later will need ? -> stores : model_name , model_version , prompt_version
    # ai_result: dict[str, Any]

    model_config = {
        "from_attributes": True
    }