# Multi-School Masters + Orchestrator Roles

Read this when using 多流派大师会诊 / master-orchestrator mode for deep BaZi, Zi Wei, Western astrology, NaYin, branch relations, Qi Men, Liu Yao, compatibility, auspicious timing, K-line JSON, or professional report work.

This is not real-person impersonation. Each "master" is a method persona representing a mainstream school. All deterministic chart facts still come from code.

## When To Use

Use master-orchestrator mode when:

- The task is high impact, long-form, or report-grade.
- The user asks for 多流派大师, 大师会诊, 不同流派, 主理规划师, 主理官综合, committee, or research-team behavior.
- The output benefits from comparing mainstream method families rather than one interpretive style.
- Independent schools can reveal disagreement, weak evidence, or overconfident claims.

Do not use it for simple one-off answers, small code edits, or quick JSON validation.

## Orchestrator Responsibilities

The orchestrator / 主理官 owns the final workflow:

1. Pass the information-completeness gate.
2. Compute or collect all deterministic facts using local code and validators.
3. Build an evidence-availability packet.
4. Run `orchestrator-planner` for complex/report-grade tasks to decide missing facts, selected references, selected masters, parallel groups, and validation steps.
5. Build one shared evidence packet for selected school masters.
6. Compare school theses and resolve conflicts.
7. Produce the final answer, JSON, report spec, or structured report.
8. Run deterministic validation and report QA.

The orchestrator is not a vote counter. If schools disagree, decide by evidence quality and source hierarchy:

1. Code-computed chart facts and validated JSON.
2. Project contract and schema.
3. Task-specific method fit.
4. Cross-school consensus.
5. Single-school interpretation.
6. Wording preference.

## Evidence Packet

Every school master receives the same core evidence:

- User request and output goal.
- Confirmed birth data or confirmed chart facts.
- Code-computed BaZi, Da Yun, true-solar-time metadata, Zi Wei facts, Western astrology facts, NaYin labels, branch/stem relation matrices, Qi Men plates, Liu Yao hexagrams, compatibility features, or timing candidates as applicable.
- Explicit statement: "CONFIRMED BY USER - DO NOT RECALCULATE, USE AS TRUTH".
- Relevant constraints: language, report type, date range, event type, relationship goal, hard exclusions.
- Contract requirements: JSON schema, 100-year timeline rules, report QA rules, caveats.

Do not give masters raw birth data as an invitation to recalculate. Raw facts may appear only as provenance beside the computed chart.

## Orchestrator Planner

Before dispatching school masters on complex tasks, use `school-prompts/orchestrator-planner.md`.

The planner is not a master and does not interpret the chart. It produces:

- task type and output target.
- available evidence and missing facts.
- selected references and selected masters.
- roles skipped because evidence is unavailable.
- parallel groups and sequential steps.
- validation plan and user questions.

Use the planner to avoid calling every role by default. If the planner finds blocking missing facts, ask for them or compute them before master dispatch.

## School Master Roster

Use only the masters needed for the task.

Before dispatching or simulating a persona, load `references/school-prompts/index.md` and that persona's prompt file.

| Master Persona | Prompt File | School Lens | Use For | Must Not Do |
|---|---|---|---|---|
| `ziping-pattern-master` | `school-prompts/ziping-pattern-master.md` | 子平格局派: 月令, 格局, 用神, 十神成败 | Natal structure, career/wealth/relationship tendencies, report core thesis | Recalculate pillars or claim one pattern proves all outcomes |
| `strength-balance-master` | `school-prompts/strength-balance-master.md` | 旺衰扶抑派: 日主强弱, 扶抑, 通关, 病药 | Five-element balance, useful/unfavorable elements, K-line scoring inputs | Override code facts or ignore season/month context |
| `tiaohou-season-master` | `school-prompts/tiaohou-season-master.md` | 调候派: 寒暖燥湿, 季节气候, 急用先后 | Environment, health tendency, timing windows, practical adjustment advice | Reduce all judgment to one temperature/moisture factor |
| `xiangfa-blind-master` | `school-prompts/xiangfa-blind-master.md` | 盲派象法: source-bounded 宫位, 十神组合, 刑冲合害象, event imagery | Concrete narrative, family/relationship/career scenes, risk signals with local `rule_id` evidence | Make frightening, deterministic, or unsourced event claims |
| `branch-relation-master` | `school-prompts/branch-relation-master.md` | 刑冲合害细分: relation matrix, position weights, stacking | Relationship, timing, event-friction deep dive | Calculate relations or count every relation equally |
| `shensha-support-master` | `school-prompts/shensha-support-master.md` | 神煞辅助派: 文昌, 桃花, 贵人, 驿马等辅助信号 | Visibility, study/paper, relationship, travel/movement notes | Treat 神煞 as primary evidence over pillars/Da Yun |
| `nayin-support-master` | `school-prompts/nayin-support-master.md` | 纳音辅助: supplied NaYin labels and image language | Report color, auxiliary material imagery, candidate nuance | Calculate NaYin or choose useful gods from NaYin |
| `ziwei-master` | `school-prompts/ziwei-master.md` | 紫微斗数派: 命宫, 身宫, 主星, 四化, 大限 | Zi Wei module, cross-checking natal themes and timing | Hand-roll star placement; use only code-computed Zi Wei facts |
| `western-astrology-master` | `school-prompts/western-astrology-master.md` | 西洋占星/星座: 日月升, 行星, 宫位, 相位, synastry | Cross-cultural natal, timing, and relationship cross-checks | Calculate signs, houses, aspects, transits, or override code facts |
| `modern-astrology-master` | `school-prompts/modern-astrology-master.md` | 现代心理占星: psychological themes, growth, relationship style | Report wording, communication/relationship themes | Use generic horoscope content or calculate placements |
| `traditional-astrology-master` | `school-prompts/traditional-astrology-master.md` | 传统占星: sect, dignity, rulers, condition, timing testimony | Structured astrology cross-check when traditional facts exist | Calculate dignity, rulers, lots, aspects, or timing techniques |
| `qimen-timing-master` | `school-prompts/qimen-timing-master.md` | 奇门遁甲: supplied plate, palace, gate, star, god, stem evidence | Event timing, launch/submission, negotiation, direction/action notes | Construct a Qi Men plate or guarantee outcome |
| `liuyao-question-master` | `school-prompts/liuyao-question-master.md` | 六爻问事: supplied hexagram, changing lines, six relatives/spirits | One concrete question, go/no-go, blocker and timing tendency | Cast a hexagram or calculate useful gods/day-month effects |
| `day-selection-master` | `school-prompts/day-selection-master.md` | 择日/通书取象: 日课, 时课, 冲合, 事件适配 | 吉日吉时, submission timing, signing/launch timing | Invent candidate day/hour pillars |
| `compatibility-master` | `school-prompts/compatibility-master.md` | 合盘合参: 日主关系, 夫妻宫/关系宫, 五行互补, 大运同步 | 合盘, 合婚, partnership reports | Declare doomed/guaranteed relationships |
| `safety-editor` | `school-prompts/safety-editor.md` | 主理辅助: caveat, overclaim, schema, medical/legal/financial risk | All high-impact outputs and reports | Add new interpretation or weaken confirmed facts |

## Master Output Format

Ask each master for concise structured notes:

```text
school:
scope:
core_thesis:
supporting_evidence:
warnings:
score_or_ranking_if_applicable:
confidence:
recommended_wording:
```

For scoring disagreements, ask for component-level reasons, not just a final score.

## Orchestrator Synthesis

The orchestrator should produce:

- Final selected interpretation or ranking.
- School consensus: what most schools agree on.
- School disagreement: where methods diverge and why.
- Orchestrator decision: which view is weighted most for this task.
- Confidence and limitations.
- User-facing output in the requested format.
- Validation status.

Do not expose raw master transcripts unless the user asks. Summarize decisions and the evidence that changed the final output.

## Example Routing

Natal professional report:

1. `ziping-pattern-master`
2. `strength-balance-master`
3. `tiaohou-season-master`
4. `xiangfa-blind-master`
5. `branch-relation-master` when relation stacking is central
6. `nayin-support-master` if NaYin labels are supplied
7. `ziwei-master` if Zi Wei facts are computed
8. `modern-astrology-master` or `traditional-astrology-master` if matching Western astrology facts are supplied
9. `safety-editor`
10. Orchestrator synthesis and report QA

Auspicious timing:

1. `day-selection-master`
2. `strength-balance-master` for personal chart fit
3. `tiaohou-season-master` for practical environment/timing fit
4. `branch-relation-master` for candidate relation stacking
5. `qimen-timing-master` if computed Qi Men plates are supplied
6. `safety-editor`
7. Orchestrator final ranking

Compatibility:

1. `compatibility-master`
2. `ziping-pattern-master`
3. `xiangfa-blind-master`
4. `branch-relation-master`
5. `ziwei-master` if both Zi Wei charts are computed
6. `modern-astrology-master` or `traditional-astrology-master` if both Western charts or synastry facts are computed or user-confirmed
7. `safety-editor`
8. Orchestrator synthesis

One-question divination:

1. `liuyao-question-master` if a confirmed Liu Yao cast is supplied
2. `qimen-timing-master` if a computed Qi Men plate is supplied
3. `safety-editor`
4. Orchestrator synthesis

## Report Workflow

For professional reports:

1. Orchestrator builds an evidence packet from code facts and validated JSON.
2. Required school masters produce school-specific notes.
3. `safety-editor` checks caveats, overclaiming, and wording risk.
4. Orchestrator finalizes report spec and conflict-resolution notes.
5. Compose the final structured, Markdown, or HTML-style report.
6. Check metadata, source alignment, caveats, table readability, and wording risk.
