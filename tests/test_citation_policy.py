import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REFERENCES = REPO / "references"

INSTALL_ROOT = "${CODEX_HOME:-$HOME/.codex}/skills/bazi-skill"
# A shell invocation of a python script, with or without surrounding quotes.
PY_INVOCATION = re.compile(r"python3\s+(\"?)([^\"\s]+\.py)\1")
CLASSICS_ROOT_ARG = re.compile(r"--classics-root\s+(\"?)([^\"\s]+)\1")

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


class InstallPathContractTest(unittest.TestCase):
    """SKILL.md declares the invariant that script and `references/` paths
    inside commands *always* use the full install path, because the working
    directory is an arbitrary host project. Thirteen commands under
    `references/` — including the referee's own duty-1 enforcement command —
    used the bare `python3 scripts/...` form and simply did not run from a
    host-project cwd. This scans the shipped docs instead of trusting them."""

    def markdown_files(self):
        return sorted(REFERENCES.rglob("*.md"))

    def test_skill_md_declares_the_invariant(self):
        self.assertIn(INSTALL_ROOT, (REPO / "SKILL.md").read_text(encoding="utf-8"))

    def test_every_script_invocation_uses_the_install_path(self):
        checked = 0
        for path in self.markdown_files():
            for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                for match in PY_INVOCATION.finditer(line):
                    checked += 1
                    script = match.group(2)
                    self.assertTrue(
                        script.startswith(f"{INSTALL_ROOT}/"),
                        f"{path.relative_to(REPO)}:{number}: {script}",
                    )
        self.assertGreaterEqual(checked, 13, "invocation scan found nothing to check")

    def test_every_classics_root_argument_uses_the_install_path(self):
        checked = 0
        for path in self.markdown_files():
            for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                for match in CLASSICS_ROOT_ARG.finditer(line):
                    checked += 1
                    self.assertEqual(
                        match.group(2),
                        f"{INSTALL_ROOT}/references/classics",
                        f"{path.relative_to(REPO)}:{number}",
                    )
        self.assertGreater(checked, 0, "--classics-root scan found nothing to check")


if __name__ == "__main__":
    unittest.main()
