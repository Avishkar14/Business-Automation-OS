from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import relationship

from database import Base


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    job_metadata = Column(JSONB, nullable=True)
    status = Column(String(50), default="OPEN")

    applications = relationship("Application", back_populates="job")
    tests = relationship("Test",back_populates="job")


class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id = Column(Integer, primary_key=True, index=True)

    name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)

    resume_text = Column(Text, nullable=True)
    resume_metadata = Column(JSONB, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    applications = relationship("Application", back_populates="candidate")

class Application(Base):
    __tablename__ = "applications"

    application_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.candidate_id"),
        nullable=False
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.job_id"),
        nullable=False
    )

    status = Column(
        String(50),
        default="APPLIED",
        nullable=False
    )

    applied_at = Column(
        DateTime(timezone=True),
        # default=datetime.utcnow,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships established for SQLAlchemy to identify :

    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    screening = relationship( "ScreeningRecord", back_populates="application", uselist=False)
    test_attempts = relationship("TestAttempt", back_populates="application")


class ScreeningRecord(Base):
    __tablename__ = "screening_records"

    screening_id = Column(Integer, primary_key=True, index=True)

    application_id = Column(
        Integer,
        ForeignKey("applications.application_id"),
        nullable=False,
        unique=True
    )

    score = Column(
        Numeric(5, 2),
        nullable=True
    )

    decision = Column(
        String(30),
        nullable=False
    )

    matched_skills = Column(
        JSONB,
        nullable=True
    )

    missing_skills = Column(
        JSONB,
        nullable=True
    )

    experience_match = Column(
        JSONB,
        nullable=True
    )

    reason = Column(
        Text,
        nullable=True
    )
# Later will need ? -> stores : model_name , model_version , prompt_version
    # ai_result = Column(
    #     JSONB,
    #     nullable=True
    # )

    created_at = Column(
        DateTime(timezone=True),
        # default=datetime.utcnow,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # One-to-one relationship with Application
    application = relationship(
        "Application",
        back_populates="screening"
    )



class Test(Base):
    __tablename__ = "tests"

    test_id = Column(Integer, primary_key=True, index=True)

    job_id = Column(
        Integer,
        ForeignKey("jobs.job_id"),
        nullable=False
    )

    title = Column(String(200), nullable=False)

    description = Column(Text, nullable=True)

    duration_minutes = Column(
        Integer,
        nullable=True
    )

    status = Column(
        String(30),
        default="DRAFT",
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    job = relationship(
        "Job",
        back_populates="tests"
    )

    questions = relationship(
        "Question",
        back_populates="test"
    )

    test_attempts = relationship(
        "TestAttempt",
        back_populates="test"
    )


class Question(Base):
    __tablename__ = "questions"

    question_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    test_id = Column(
        Integer,
        ForeignKey("tests.test_id"),
        nullable=False
    )

    question_text = Column(
        Text,
        nullable=False
    )

    question_type = Column(
        String(30),
        nullable=False
    )

    options = Column(
        JSONB,
        nullable=True
    )

    correct_answer = Column(
        JSONB,
        nullable=True
    )

    points = Column(
        Integer,
        nullable=False
    )

    question_order = Column(
        Integer,
        nullable=False
    )

    # Relationships
    test = relationship(
        "Test",
        back_populates="questions"
    )

    answers = relationship(
        "Answer",
        back_populates="question"
    )


class TestAttempt(Base):
    __tablename__ = "test_attempts"

    attempt_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    application_id = Column(
        Integer,
        ForeignKey("applications.application_id"),
        nullable=False
    )

    test_id = Column(
        Integer,
        ForeignKey("tests.test_id"),
        nullable=False
    )

    status = Column(
        String(30),
        default="NOT_STARTED",
        nullable=False
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    submitted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    score = Column(
        Numeric(5, 2),
        nullable=True
    )

    # Relationships
    application = relationship(
        "Application",
        back_populates="test_attempts"
    )

    test = relationship(
        "Test",
        back_populates="test_attempts"
    )

    answers = relationship(
        "Answer",
        back_populates="attempt"
    )


class Answer(Base):
    __tablename__ = "answers"

    answer_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    attempt_id = Column(
        Integer,
        ForeignKey("test_attempts.attempt_id"),
        nullable=False
    )

    question_id = Column(
        Integer,
        ForeignKey("questions.question_id"),
        nullable=False
    )

    answer = Column(
        JSONB,
        nullable=True
    )

    is_correct = Column(
        Boolean,
        nullable=True
    )

    points_awarded = Column(
        Numeric(5, 2),
        nullable=True
    )

    answered_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    attempt = relationship(
        "TestAttempt",
        back_populates="answers"
    )

    question = relationship(
        "Question",
        back_populates="answers"
    )