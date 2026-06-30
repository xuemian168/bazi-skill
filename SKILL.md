---
name: life-kline-bazi
description: Specialized workflow for Life K-Line / 人生K线 BaZi and optional Zi Wei work. Use when the user asks to build, debug, validate, or improve this lifeline-k project, BaZi 八字排盘, 四柱, 大运, 流年, 紫微斗数, 人生K线, fortune K-line JSON, AI prompt/schema alignment, lunar-javascript or optional deterministic Zi Wei chart logic, true solar time, 真太阳时, 均时差, 时辰边界, compatibility/synastry analysis, 合盘, 合婚, 八字合盘, 关系匹配, 伴侣匹配, auspicious date/hour selection, 择日, 择时, 吉日, 吉时, professional report writing, structured reports, 专业报告, 命理研报, multi-school master/referee workflows, 多流派大师, 大师会诊, 裁判综合, or asks for analysis output that must match the app's AnalysisResult contract.
---

# Life K-Line BaZi

Use this skill for project-aware BaZi, optional Zi Wei Dou Shu evidence, and "Life Stock Market" K-line work. Preserve the app's existing source-of-truth split: local libraries calculate charts; AI writes structured interpretation against a confirmed chart.

## Workflow

1. Classify the task:
   - Code change in `lifeline-k-`: read the repository docs and the touched modules before editing. Start with `CLAUDE.md`, then the relevant `components/CLAUDE.md`, `services/CLAUDE.md`, `types/CLAUDE.md`, or `constants/CLAUDE.md` if present.
   - Skill or workflow architecture change, including requests to reference `ai-berkshire`, a multi-agent research/team pattern, multi-school masters, 大师会诊, or 裁判综合: update this skill or related skill docs first; do not change frontend/backend application code unless the user explicitly asks for implementation.
   - Analysis JSON generation, repair, or validation: read `references/project-contracts.md`, then run `scripts/validate_analysis_result.py` on any candidate JSON.
   - BaZi rules, prompt wording, scoring logic, or domain explanation: read `references/bazi-domain-reference.md`, then `references/analysis-methods.md` when the task needs interpretation or ranking.
   - True solar time, strict apparent solar time, timezone, longitude correction, equation of time, or boundary-hour issues: read `references/true-solar-time.md`; if implementing, also read `references/project-contracts.md`.
   - Zi Wei chart logic, palace display, or pattern wording: read `references/ziwei-reference.md`.
   - Compatibility or synastry analysis, 合盘, 合婚, 伴侣匹配, relationship fit, or partnership matching: read `references/compatibility-analysis.md`, plus `references/analysis-methods.md`; if the task is also app implementation, read `references/project-contracts.md`.
   - Auspicious date/hour selection, 吉日吉时, 择日, or 择时: read `references/auspicious-timing.md` and `references/analysis-methods.md`; if the task is also app implementation, read `references/project-contracts.md`.
   - Professional report, 命理研报, structured report, Markdown report, or HTML report workflow: read `references/report-generation.md` and `references/project-contracts.md`; if using an `AnalysisResult`, validate the JSON before composing the report.

2. Apply an information-completeness gate before analysis, JSON generation, report rendering, or multi-agent work:
   - If required user information is missing, ask follow-up questions before proceeding. Do not guess birth facts, chart facts, event constraints, relationship counterpart data, or report scope.
   - Ask only the missing essentials, preferably 1-3 concise questions at a time.
   - For normal BaZi calculation, required essentials are: gender, birth date, birth time, calendar type (solar/lunar if ambiguous), birthplace or longitude/timezone basis, and whether true solar time should use the current legacy method or strict apparent solar time when that distinction matters. For Zi Wei, first verify that the current repo actually contains a tracked implementation and contract; otherwise treat Zi Wei as unavailable or planned.
   - For professional-mode chart input, required essentials are: four pillars and gender. Birth year, startAge, direction, and daYun can use documented defaults only when the user accepts approximate/professional-mode behavior.
   - For compatibility/synastry, require both people’s chart inputs or confirmed charts plus the relationship goal/context.
   - For auspicious timing, require event type, candidate date range, location/timezone, and any hard constraints before ranking dates/hours.
   - For professional reports, require the source `BaZiResult`, `AnalysisResult`, or report-spec JSON and the desired output format/scope before rendering.
   - Optional missing details may be handled with explicit assumptions only when the final output remains contract-valid and the user request is not asking for precision.

## Multi-School Masters + Referee Pattern

Use this pattern when the user asks for an `ai-berkshire`-style team workflow, multi-agent analysis, 多流派大师, 大师会诊, 裁判综合, deep review, report generation, or a complex task where different mainstream schools should be compared. For role details, read `references/agent-roles.md`; for executable school prompts, read `references/school-prompts/index.md` and only the selected role prompt files.

### Three-layer design

1. **Skill layer**: The skill is the scenario entry point. It decides the workflow, required references, output contract, and validation gates.
2. **School-master layer**: Parallel master personas represent different mainstream schools. They perform school-specific interpretation from the same evidence packet. They do not own source-of-truth calculations and do not emit final app contracts directly.
3. **Tool/validator layer**: Local deterministic libraries and scripts are the authority for chart facts, schema checks, JSON validation, and report composition.

### Referee workflow

For complex BaZi/Zi Wei/K-line work, the main agent acts as **referee / 裁判**:

1. Build an evidence packet from code-computed facts, validated JSON, user constraints, and relevant references.
2. Load `references/school-prompts/index.md`, then assign only the school masters needed for the task: 子平格局, 旺衰扶抑, 调候, 盲派象法, 神煞辅助, 紫微, 择日, 合盘, and safety/report roles as applicable.
3. Load each selected master's corresponding prompt file from `references/school-prompts/` before dispatching or simulating that role.
4. Require each master to return school-specific thesis, evidence, risks, confidence, and recommended wording. Masters may not recalculate chart facts.
5. Compare school disagreements explicitly; resolve by source hierarchy: code facts > project contract > task-specific method fit > cross-school consensus > narrative preference.
6. The referee synthesizes the final answer, JSON, or report. Do not average school scores mechanically.
7. Validate final artifacts with deterministic scripts before treating them as ready.

### Execution rules

- Start school masters in parallel only when the task is large enough to benefit from independent views. For small edits, use a single-agent workflow.
- Do not start parallel masters until the information-completeness gate has passed or the user has explicitly accepted the stated assumptions.
- Every master prompt must include: "CONFIRMED BY USER - DO NOT RECALCULATE, USE AS TRUTH" and the relevant confirmed facts.
- Give each master the same source-of-truth evidence packet plus only the references required for its school.
- If a selected prompt file says the current project lacks a complete knowledge base for that sub-school, preserve that limitation in the master output as `evidence_gap` instead of inventing rules.
- Master outputs should be concise findings, risks, evidence, scores, or section edits. The referee must synthesize; do not paste master reports together.
- The referee owns final decisions, contract shape, JSON repair, and user-facing wording.
- Validate every final `AnalysisResult` with `scripts/validate_analysis_result.py` before treating it as ready.
- For professional reports, run the report-generation workflow after JSON validation; masters may review sections, but final prose consumes computed/validated data only.
- Do not implement runtime multi-agent behavior in the frontend/backend unless the user explicitly asks for an app code change.

3. Keep calculation authority local:
   - Normal birth input uses `services/baziService.ts` with `lunar-javascript`.
   - Convert lunar input to solar before true-solar-time adjustment.
   - Current project true-solar-time behavior is a legacy longitude correction: `clock time + (longitude - 120) * 4 minutes`.
   - For strict apparent solar time, add timezone-standard-meridian handling and equation-of-time correction; see `references/true-solar-time.md`.
   - Da Yun from `lunar.getEightChar().getYun(genderCode)` is authoritative when normal birth data is available.
   - Professional mode accepts user-entered pillars as truth and only fills defaults for missing `startAge`, `direction`, and `daYun`.
   - Do not assume the repo contains a Zi Wei service. Verify tracked/present files before referencing any path such as `services/ziweiService.ts` or `components/ZiWeiChartPanel.tsx`.
   - If Zi Wei is implemented, its palaces, stars, Si Hua, Da Xian, and pattern evidence must still come from deterministic code or a vetted library; do not hand-roll these facts in AI text.
   - Never ask an AI model to calculate or recalculate BaZi, Da Yun, Liu Nian GanZhi, Zi Wei palaces/stars, compatibility matrices, or auspicious timing pillars. Code must compute these facts first; AI may only interpret, summarize, explain, rank from supplied features, or polish wording.

4. Treat confirmed chart data as truth:
   - Prompts must tell the AI: "CONFIRMED BY USER - DO NOT RECALCULATE, USE AS TRUTH".
   - Do not let model text contradict `BaZiResult.bazi`, `startAge`, `direction`, `daYun`, `birthYear`, or `gender`.
   - If a user edits pillars in the confirmation screen, downstream analysis must use the edited pillars.
   - When sending data to AI, include computed facts and feature labels, not raw birth details as an invitation to recalculate.

5. After a chart run, advance the conversation with a current-life question:
   - When the user asks to "run", "排盘", or provides birth data without a specific analysis question, first return the computed facts and a concise reading.
   - After the concise reading, ask the user what has been troubling them recently or what domain they want to focus on next, such as career, money, relationship, study, family, health, relocation, timing, or decision pressure.
   - Phrase the follow-up as a natural next step, for example: "如果要继续细看，我需要知道你最近最困扰的是什么；我会结合当前日期、当前大运、流年/流月与这张命盘来推。"
   - For deeper current-period analysis, use the current date, current Da Yun, current Liu Nian, and Liu Yue/Liu Ri when relevant, but keep the confirmed birth chart and Da Yun as source of truth.
   - Do not invent the user's current problem. If the user has not supplied a focus area, ask before giving a detailed current-life judgment.

6. Preserve the Life K-Line contract:
   - Output must be valid JSON, no markdown.
   - Include all top-level `AnalysisResult` fields documented in `references/project-contracts.md`.
   - `timeline` must contain exactly 100 entries, birth year through birth year + 99, ages 1 through 100.
   - Keep OHLC values integers or finite numbers from 0 to 100.
   - Include both rising and falling candles.
   - Mark exactly one `isPeak: true`; backend provider services currently normalize the peak to the highest `high`, tie-breaking by `close`.

7. Produce report artifacts from computed data only:
   - A professional report must consume confirmed `BaZiResult`, `AnalysisResult`, compatibility results, or auspicious-timing feature tables.
   - Do not let the report-generation stage recalculate pillars, true solar time, Zi Wei stars, compatibility relations, or timing candidates.
   - Include computation metadata, method notes, caveats, and source-validation status.
   - Do not offer PDF export or offline PDF rendering; this skill currently supports structured, Markdown, or HTML-style report content only.

8. Edit prompts and schemas together:
   - Frontend manual prompt lives in `utils/promptGenerator.ts`.
   - Backend Gemini prompt/schema lives in `backend/src/services/gemini.ts`.
   - Backend Claude prompt lives in `backend/src/services/claude.ts`.
   - When adding, renaming, or making a field required, update `types.ts`, frontend rendering, backend prompt/schema, demo data, and validation logic together.

9. Use culturally careful output:
   - Frame BaZi/Zi Wei as cultural analysis and reflective guidance, not deterministic medical, legal, or financial advice.
   - Avoid frightening, absolute, or diagnosis-like claims.
   - For investment language, describe temperament, risk style, and timing tendencies; do not recommend specific securities or guaranteed returns.
   - For compatibility language, describe interaction dynamics and risk points; do not frame a relationship as doomed or guaranteed.
   - For auspicious timing, rank candidate windows and explain tradeoffs; do not present a time as guaranteed to cause an outcome.

## Resources

- `references/project-contracts.md`: repository map, TypeScript data contracts, AI provider contract, and output checklist.
- `references/bazi-domain-reference.md`: concise BaZi tables and rule reminders adapted for this app's current implementation.
- `references/analysis-methods.md`: distilled project methods from AlgorithmGuide, llms docs, and module docs for K-line scoring, eight-dimension analysis, and day/hour ranking.
- `references/true-solar-time.md`: current vs strict true solar time, equation-of-time handling, timezone design, and boundary-hour policy.
- `references/compatibility-analysis.md`: two-chart comparison method for 合盘, 合婚, relationship fit, and partnership matching.
- `references/ziwei-reference.md`: optional Zi Wei workflow rules, repo-verification policy, and no-assumption boundaries.
- `references/auspicious-timing.md`: workflow for day/hour granularity, event-type inputs, scoring, and output format for 吉日吉时.
- `references/report-generation.md`: professional structured/Markdown/HTML report workflow, section structure, and QA checklist.
- `references/agent-roles.md`: multi-school master + referee workflow, school roster, evidence packet, and synthesis rules.
- `references/school-prompts/`: executable prompt templates and source-bounded knowledge slices for the referee and each school master.
- `scripts/validate_analysis_result.py`: deterministic validator for candidate Life K-Line `AnalysisResult` JSON.

## Useful Commands

Validate a JSON file:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/life-kline-bazi/scripts/validate_analysis_result.py" result.json
```

Validate stdin with an explicit birth year:

```bash
cat result.json | python3 "${CODEX_HOME:-$HOME/.codex}/skills/life-kline-bazi/scripts/validate_analysis_result.py" --birth-year 1990 -
```
