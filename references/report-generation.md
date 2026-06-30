# Professional Report Generation

Read this when the user asks for 专业报告, 命理研报, structured report, Markdown report, HTML-style report, or a report-writing workflow for Life K-Line.

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
4. Visual summary specification: Life K-Line chart notes, score cards, Da Yun timeline, and selected important years.
5. Deep sections: investment, personality, career, wealth, feng shui/environment, relationship, health tendency, family/support.
6. Optional modules: Zi Wei summary, compatibility report, auspicious timing table, manuscript-submission timing notes.
7. Appendix: calculation method, AI boundary, disclaimer, and raw key facts used for interpretation.

For 合盘 reports, replace individual deep sections with relationship dynamics, complementarity, friction matrix, timing synchronization, advice, and caveats. For 择时报表, center the report on ranked candidate windows, score components, avoid windows, and practical submission schedule.

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
