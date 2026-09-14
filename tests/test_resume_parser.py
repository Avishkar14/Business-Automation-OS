import tempfile
import unittest
from pathlib import Path

from screening.resume_parser import ResumeParseError, parse_resume


class ResumeParserTests(unittest.TestCase):
    def test_parse_txt(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as handle:
            handle.write("  Alice  \n\nPython engineer\n")
            path = handle.name

        try:
            text = parse_resume(path)
            self.assertIn("Alice", text)
            self.assertIn("Python engineer", text)
            self.assertNotIn("\n\n", text)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_missing_file(self):
        with self.assertRaises(ResumeParseError):
            parse_resume("does-not-exist.pdf")

    def test_unsupported_type(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as handle:
            path = handle.name
        try:
            with self.assertRaises(ResumeParseError):
                parse_resume(path)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as handle:
            handle.write("   \n")
            path = handle.name
        try:
            with self.assertRaises(ResumeParseError):
                parse_resume(path)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_sample_resume(self):
        text = parse_resume("samples/sample_resume.txt")
        self.assertIn("Python", text)


if __name__ == "__main__":
    unittest.main()
