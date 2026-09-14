import unittest
from unittest.mock import MagicMock

from screening.jd_matcher import (
    JDMatcherError,
    MatchResult,
    _parse_json_response,
    _result_from_parsed,
    match_resume_to_jd,
    sort_by_score,
)


class JsonParseTests(unittest.TestCase):
    def test_plain_json(self):
        parsed = _parse_json_response('{"overall_score": 70}')
        self.assertEqual(parsed["overall_score"], 70)

    def test_fenced_json(self):
        raw = '```json\n{"overall_score": 80}\n```'
        parsed = _parse_json_response(raw)
        self.assertEqual(parsed["overall_score"], 80)

    def test_json_with_preamble(self):
        raw = 'Here you go:\n{"overall_score": 55, "verdict": "weak_match"}'
        parsed = _parse_json_response(raw)
        self.assertEqual(parsed["verdict"], "weak_match")

    def test_invalid_json(self):
        with self.assertRaises(JDMatcherError):
            _parse_json_response("not json at all")


class ResultShapeTests(unittest.TestCase):
    def test_clamps_score_and_normalizes_verdict(self):
        result = _result_from_parsed(
            {
                "overall_score": 140,
                "verdict": "amazing",
                "matched_requirements": "Python",
                "years_relevant_experience": "3",
            },
            "{}",
        )
        self.assertEqual(result.overall_score, 100)
        self.assertEqual(result.verdict, "strong_match")
        self.assertEqual(result.matched_requirements, ["Python"])
        self.assertEqual(result.years_relevant_experience, 3.0)
        self.assertTrue(result.is_shortlisted())

    def test_to_dict_omits_raw_response(self):
        result = MatchResult(overall_score=61, verdict="possible_match", raw_response="secret")
        self.assertNotIn("raw_response", result.to_dict())
        self.assertTrue(result.is_shortlisted(60))
        self.assertFalse(result.is_shortlisted(80))


class SortAndMatchTests(unittest.TestCase):
    def test_sort_by_score_skips_errors(self):
        ranked = sort_by_score(
            {
                "a": MatchResult(overall_score=40, verdict="weak_match"),
                "b": JDMatcherError("fail"),
                "c": MatchResult(overall_score=90, verdict="strong_match"),
            }
        )
        self.assertEqual([cid for cid, _ in ranked], ["c", "a"])

    def test_empty_inputs(self):
        with self.assertRaises(JDMatcherError):
            match_resume_to_jd(" ", "JD")
        with self.assertRaises(JDMatcherError):
            match_resume_to_jd("resume", "")

    def test_match_uses_injected_client(self):
        payload = {
            "overall_score": 88,
            "verdict": "strong_match",
            "matched_requirements": ["Python"],
            "missing_requirements": [],
            "matched_skills": ["Python"],
            "years_relevant_experience": 3,
            "red_flags": [],
            "summary": "Strong backend fit.",
        }
        message = MagicMock()
        message.content = str(payload).replace("'", '"')

        choice = MagicMock()
        choice.message = message

        response = MagicMock()
        response.choices = [choice]

        client = MagicMock()
        client.chat.completions.create.return_value = response

        result = match_resume_to_jd("Python engineer resume", "Need Python", client=client)
        self.assertEqual(result.overall_score, 88)
        self.assertTrue(result.is_shortlisted())
        client.chat.completions.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
