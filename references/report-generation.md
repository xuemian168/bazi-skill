# Professional Report Generation

Read this when the user asks for 专业报告, 命理研报, structured report, Markdown report, HTML-style report, or a report-writing workflow for bazi-skill.

Current scope excludes PDF export and offline PDF rendering.

## Boundary

Report generation is a presentation layer. Code must calculate and provide:

- BaZi four pillars, Da Yun, true-solar-time mode, boundary warnings, and lunar/solar conversion metadata.
- `AnalysisResult` timeline and eight-dimension interpretation JSON.
- Zi Wei palaces, stars, Si Hua, Da Xian, and pattern evidence if included.
- Compatibility matrices and pair-level scores if the report is 合盘/合婚.
- Auspicious-timing candidate day/hour pillars, feature labels, and ranking inputs if the report is 择日/择时.

AI may write narrative summaries and section prose, but it must not calculate, verify, or silently alter those facts.

## Required Data Package

Before composing a report, assemble a report data object with:

- `reportTitle`, `subjectName`, `lang`, `generatedAt`, and report type (`natal`, `compatibility`, `auspicious-timing`, or `mixed`).
- Confirmed chart facts: `BaZiResult`, `AnalysisResult`, optional computed Zi Wei facts, optional compatibility result, optional auspicious-timing result.
- Computation metadata: library names and versions, true-solar-time mode, longitude, timezone, equation-of-time use, and whether boundary-hour ambiguity exists.
- Source caveat: cultural/reflective analysis only; not deterministic medical, legal, financial, or relationship advice.
- If the input is an `AnalysisResult`, run `scripts/validate_analysis_result.py` before report composition.

## Report Structure

Use a professional report structure:

1. Cover/heading: title, subject, generated date, report type, and one-line caveat.
2. Executive summary: overall score, main attribute, 3-5 key findings, and confidence/limitations.
3. Computed chart facts: four-pillar table, true-solar-time note, lunar date, Da Yun start age/direction.
4. Visual summary specification: K-line chart notes, score cards, Da Yun timeline, and selected important years.
5. Deep sections: investment, personality, career, wealth, feng shui/environment, relationship, health tendency, family/support.
6. Optional modules: Zi Wei summary, compatibility report, auspicious timing table, manuscript-submission timing notes.
7. Appendix: calculation method, AI boundary, disclaimer, and raw key facts used for interpretation.

For 合盘 reports, replace individual deep sections with relationship dynamics, complementarity, friction matrix, timing synchronization, advice, and caveats. For 择时报表, center the report on ranked candidate windows, score components, avoid windows, and practical submission schedule.

## 依据索引（固定章节）

每份使用典籍条文的报告，末尾必须有「依据索引」章节：

```markdown
## 依据索引

| 卡片ID | 典籍出处 | 原文 | 本盘适用理由 |
|---|---|---|---|
| DTS-0142 | 滴天髓·通神论·衰旺 | 能知衰旺之真机，其于三命之奥，思过半矣。 | 本造月令为寅，藏干齐备，满足该条前提 |
```

规则：

- **正文不带角标。** 中文报告行内堆角标可读性差，且容易退化成本 skill 明令禁止的
  装饰性引用。可追溯性由尾注承担。
- 正文每个结构性论断必须能在依据索引中找到对应行。
- 无典籍支撑的段落（如象法推演）在该段落末尾单独注明
  「该部分为象法推演，无典籍条文支撑」，不进入依据索引表。
- 组稿完成后运行（当前工作目录通常是宿主项目而非 skill 目录，故脚本与
  `references/` 用完整安装路径，`report.md` 相对宿主项目工作目录解析）：

  ```bash
  python3 "${CODEX_HOME:-$HOME/.codex}/skills/bazi-skill/scripts/validate_citations.py" --answer report.md --classics-root "${CODEX_HOME:-$HOME/.codex}/skills/bazi-skill/references/classics"
  ```

  它会检查正文出现的每个卡片 ID 都在依据索引中，且索引中没有不存在的卡片。
  它**不检查**「正文每个结构性论断都有对应索引行」—— 正文不带角标意味着正文里
  按定义没有卡片 ID，这条覆盖关系无法机械判定，只能由裁判与作者执行。
- **依据索引不得空表通过。** 依据索引一条卡片都没列出时，报告必须二选一：写出
  `citations:` 字段（无可引则写 `no_classical_basis`），或在相应段落写明
  「无典籍条文支撑」。校验器会强制这一条 —— 报告免写 `citations:` 的前提正是
  「依据索引表本身就是引用声明」，而空表什么也没声明。
- 依据索引表本身就是报告层的引用声明（卡片ID 列 + 本盘适用理由列），报告
  不需要另外携带 master 输出层的 `citations:` / `citation_fit:` 字段；
  校验器对报告型输入不要求这两个字段存在，若报告中确实写了这两个字段，
  校验器仍会照常检查其内容。
- 若依据索引列出的卡片中有两张互为「竞合」，须在依据索引章节内追加一行
  `rival_resolution: <采纳ID> over <落选ID> — <理由>`，记录取舍依据；这是
  裁判在校勘中的取舍，报告读者应当能看到，不应只存在于裁判的工作记录中。
  校验器会在这种情况下强制要求该行存在。

## Output Routes

Supported routes:

- Structured JSON report spec for downstream app rendering.
- Markdown report for direct user delivery.
- HTML-style report body when the user wants a layout-ready artifact without PDF export.

Do not add a PDF export button, PDF renderer, Chromium print step, or `html2canvas` / `jspdf` dependency unless the user explicitly reopens that requirement.

## Design Standards

- Use clear section hierarchy, compact tables, and readable body text.
- Prefer tables and labeled chart descriptions for computed facts; prose should explain implications, not repeat every number.
- Do not force dense timing or compatibility matrices into many narrow columns. For tables with more than five columns or long rationale text, render each candidate as a compact block: short facts on top, rationale/advice in full-width rows below.
- Ensure Chinese text is readable in Markdown/HTML contexts: use sensible line breaks, adequate line-height when CSS is present, and avoid overpacked table cells.
- Keep claims calibrated: tendency, interaction, timing support, risk point, confidence; never guarantee outcomes.

## QA Checklist

Before delivering a report:

- Confirm the source JSON passed `validate_analysis_result.py` when applicable.
- Confirm report facts match source data: four pillars, start age, Da Yun, peak year, scores, and timing windows.
- Check no section contains uncomputed GanZhi, Zi Wei stars, compatibility relations, or timing facts invented during narrative writing.
- Confirm metadata and AI boundary notes are present.
- Preserve the source JSON alongside the report spec when a reproducible report deliverable is requested.
- Confirm the report has a 依据索引 section covering every structural claim, and that
  `validate_citations.py --answer` passes on the composed report.
