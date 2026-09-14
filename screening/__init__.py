"""Resume screening: parse resumes and score them against a job description."""

from .resume_parser import ResumeParseError, parse_resume
from .jd_matcher import (
    JDMatcherError,
    MatchResult,
    match_batch,
    match_resume_to_jd,
    sort_by_score,
)

__all__ = [
    "ResumeParseError",
    "parse_resume",
    "JDMatcherError",
    "MatchResult",
    "match_batch",
    "match_resume_to_jd",
    "sort_by_score",
]
