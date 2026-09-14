"""
Resume <-> Job Description matching engine.

Calls the Groq API to produce a structured match score and reasoning.
Designed to be imported by the recruitment orchestrator.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Optional 

import groq 

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
VALID_VERDICTS = {"strong_match", "possible_match", "weak_match", "no_match"}

SYSTEM_PROMPT = """You are a resume-screening assistant for a recruitment pipeline. \
You compare a candidate's resume against a job description and produce an \
objective match assessment. Be strict and evidence-based: only credit a skill \
or requirement if it is actually supported by the resume text. Do not invent \
candidate details. Respond with ONLY a JSON object — no markdown fences, no \
preamble, no commentary outside the JSON."""

USER_PROMPT_TEMPLATE = """JOB DESCRIPTION:
{jd_text} 

CANDIDATE RESUME: 
{resume_text} 

Evaluate this candidate against the job description and return a JSON object \
with EXACTLY this shape:

{{
  "overall_score": <integer 0-100>,
  "verdict": "<one of: strong_match, possible_match, weak_match, no_match>",
  "matched_requirements": ["<requirement from JD the resume clearly satisfies>", ...],
  "missing_requirements": ["<requirement from JD the resume does not show>", ...],
  "matched_skills": ["<specific skill/tech found in both JD and resume>", ...],
  "years_relevant_experience": <number, best estimate, 0 if unclear>,
  "red_flags": ["<any gaps, inconsistencies, or concerns, empty list if none>"],
  "summary": "<2-3 sentence plain-English summary of fit, for a recruiter to skim>"
}}

Scoring guide:
- 85-100 (strong_match): meets nearly all core requirements, strong evidence
- 60-84 (possible_match): meets most core requirements, some gaps
- 30-59 (weak_match): meets a minority of requirements
- 0-29 (no_match): fundamentally unqualified or wrong domain
"""


@dataclass
class MatchResult:
    """Structured result of a resume-JD match, ready for the DB layer / dashboard."""

    overall_score: int
    verdict: str
    matched_requirements: list = field(default_factory=list)
    missing_requirements: list = field(default_factory=list)
    matched_skills: list = field(default_factory=list)
    years_relevant_experience: float = 0
    red_flags: list = field(default_factory=list)
    summary: str = ""
    raw_response: Optional[str] = field(default=None, repr=False)

    def to_dict(self) -> dict:
        return {
            "overall_score": self.overall_score,
            "verdict": self.verdict,
            "matched_requirements": self.matched_requirements,
            "missing_requirements": self.missing_requirements,
            "matched_skills": self.matched_skills,
            "years_relevant_experience": self.years_relevant_experience,
            "red_flags": self.red_flags,
            "summary": self.summary,
        }

    def is_shortlisted(self, threshold: Optional[int] = None) -> bool:
        """Matches the orchestrator's 'if shortlisted' branch."""
        if threshold is None:
            threshold = int(os.environ.get("SHORTLIST_THRESHOLD", "60"))
        return self.overall_score >= threshold


class JDMatcherError(Exception):
    """Raised when the matcher fails to get a usable result from the API."""


def match_resume_to_jd(
    resume_text: str,
    jd_text: str,
    client: Optional[groq.Groq] = None,
    model: str = MODEL,
) -> MatchResult:
    """
    Score a single resume against a job description.

    Args:
        resume_text: Plain text of the resume (e.g. from parse_resume).
        jd_text: Plain text of the job description.
        client: Optional pre-built Groq client (reuse across batch calls).
        model: Groq model string to use.

    Returns:
        MatchResult with score, verdict, and reasoning.

    Raises:
        JDMatcherError: if the API call fails or returns unparseable output.
    """
    if not resume_text.strip() or not jd_text.strip():
        raise JDMatcherError("Both resume_text and jd_text must be non-empty.")

    client = client or _default_client()

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.2,
            max_tokens=1500,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": USER_PROMPT_TEMPLATE.format(
                        jd_text=jd_text.strip(), resume_text=resume_text.strip()
                    ),
                },
            ],
        )
    except groq.APIError as e:
        raise JDMatcherError(f"Groq API call failed: {e}") from e

    raw_text = (response.choices[0].message.content or "").strip()
    parsed = _parse_json_response(raw_text)
    return _result_from_parsed(parsed, raw_text)


def match_batch(
    resumes: dict,
    jd_text: str,
    client: Optional[groq.Groq] = None,
    model: str = MODEL,
) -> dict:
    """
    Score multiple resumes against the same JD.

    Args:
        resumes: dict of {candidate_id: resume_text}.
        jd_text: Plain text of the job description.
        client: Optional shared client (built once here if not passed).
        model: Groq model string to use.

    Returns:
        dict of {candidate_id: MatchResult | JDMatcherError}.
    """
    client = client or _default_client()
    results = {}
    for candidate_id, resume_text in resumes.items():
        try:
            results[candidate_id] = match_resume_to_jd(
                resume_text, jd_text, client=client, model=model
            )
        except JDMatcherError as e:
            results[candidate_id] = e
    return results


def sort_by_score(results: dict) -> list:
    """Turn a match_batch() dict into a score-sorted list of (id, MatchResult)."""
    scored = [
        (cid, r) for cid, r in results.items() if isinstance(r, MatchResult)
    ]
    return sorted(scored, key=lambda pair: pair[1].overall_score, reverse=True)


def _default_client() -> groq.Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise JDMatcherError(
            "GROQ_API_KEY environment variable not set. "
            "Copy .env.example to .env or set the variable in your shell."
        )
    return groq.Groq(api_key=api_key)


def _parse_json_response(raw_text: str) -> dict:
    """Parse model JSON, including ```json fences or extra surrounding text."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        raise JDMatcherError(
            f"Could not parse model output as JSON.\nRaw output: {raw_text[:500]}"
        ) from None


def _as_str_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def _result_from_parsed(parsed: dict, raw_text: str) -> MatchResult:
    try:
        score = int(float(parsed.get("overall_score", 0)))
    except (TypeError, ValueError):
        score = 0
    score = max(0, min(100, score))

    verdict = str(parsed.get("verdict", "no_match")).strip().lower()
    if verdict not in VALID_VERDICTS:
        if score >= 85:
            verdict = "strong_match"
        elif score >= 60:
            verdict = "possible_match"
        elif score >= 30:
            verdict = "weak_match"
        else:
            verdict = "no_match"

    try:
        years = float(parsed.get("years_relevant_experience", 0) or 0)
    except (TypeError, ValueError):
        years = 0.0

    return MatchResult(
        overall_score=score,
        verdict=verdict,
        matched_requirements=_as_str_list(parsed.get("matched_requirements")),
        missing_requirements=_as_str_list(parsed.get("missing_requirements")),
        matched_skills=_as_str_list(parsed.get("matched_skills")),
        years_relevant_experience=years,
        red_flags=_as_str_list(parsed.get("red_flags")),
        summary=str(parsed.get("summary", "") or ""),
        raw_response=raw_text,
    )
