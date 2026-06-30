# Zi Wei Reference

Read this for Life K-Line Zi Wei / 紫微斗数 work. Zi Wei is optional in the current skill because the tracked repository may not contain a Zi Wei service or UI module.

## Repo Verification Gate

Before treating Zi Wei as an implemented project feature, verify the current repository state:

```bash
git ls-files services/ziweiService.ts components/ZiWeiChartPanel.tsx
```

- If these files are not tracked or not present, do not claim the repo contains a Zi Wei implementation.
- Local untracked files are not project source-of-truth unless the user explicitly asks to adopt or implement them.
- Do not list `services/ziweiService.ts`, `components/ZiWeiChartPanel.tsx`, `iztro`, or `calculateZiWei` as current repo facts unless verified.
- If a user asks for Zi Wei analysis but no computed `ZiWeiChart` facts are supplied, return `evidence_gap` or ask to implement/compute the chart first.

## Source-Of-Truth Rule

AI must not calculate Zi Wei palaces, stars, Si Hua, Da Xian, palace order, or pattern evidence.

Valid Zi Wei evidence may come only from:

- A tracked deterministic implementation in the repo.
- A user-supplied confirmed Zi Wei chart.
- A separate code-computed evidence packet explicitly supplied for the task.

If Zi Wei is implemented later, use a vetted library or deterministic algorithm for star placement. Keep BaZi and Zi Wei solar-time handling aligned through shared code; do not let the two systems use different adjusted dates or time branches.

## Optional Implementation Contract

If the project adds Zi Wei support, document the actual tracked implementation here after it exists. A reasonable contract may include:

- Source metadata: solar date, clock time, adjusted solar time mode, longitude/timezone, lunar date, gender, and chart-confirmation status.
- Core chart facts: 命宫, 身宫, 五行局, 命主/身主 if the library supplies them.
- Palaces: twelve palace records with branch/stem, stars, Da Xian age ranges, and flags.
- Stars: major/supportive/pressure/minor classification based on code output.
- Patterns: concise detected patterns with concrete palace/star evidence.
- Confidence: lower confidence when birth time, timezone, or solar-time boundary is uncertain.

Do not add these fields to prompts, reports, or schemas until the repo actually has the corresponding code and types.

## Prompting Rules

When Zi Wei facts are available:

- Tell the AI: `CONFIRMED BY USER - DO NOT RECALCULATE, USE AS TRUTH`.
- Send computed palace/star/pattern facts, not raw birth data as an invitation to recalculate.
- Use Zi Wei as secondary cross-check evidence unless the task is specifically Zi Wei-focused.
- Keep every claim tied to supplied palace, star, Da Xian, or pattern evidence.

When Zi Wei facts are unavailable:

- Say the current evidence packet does not contain computed Zi Wei facts.
- Do not infer Zi Wei from BaZi pillars.
- Do not mention specific stars, palaces, Si Hua, or Da Xian.
- Route app implementation requests through `project-contracts.md` before adding new files or schema fields.
