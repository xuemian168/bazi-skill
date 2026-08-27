import hashlib
import tempfile
import textwrap
import unittest
from pathlib import Path

from classics.corpus import parse_provenance, read_lines, sha256_of, slice_lines


class CorpusTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_sha256_matches_hashlib(self):
        path = self.root / "a.txt"
        path.write_text("甲乙丙", encoding="utf-8")
        expected = hashlib.sha256("甲乙丙".encode("utf-8")).hexdigest()
        self.assertEqual(sha256_of(path), expected)

    def test_read_lines_drops_line_endings(self):
        path = self.root / "a.txt"
        path.write_text("一\n二\n三\n", encoding="utf-8")
        self.assertEqual(read_lines(path), ["一", "二", "三"])

    def test_slice_lines_is_one_indexed_inclusive(self):
        lines = ["一", "二", "三", "四"]
        self.assertEqual(slice_lines(lines, 2, 3), "二三")
        self.assertEqual(slice_lines(lines, 1, 1), "一")

    def test_slice_lines_out_of_range_returns_none(self):
        lines = ["一", "二"]
        self.assertIsNone(slice_lines(lines, 0, 1))
        self.assertIsNone(slice_lines(lines, 1, 3))

    def test_parse_provenance_extracts_sha256_per_file(self):
        path = self.root / "PROVENANCE.md"
        path.write_text(
            textwrap.dedent(
                """\
                # 语料溯源

                ## corpus/ditiansui.txt
                - 来源: https://example.org/a
                - sha256: aa11
                - 公有领域依据: 清代

                ## corpus/qiongtong-baojian.txt
                - sha256: bb22
                """
            ),
            encoding="utf-8",
        )
        mapping, errors = parse_provenance(path)
        self.assertEqual(errors, [])
        self.assertEqual(
            mapping,
            {"corpus/ditiansui.txt": "aa11", "corpus/qiongtong-baojian.txt": "bb22"},
        )

    def test_parse_provenance_reports_section_without_sha256(self):
        path = self.root / "PROVENANCE.md"
        path.write_text("## corpus/a.txt\n- 来源: x\n", encoding="utf-8")
        mapping, errors = parse_provenance(path)
        self.assertEqual(mapping, {})
        self.assertTrue(any("sha256" in e for e in errors), errors)

    def test_parse_provenance_missing_file(self):
        mapping, errors = parse_provenance(self.root / "nope.md")
        self.assertEqual(mapping, {})
        self.assertTrue(any("PROVENANCE" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
