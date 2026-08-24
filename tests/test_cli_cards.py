import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "scripts" / "validate_citations.py"
FIXTURES = REPO / "tests" / "fixtures"


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )


class CliCardsTest(unittest.TestCase):
    def test_fixture_library_is_valid(self):
        result = run_cli("--cards", str(FIXTURES))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("VALID", result.stdout)

    def test_fixture_library_has_five_cards(self):
        result = run_cli("--cards", str(FIXTURES), "--count")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("cards: 5", result.stdout)

    def test_missing_cards_dir_exits_two(self):
        result = run_cli("--cards", str(REPO / "docs"))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_requires_a_mode(self):
        result = run_cli()
        self.assertNotEqual(result.returncode, 0)

    def test_unreadable_card_file_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            classics_root = Path(tmp)
            cards_dir = classics_root / "cards"
            cards_dir.mkdir()
            (cards_dir / "bad.md").write_bytes(b"### DTS-0001\n- \xff\xfe not valid utf-8\n")
            result = run_cli("--cards", str(classics_root))
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


class CliAnswerTest(unittest.TestCase):
    def test_unreadable_answer_file_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            answer_path = Path(tmp) / "answer.txt"
            answer_path.write_bytes(b"citations: DTS-0001\n\xff\xfe not valid utf-8\n")
            result = run_cli(
                "--answer", str(answer_path), "--classics-root", str(FIXTURES)
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
