import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REPORT = REPO / "references" / "report-generation.md"
SAFETY = REPO / "references" / "school-prompts" / "safety-editor.md"


class ReportContractTest(unittest.TestCase):
    def setUp(self):
        self.report = REPORT.read_text(encoding="utf-8")
        self.safety = SAFETY.read_text(encoding="utf-8")

    def test_report_defines_index_section(self):
        self.assertIn("依据索引", self.report)

    def test_report_defines_four_columns(self):
        for column in ("卡片ID", "典籍出处", "原文", "本盘适用理由"):
            self.assertIn(column, self.report, f"missing column: {column}")

    def test_report_keeps_body_free_of_inline_markers(self):
        self.assertIn("正文不带角标", self.report)

    def test_report_requires_validator_run(self):
        self.assertIn("validate_citations.py", self.report)

    def test_report_documents_no_basis_annotation(self):
        self.assertIn("无典籍条文支撑", self.report)

    def test_report_documents_rival_resolution(self):
        # Round 2 correction: the validator enforces rival_resolution
        # whenever a report's 依据索引 lists two mutually-竞合 cards
        # (confirmed by probe), but the report contract never told an
        # author that field exists. A report author following the
        # documentation literally must be able to satisfy every rule the
        # tooling enforces.
        self.assertIn("rival_resolution", self.report)

    def test_safety_editor_checks_index_section(self):
        self.assertIn("依据索引", self.safety)


if __name__ == "__main__":
    unittest.main()
