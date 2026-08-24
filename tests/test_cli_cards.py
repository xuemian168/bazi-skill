import subprocess
import sys
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
        self.assertIn("5", result.stdout)

    def test_missing_cards_dir_exits_two(self):
        result = run_cli("--cards", str(REPO / "docs"))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_requires_a_mode(self):
        result = run_cli()
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
