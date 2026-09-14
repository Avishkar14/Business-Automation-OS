"""
CLI demo for Resume <-> JD matching.

Usage (from repo root):
    python -m screening.main --resume samples/sample_resume.txt --jd samples/sample_jd.txt
    python -m screening.main --resume-dir samples/ --jd samples/sample_jd.txt
"""

import argparse
import json
import sys
from pathlib import Path

from .resume_parser import ResumeParseError, parse_resume
from .jd_matcher import JDMatcherError, match_batch, match_resume_to_jd, sort_by_score


def load_jd(jd_path: str) -> str:
    path = Path(jd_path)
    if not path.exists():
        print(f"JD file not found: {jd_path}")
        sys.exit(1)
    return path.read_text(encoding="utf-8", errors="ignore")


def run_single(resume_path: str, jd_path: str) -> None:
    jd_text = load_jd(jd_path)
    try:
        resume_text = parse_resume(resume_path)
    except ResumeParseError as e:
        print(f"Resume parse error: {e}")
        sys.exit(1)

    print(f"Parsed resume ({len(resume_text)} chars). Scoring against JD...\n")
    try:
        result = match_resume_to_jd(resume_text, jd_text)
    except JDMatcherError as e:
        print(f"Matching error: {e}")
        sys.exit(1)

    print(json.dumps(result.to_dict(), indent=2))
    print(f"\nShortlisted: {result.is_shortlisted()}")


def run_batch(resume_dir: str, jd_path: str) -> None:
    jd_text = load_jd(jd_path)
    dir_path = Path(resume_dir)
    if not dir_path.is_dir():
        print(f"Not a directory: {resume_dir}")
        sys.exit(1)

    resumes = {}
    for file in sorted(dir_path.iterdir()):
        if file.suffix.lower() in (".pdf", ".docx", ".txt") and "jd" not in file.stem.lower():
            try:
                resumes[file.stem] = parse_resume(str(file))
            except ResumeParseError as e:
                print(f"Skipping {file.name}: {e}")

    if not resumes:
        print("No parseable resumes found in directory.")
        sys.exit(1)

    print(f"Scoring {len(resumes)} resumes against JD...\n")
    results = match_batch(resumes, jd_text)
    ranked = sort_by_score(results)

    print(f"{'Rank':<5}{'Candidate':<28}{'Score':<8}{'Verdict':<16}{'Shortlisted'}")
    for i, (cid, r) in enumerate(ranked, start=1):
        print(f"{i:<5}{cid:<28}{r.overall_score:<8}{r.verdict:<16}{r.is_shortlisted()}")

    failed = [cid for cid, r in results.items() if isinstance(r, JDMatcherError)]
    if failed:
        print(f"\nFailed to score: {failed}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Resume <-> JD matching prototype")
    parser.add_argument("--jd", required=True, help="Path to job description text file")
    parser.add_argument("--resume", help="Path to a single resume file")
    parser.add_argument("--resume-dir", help="Path to a directory of resumes (batch mode)")
    args = parser.parse_args()

    if not args.resume and not args.resume_dir:
        parser.error("Provide either --resume or --resume-dir")

    if args.resume:
        run_single(args.resume, args.jd)
    else:
        run_batch(args.resume_dir, args.jd)


if __name__ == "__main__":
    main()
