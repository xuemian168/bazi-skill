# School Prompt Pack Index

Read this directory only for master-orchestrator / 多流派大师会诊 workflows. These files are prompt templates and small knowledge slices distilled from the current skill references and project docs. They are not a replacement for deterministic code calculation.

## Source Policy

- Use code-computed facts as truth: BaZi pillars, Da Yun, Liu Nian, Zi Wei facts, Western astrology facts, NaYin labels, branch/stem relation matrices, Qi Men plates, Liu Yao hexagrams, compatibility features, and timing candidates.
- Use these prompt files only to interpret, compare, rank, and write.
- If a requested school needs facts not present in the evidence packet, ask the orchestrator for those facts or return `evidence_gap`; do not fill them from memory.
- Do not quote classical book names decoratively. Mention source families only when applying a method already represented in the prompt or project references.

## Common Evidence Packet

Every master prompt should receive:

```text
Input Data (CONFIRMED BY USER - DO NOT RECALCULATE, USE AS TRUTH)
- user_request:
- output_goal:
- confirmed_chart_facts:
- computed_feature_tables:
- constraints:
- relevant_contract_requirements:
- language:
```

If raw birth data is included, treat it as provenance only. The computed chart facts remain authoritative.

## Prompt Files

| Role | File | Primary Sources |
|---|---|---|
| Orchestrator Planner / 主理规划师 | `orchestrator-planner.md` | `agent-roles.md`, `project-contracts.md`, `common-schools.md`, task references |
| Orchestrator / 主理官 | `orchestrator.md` | `agent-roles.md`, `project-contracts.md`, `report-generation.md` |
| 子平格局 | `ziping-pattern-master.md` | `bazi-domain-reference.md`, `analysis-methods.md`, `AlgorithmGuide.tsx` |
| 旺衰扶抑 | `strength-balance-master.md` | `bazi-domain-reference.md`, `analysis-methods.md`, `utils/CLAUDE.md` |
| 调候 | `tiaohou-season-master.md` | `bazi-domain-reference.md`, `analysis-methods.md`, `true-solar-time.md` |
| 盲派象法 | `xiangfa-blind-master.md` | `xiangfa-system/source-map.md`, `xiangfa-system/coverage-map.md`, selected `xiangfa-system/*` slices, `analysis-methods.md`, `compatibility-analysis.md` |
| 刑冲合害细分 | `branch-relation-master.md` | `analysis-methods.md`, `compatibility-analysis.md`, `common-schools.md` |
| 神煞辅助 | `shensha-support-master.md` | `bazi-domain-reference.md`, `analysis-methods.md`, `utils/CLAUDE.md` limitation note |
| 纳音辅助 | `nayin-support-master.md` | `common-schools.md`, `bazi-domain-reference.md` |
| 紫微 | `ziwei-master.md` | `ziwei-reference.md` |
| 西洋占星 / 星座 | `western-astrology-master.md` | `western-astrology.md` |
| 现代心理占星 | `modern-astrology-master.md` | `western-astrology.md`, `common-schools.md` |
| 传统占星 | `traditional-astrology-master.md` | `western-astrology.md`, `common-schools.md` |
| 奇门遁甲 | `qimen-timing-master.md` | `common-schools.md`, `auspicious-timing.md` |
| 六爻问事 | `liuyao-question-master.md` | `common-schools.md` |
| 择日择时 | `day-selection-master.md` | `auspicious-timing.md`, `analysis-methods.md`, `true-solar-time.md` |
| 合盘 | `compatibility-master.md` | `compatibility-analysis.md`, `analysis-methods.md` |
| 安全/报告编辑 | `safety-editor.md` | `project-contracts.md`, `report-generation.md`, `analysis-methods.md` |

## Invocation Template

```text
You are {role_name}. Use only your school prompt and the evidence packet.
The chart/calendar facts are CONFIRMED BY USER - DO NOT RECALCULATE, USE AS TRUTH.
Do not invent missing GanZhi, Da Yun, Zi Wei stars, Western astrology placements/aspects/transits, NaYin labels, branch/stem relations, Qi Men plates, Liu Yao hexagrams, ShenSha, compatibility relations, or day/hour pillars.
When evidence is insufficient, write evidence_gap instead of guessing.
Return the required structured notes only.
```

For `orchestrator-planner`, use `orchestrator-planner.md` instead of the master invocation template. The planner outputs role selection and validation steps only; it must not interpret chart facts.
