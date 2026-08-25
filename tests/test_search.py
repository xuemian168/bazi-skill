import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from classics.cards import load_cards
from classics.search import bigrams, score, search_cards, search_corpus

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests" / "fixtures"
CLI = REPO / "scripts" / "search_classics.py"


class BigramTest(unittest.TestCase):
    def test_bigrams_of_normalised_text(self):
        self.assertEqual(bigrams("衰旺真机"), ["衰旺", "旺真", "真机"])

    def test_punctuation_is_normalised_away_before_splitting(self):
        self.assertEqual(bigrams("衰旺，真机"), ["衰旺", "旺真", "真机"])

    def test_single_character_query_yields_no_bigram(self):
        self.assertEqual(bigrams("木"), [])

    def test_score_is_zero_when_nothing_matches(self):
        self.assertEqual(score(bigrams("紫微"), "能知衰旺之真机"), 0.0)

    def test_score_is_positive_on_overlap(self):
        self.assertGreater(score(bigrams("衰旺"), "能知衰旺之真机"), 0.0)


class SearchCardsTest(unittest.TestCase):
    def setUp(self):
        self.cards, errors = load_cards(FIXTURES / "cards")
        self.assertEqual(errors, [])

    def test_finds_the_wangshuai_card(self):
        hits = search_cards(self.cards, "衰旺真机")
        self.assertTrue(hits)
        self.assertEqual(hits[0][1].id, "DTS-0001")

    def test_school_filter_excludes_others(self):
        hits = search_cards(self.cards, "余寒", school="调候")
        self.assertTrue(hits)
        self.assertTrue(all(h[1].schools == ("调候",) for h in hits))

    def test_topic_filter_matches_source_filename(self):
        hits = search_cards(self.cards, "月令", topic="30-tiaohou")
        self.assertTrue(all("30-tiaohou" in h[1].source_file for h in hits))

    def test_limit_is_honoured(self):
        self.assertLessEqual(len(search_cards(self.cards, "月令", limit=2)), 2)

    def test_no_match_returns_empty(self):
        self.assertEqual(search_cards(self.cards, "紫微斗数飞星"), [])


class SearchCorpusTest(unittest.TestCase):
    def test_locates_line_in_corpus(self):
        hits = search_corpus(FIXTURES, "余寒犹存")
        self.assertTrue(hits)
        _, rel, line, _ = hits[0]
        self.assertEqual(rel, "corpus/qiongtong-baojian.txt")
        self.assertEqual(line, 3)


class SearchCliTest(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            capture_output=True,
            text=True,
            cwd=str(REPO),
        )

    def test_card_search_prints_id(self):
        result = self._run("衰旺真机", "--classics-root", str(FIXTURES))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DTS-0001", result.stdout)

    def test_corpus_search_prints_location(self):
        result = self._run("余寒犹存", "--classics-root", str(FIXTURES), "--corpus")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("qiongtong-baojian.txt", result.stdout)
        self.assertIn("#L3", result.stdout)

    def test_no_hit_exits_one(self):
        result = self._run("紫微斗数飞星", "--classics-root", str(FIXTURES))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_unreadable_card_file_exits_two(self):
        # Guard requirement (not in the brief): search_classics.py calls
        # load_cards(), which does a plain path.read_text(encoding="utf-8")
        # per card file. An invalid-UTF-8 card file must not surface as an
        # unguarded traceback (Python's default exit 1, indistinguishable
        # from a legitimate "no hits" run) -- it must exit 2 like
        # validate_citations.py's equivalent guard.
        with tempfile.TemporaryDirectory() as tmp:
            classics_root = Path(tmp)
            cards_dir = classics_root / "cards"
            cards_dir.mkdir()
            (cards_dir / "bad.md").write_bytes(b"### DTS-0001\n- \xff\xfe not valid utf-8\n")
            result = self._run("衰旺", "--classics-root", str(classics_root))
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
