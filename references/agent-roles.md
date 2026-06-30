# Multi-School Masters + Referee Roles

Read this when using 多流派大师会诊 / master-referee mode for deep BaZi, Zi Wei, Western astrology, compatibility, auspicious timing, K-line JSON, or professional report work.

This is not real-person impersonation. Each "master" is a method persona representing a mainstream school. All deterministic chart facts still come from code.

## When To Use

Use master-referee mode when:

- The task is high impact, long-form, or report-grade.
- The user asks for 多流派大师, 大师会诊, 不同流派, 裁判综合, committee, or research-team behavior.
- The output benefits from comparing mainstream method families rather than one interpretive style.
- Independent schools can reveal disagreement, weak evidence, or overconfident claims.

Do not use it for simple one-off answers, small code edits, or quick JSON validation.

## Referee Responsibilities

The referee / 裁判 owns the final workflow:

1. Pass the information-completeness gate.
2. Compute or collect all deterministic facts using local code and validators.
3. Build one shared evidence packet for all school masters.
4. Select the minimum useful master set.
5. Compare school theses and resolve conflicts.
6. Produce the final answer, JSON, report spec, or structured report.
7. Run deterministic validation and report QA.

The referee is not a vote counter. If schools disagree, decide by evidence quality and source hierarchy:

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
- Code-computed BaZi, Da Yun, true-solar-time metadata, Zi Wei facts, Western astrology facts, compatibility features, or timing candidates as applicable.
- Explicit statement: "CONFIRMED BY USER - DO NOT RECALCULATE, USE AS TRUTH".
- Relevant constraints: language, report type, date range, event type, relationship goal, hard exclusions.
- Contract requirements: JSON schema, 100-year timeline rules, report QA rules, caveats.

Do not give masters raw birth data as an invitation to recalculate. Raw facts may appear only as provenance beside the computed chart.

## School Master Roster

Use only the masters needed for the task.

Before dispatching or simulating a persona, load `references/school-prompts/index.md` and that persona's prompt file.

| Master Persona | Prompt File | School Lens | Use For | Must Not Do |
|---|---|---|---|---|
| `ziping-pattern-master` | `school-prompts/ziping-pattern-master.md` | 子平格局派: 月令, 格局, 用神, 十神成败 | Natal structure, career/wealth/relationship tendencies, report core thesis | Recalculate pillars or claim one pattern proves all outcomes |
| `strength-balance-master` | `school-prompts/strength-balance-master.md` | 旺衰扶抑派: 日主强弱, 扶抑, 通关, 病药 | Five-element balance, useful/unfavorable elements, K-line scoring inputs | Override code facts or ignore season/month context |
| `tiaohou-season-master` | `school-prompts/tiaohou-season-master.md` | 调候派: 寒暖燥湿, 季节气候, 急用先后 | Environment, health tendency, timing windows, practical adjustment advice | Reduce all judgment to one temperature/moisture factor |
| `xiangfa-blind-master` | `school-prompts/xiangfa-blind-master.md` | 盲派象法: 宫位, 十神组合, 刑冲合害象, event imagery | Concrete narrative, family/relationship/career scenes, risk signals | Make frightening or deterministic event claims |
| `shensha-support-master` | `school-prompts/shensha-support-master.md` | 神煞辅助派: 文昌, 桃花, 贵人, 驿马等辅助信号 | Visibility, study/paper, relationship, travel/movement notes | Treat 神煞 as primary evidence over pillars/Da Yun |
| `ziwei-master` | `school-prompts/ziwei-master.md` | 紫微斗数派: 命宫, 身宫, 主星, 四化, 大限 | Zi Wei module, cross-checking natal themes and timing | Hand-roll star placement; use only code-computed Zi Wei facts |
| `western-astrology-master` | `school-prompts/western-astrology-master.md` | 西洋占星/星座: 日月升, 行星, 宫位, 相位, synastry | Cross-cultural natal, timing, and relationship cross-checks | Calculate signs, houses, aspects, transits, or override code facts |
| `day-selection-master` | `school-prompts/day-selection-master.md` | 择日/通书取象: 日课, 时课, 冲合, 事件适配 | 吉日吉时, submission timing, signing/launch timing | Invent candidate day/hour pillars |
| `compatibility-master` | `school-prompts/compatibility-master.md` | 合盘合参: 日主关系, 夫妻宫/关系宫, 五行互补, 大运同步 | 合盘, 合婚, partnership reports | Declare doomed/guaranteed relationships |
| `safety-editor` | `school-prompts/safety-editor.md` | 裁判辅助: caveat, overclaim, schema, medical/legal/financial risk | All high-impact outputs and reports | Add new interpretation or weaken confirmed facts |

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

## Referee Synthesis

The referee should produce:

- Final selected interpretation or ranking.
- School consensus: what most schools agree on.
- School disagreement: where methods diverge and why.
- Referee decision: which view is weighted most for this task.
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
5. `ziwei-master` if Zi Wei facts are computed
6. `western-astrology-master` if Western astrology facts are computed or user-confirmed
7. `safety-editor`
8. Referee synthesis and report QA

Auspicious timing:

1. `day-selection-master`
2. `strength-balance-master` for personal chart fit
3. `tiaohou-season-master` for practical environment/timing fit
4. `safety-editor`
5. Referee final ranking

Compatibility:

1. `compatibility-master`
2. `ziping-pattern-master`
3. `xiangfa-blind-master`
4. `ziwei-master` if both Zi Wei charts are computed
5. `western-astrology-master` if both Western charts or synastry facts are computed or user-confirmed
6. `safety-editor`
7. Referee synthesis

## Report Workflow

For professional reports:

1. Referee builds an evidence packet from code facts and validated JSON.
2. Required school masters produce school-specific notes.
3. `safety-editor` checks caveats, overclaiming, and wording risk.
4. Referee finalizes report spec and conflict-resolution notes.
5. Compose the final structured, Markdown, or HTML-style report.
6. Check metadata, source alignment, caveats, table readability, and wording risk.
