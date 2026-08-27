import os
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

    def test_empty_cards_value_exits_two(self):
        # `--cards ""` must dispatch to cards mode (args.cards is not None)
        # rather than falling through to answer mode with args.answer=None.
        # --classics-root is set to a real directory so run_answer_mode
        # would actually reach `Path(args.answer)` (= Path(None)) instead
        # of bailing out earlier on a missing classics root — otherwise
        # this test would pass for the wrong reason on the old dispatch
        # bug too, since this repo has no references/classics/cards yet.
        result = run_cli("--cards", "", "--classics-root", str(FIXTURES))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)


class CliAnswerTest(unittest.TestCase):
    def test_unreadable_answer_file_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            answer_path = Path(tmp) / "answer.txt"
            answer_path.write_bytes(b"citations: DTS-0001\n\xff\xfe not valid utf-8\n")
            result = run_cli(
                "--answer", str(answer_path), "--classics-root", str(FIXTURES)
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_unreadable_stdin_exits_two(self):
        # Force a UTF-8 locale: under an unset/POSIX locale, Python decodes
        # stdin with surrogateescape and invalid bytes pass through silently
        # (no exception at all), which would make this test pass whether or
        # not the guard exists. A real UTF-8 locale makes stdin decoding
        # strict, so the bad bytes below actually raise.
        env = dict(os.environ)
        env["LANG"] = "en_US.UTF-8"
        env["LC_ALL"] = "en_US.UTF-8"
        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "--answer",
                "-",
                "--classics-root",
                str(FIXTURES),
            ],
            input=b"citations: DTS-0001\n\xff\xfe not valid utf-8\n",
            capture_output=True,
            cwd=str(REPO),
            env=env,
        )
        self.assertEqual(
            result.returncode,
            2,
            result.stdout.decode(errors="replace") + result.stderr.decode(errors="replace"),
        )


if __name__ == "__main__":
    unittest.main()
