import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AGENT_ROLES = REPO / "references" / "agent-roles.md"
REFEREE = REPO / "references" / "school-prompts" / "referee.md"


class RefereeContractTest(unittest.TestCase):
    def setUp(self):
        self.agent_roles = AGENT_ROLES.read_text(encoding="utf-8")
        self.referee = REFEREE.read_text(encoding="utf-8")

    def test_source_hierarchy_splits_classics_into_two_tiers(self):
        for text, name in ((self.agent_roles, "agent-roles"), (self.referee, "referee")):
            self.assertIn("核心论断", text, f"{name} missing strong classics tier")
            self.assertIn("例证", text, f"{name} missing example classics tier")

    def test_referee_must_run_the_validator(self):
        self.assertIn("validate_citations.py", self.referee)

    def test_referee_must_void_unmet_premises(self):
        self.assertIn("适用前提", self.referee)
        self.assertIn("作废", self.referee)

    def test_referee_must_record_rival_resolution(self):
        self.assertIn("rival_resolution", self.referee)
        self.assertIn("竞合", self.referee)

    def test_referee_keeps_lone_evidence_rule(self):
        self.assertIn("孤证不立", self.referee)

    def test_lone_evidence_is_documented_as_prompt_rule_not_script_check(self):
        self.assertIn("不由脚本检查", self.referee)


if __name__ == "__main__":
    unittest.main()
