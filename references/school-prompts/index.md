# School Prompt Pack Index

Read this directory only for master-referee / 多流派大师会诊 workflows. These files are prompt templates and small knowledge slices distilled from the current skill references and project docs. They are not a replacement for deterministic code calculation.

## Source Policy

- Use code-computed facts as truth: BaZi pillars, Da Yun, Liu Nian, Zi Wei facts, compatibility features, and timing candidates.
- Use these prompt files only to interpret, compare, rank, and write.
- If a requested school needs facts not present in the evidence packet, ask the referee for those facts or return `evidence_gap`; do not fill them from memory.
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
| Referee / 裁判 | `referee.md` | `agent-roles.md`, `project-contracts.md`, `report-generation.md` |
| 子平格局 | `ziping-pattern-master.md` | `bazi-domain-reference.md`, `analysis-methods.md`, `AlgorithmGuide.tsx` |
| 旺衰扶抑 | `strength-balance-master.md` | `bazi-domain-reference.md`, `analysis-methods.md`, `utils/CLAUDE.md` |
| 调候 | `tiaohou-season-master.md` | `bazi-domain-reference.md`, `analysis-methods.md`, `true-solar-time.md` |
| 盲派象法 | `xiangfa-blind-master.md` | `analysis-methods.md`, `compatibility-analysis.md` position/branch methods |
| 神煞辅助 | `shensha-support-master.md` | `bazi-domain-reference.md`, `analysis-methods.md`, `utils/CLAUDE.md` limitation note |
| 紫微 | `ziwei-master.md` | `ziwei-reference.md` |
| 择日择时 | `day-selection-master.md` | `auspicious-timing.md`, `analysis-methods.md`, `true-solar-time.md` |
| 合盘 | `compatibility-master.md` | `compatibility-analysis.md`, `analysis-methods.md` |
| 安全/报告编辑 | `safety-editor.md` | `project-contracts.md`, `report-generation.md`, `analysis-methods.md` |

## Invocation Template

```text
You are {role_name}. Use only your school prompt and the evidence packet.
The chart/calendar facts are CONFIRMED BY USER - DO NOT RECALCULATE, USE AS TRUTH.
Do not invent missing GanZhi, Da Yun, Zi Wei stars, ShenSha, compatibility relations, or day/hour pillars.
When evidence is insufficient, write evidence_gap instead of guessing.
Return the required structured notes only.
```

