import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROMPTS = REPO / "references" / "school-prompts"

MASTERS = (
    "ziping-pattern-master",
    "strength-balance-master",
    "tiaohou-season-master",
    "shensha-support-master",
    "xiangfa-blind-master",
    "ziwei-master",
    "day-selection-master",
    "compatibility-master",
)

CLASSICS_BACKED = (
    "ziping-pattern-master",
    "strength-balance-master",
    "tiaohou-season-master",
    "shensha-support-master",
)

NO_BASIS_ONLY = ("xiangfa-blind-master", "ziwei-master", "day-selection-master")


def read(name: str) -> str:
    return (PROMPTS / f"{name}.md").read_text(encoding="utf-8")


class PromptContractTest(unittest.TestCase):
    def test_every_master_declares_citations_field(self):
        for name in MASTERS:
            self.assertIn("citations:", read(name), f"{name} missing citations field")

    def test_every_master_declares_citation_fit_field(self):
        for name in MASTERS:
            self.assertIn(
                "citation_fit:", read(name), f"{name} missing citation_fit field"
            )

    def test_every_master_mentions_no_classical_basis(self):
        for name in MASTERS:
            self.assertIn(
                "no_classical_basis", read(name), f"{name} missing no_classical_basis"
            )

    def test_classics_backed_masters_point_at_index(self):
        for name in CLASSICS_BACKED:
            self.assertIn(
                "references/classics/index.md", read(name), f"{name} missing index route"
            )

    def test_unsupported_masters_are_pinned_to_no_classical_basis(self):
        for name in NO_BASIS_ONLY:
            text = read(name)
            self.assertIn(
                "一律 `no_classical_basis`", text, f"{name} must be pinned to no basis"
            )

    def test_ziping_master_keeps_pattern_call_downgrade_rule(self):
        text = read("ziping-pattern-master")
        self.assertIn("pattern_tendency", text)
        self.assertIn("核心论断", text)


if __name__ == "__main__":
    unittest.main()
