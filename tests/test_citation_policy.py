import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

POLICY_FILES = (
    REPO / "references" / "bazi-domain-reference.md",
    REPO / "references" / "analysis-methods.md",
    REPO / "references" / "school-prompts" / "index.md",
)

STALE_PHRASES = (
    "Avoid decorative citation.",
    "Do not cite a classical text decoratively.",
    "Do not quote classical book names decoratively.",
)


class CitationPolicyTest(unittest.TestCase):
    def test_stale_prohibition_wording_is_gone(self):
        for path in POLICY_FILES:
            text = path.read_text(encoding="utf-8")
            for phrase in STALE_PHRASES:
                self.assertNotIn(phrase, text, f"{path.name} still has: {phrase}")

    def test_each_policy_file_points_at_the_validator(self):
        for path in POLICY_FILES:
            text = path.read_text(encoding="utf-8")
            self.assertIn("validate_citations.py", text, f"{path.name} missing validator")

    def test_each_policy_file_requires_card_ids(self):
        for path in POLICY_FILES:
            text = path.read_text(encoding="utf-8")
            self.assertIn("卡片 ID", text, f"{path.name} missing card ID requirement")

    def test_school_prompts_index_documents_no_classical_basis(self):
        text = (REPO / "references" / "school-prompts" / "index.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("no_classical_basis", text)

    def test_skill_md_routes_classics_tasks(self):
        text = (REPO / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/classics/index.md", text)
        self.assertIn("validate_citations.py", text)
        self.assertIn("search_classics.py", text)

    def test_readme_lists_the_new_scripts(self):
        text = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertIn("validate_citations.py", text)
        self.assertIn("search_classics.py", text)
        self.assertIn("references/classics/", text)


if __name__ == "__main__":
    unittest.main()
