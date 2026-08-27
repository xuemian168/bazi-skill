import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AGENT_ROLES = REPO / "references" / "agent-roles.md"
ORCHESTRATOR = REPO / "references" / "school-prompts" / "orchestrator.md"
SKILL = REPO / "SKILL.md"


class OrchestratorContractTest(unittest.TestCase):
    def setUp(self):
        self.agent_roles = AGENT_ROLES.read_text(encoding="utf-8")
        self.orchestrator = ORCHESTRATOR.read_text(encoding="utf-8")

    def test_source_hierarchy_splits_classics_into_two_tiers(self):
        for text, name in (
            (self.agent_roles, "agent-roles"),
            (self.orchestrator, "orchestrator"),
        ):
            self.assertIn("核心论断", text, f"{name} missing strong classics tier")
            self.assertIn("例证", text, f"{name} missing example classics tier")

    def test_orchestrator_must_run_the_validator(self):
        self.assertIn("validate_citations.py", self.orchestrator)

    def test_orchestrator_must_void_unmet_premises(self):
        self.assertIn("适用前提", self.orchestrator)
        self.assertIn("反例边界", self.orchestrator)
        self.assertIn("作废", self.orchestrator)

    def test_orchestrator_must_record_rival_resolution(self):
        self.assertIn("rival_resolution", self.orchestrator)
        self.assertIn("竞合", self.orchestrator)

    def test_orchestrator_keeps_lone_evidence_rule(self):
        self.assertIn("孤证不立", self.orchestrator)

    def test_lone_evidence_is_documented_as_prompt_rule_not_script_check(self):
        self.assertIn("不由脚本检查", self.orchestrator)

    def test_orchestrator_requires_the_card_library_check_before_answer_checks(self):
        # M1: `--answer` never runs the mode-A library check, so an answer
        # can be certified VALID against a library with one-way rivals, bad
        # tiers, unverified quotes, or a drifted sha256. Running the full
        # library check on every --answer is a real cost, so the ordering is
        # a documented duty rather than a code change — which makes deleting
        # the sentence the failure mode this guards.
        self.assertIn("--cards", self.orchestrator)
        self.assertIn("不核对卡片库本身", self.orchestrator)

    def test_the_renamed_referee_prompt_is_gone(self):
        # `referee.md` was renamed to `orchestrator.md` upstream. The audit
        # duties above only bind the role that is actually dispatched, so a
        # surviving referee.md would be a second, unreferenced copy of the
        # citation contract that nothing keeps in sync.
        self.assertFalse(
            (REPO / "references" / "school-prompts" / "referee.md").exists()
        )


class SkillMdHierarchySyncTest(unittest.TestCase):
    """SKILL.md is the always-loaded root entry point. If its inline
    orchestrator-workflow summary keeps the pre-Task-10, classics-blind
    ordering, an orchestrator that only ever sees SKILL.md (agent-roles.md
    and orchestrator.md are loaded conditionally) never learns classics
    outrank or are outranked by method fit.
    """

    def setUp(self):
        self.skill = SKILL.read_text(encoding="utf-8")

    def test_skill_md_does_not_carry_the_stale_classics_blind_hierarchy(self):
        self.assertNotIn(
            "task-specific method fit > cross-school consensus",
            self.skill,
        )

    def test_skill_md_hierarchy_summary_shows_both_classics_tiers(self):
        self.assertIn("核心论断", self.skill)
        self.assertIn("例证", self.skill)


if __name__ == "__main__":
    unittest.main()
