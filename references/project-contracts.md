# Host Project Contracts

Read this when changing code, prompts, schemas, demo data, or generated analysis JSON for a host repository that uses bazi-skill.

## Repository Anchors

- `types.ts`: shared TypeScript contracts for input, BaZi result, and AI analysis result. Verify before assuming optional Zi Wei types exist.
- `services/baziService.ts`: local BaZi calculation, lunar-to-solar conversion, true solar time, Da Yun, professional mode defaults.
- `utils/wuxing.ts`: stems, branches, elements, hidden stems, ten-god calculation, branch relations, yearly weather.
- `utils/promptGenerator.ts`: manual-mode user prompt.
- `backend/src/routes/analyze.ts`: request validation, CDKEY requirement, cache, provider dispatch.
- `backend/src/services/gemini.ts`: Gemini response schema and prompt.
- `backend/src/services/claude.ts`: Claude prompt and JSON parsing.
- `components/BaZiConfirmation.tsx`: user confirmation/editing of four pillars and Da Yun before AI analysis.
- `components/AnalysisSection.tsx`: analysis display, report tab, K-line chart, Da Yun timeline, and share workflow.
- `services/demoData.ts`: demo `BaZiResult` and `AnalysisResult`; update when contracts change.

Zi Wei note: do not assume `services/ziweiService.ts`, `components/ZiWeiChartPanel.tsx`, `iztro`, or `ZiWeiChart` are part of the tracked repo. Verify with `git ls-files` and the current file tree before referencing or editing them. If present only as untracked local files, treat them as draft/local state, not repository contract.

## Input Contracts

`UserInput`:

```ts
{
  name: string;
  gender: 'Male' | 'Female';
  birthDate: string;      // YYYY-MM-DD
  birthTime: string;      // HH:mm
  birthLocation: string;
  longitude: number;      // east positive, west negative
  inputMode?: 'normal' | 'professional';
  calendarType?: 'solar' | 'lunar';
}
```

`ProfessionalInput` accepts user-entered pillars and optional `birthYear`, `startAge`, `direction`, `daYun`. In this mode, the app builds a pseudo `UserInput` for compatibility. Do not infer that pseudo `birthDate`, `birthTime`, or longitude are real birth facts.

## Calculation Contract

- Lunar input is converted to solar with `Lunar.fromYmd(...).getSolar()` before true solar time.
- Current app mode uses a legacy longitude-only correction: `(longitude - 120) * 4` minutes added to clock time. Treat this as compatibility behavior, not full astronomical apparent solar time.
- Strict apparent solar time requires timezone-standard-meridian correction plus equation of time. See `references/true-solar-time.md`.
- Four pillars come from `lunar.getEightChar()`: `getYearGan/Zhi`, `getMonthGan/Zhi`, `getDayGan/Zhi`, `getTimeGan/Zhi`.
- Da Yun comes from `eightChar.getYun(genderCode)`, where `Male` maps to `1`, `Female` maps to `0`.
- `startAge` currently uses `yun.getStartYear()`.
- Normal mode Da Yun starts from `yun.getDaYun()[1]`; the first entry is skipped because it represents pre-Da-Yun time.
- Professional mode default direction follows: yang-year male or yin-year female = `Forward`; yin-year male or yang-year female = `Backward`.
- Professional mode default `startAge` is approximate: `5` for forward cases, `6` for backward cases.

## AI Boundary Contract

Code owns all deterministic astrology/calendar facts:

- BaZi four pillars.
- Lunar/solar conversion and solar-time adjustment.
- Da Yun direction, start age, and pillars.
- Liu Nian / candidate day / candidate hour GanZhi.
- Zi Wei palaces, stars, Da Xian, and pattern evidence only if a tracked implementation or supplied evidence packet computes them.
- Compatibility feature matrices.
- Auspicious timing candidate pillars and branch/stem relations.

AI may only:

- Interpret supplied facts.
- Explain why a computed feature matters.
- Rank candidates from supplied feature tables.
- Write user-facing summaries, caveats, and advice.
- Format structured JSON that matches already-defined contracts.

Prompts must not ask AI to calculate or verify the chart from raw birth data. If raw birth data appears in a prompt, include a stronger instruction that the computed chart is authoritative and raw data is context only.

## Future Strict Solar Time Contract

If implementing strict true solar time:

- Add `solarTimeMode` with values like `legacy-cn-meridian`, `local-mean-solar`, and `strict-apparent-solar`.
- Add `timezoneOffsetMinutes` or an IANA timezone identifier to normal-mode inputs.
- Include `solarTimeMode` and timezone data in cache keys because they can change the hour pillar and analysis.
- Return a structured `SolarTimeResult` with longitude correction, equation-of-time correction, total offset, and boundary warning.
- Show both hour-pillar possibilities when adjusted time is near a two-hour boundary or strict and legacy modes disagree.
- Never apply solar-time correction to professional-mode pillars after the user has supplied/confirmed them.

## BaZiResult Contract

```ts
{
  userInput: UserInput;
  solarTime: string;
  lunarDate: string;
  bazi: {
    year: { gan: string; zhi: string };
    month: { gan: string; zhi: string };
    day: { gan: string; zhi: string };
    hour: { gan: string; zhi: string };
  };
  startAge: number;
  direction: string;      // "Forward" or "Backward"
  daYun: string[];
}
```

Do not add `ziwei?: ZiWeiChart` to the current contract unless the tracked repo actually includes the Zi Wei type, service, UI, demo data, and prompt/report handling needed to support it.

## Backend Analyze Request

`POST /api/v1/analyze` requires:

```json
{
  "bazi": {
    "year": {"gan": "甲", "zhi": "子"},
    "month": {"gan": "乙", "zhi": "丑"},
    "day": {"gan": "丙", "zhi": "寅"},
    "hour": {"gan": "丁", "zhi": "卯"}
  },
  "birthYear": 1990,
  "startAge": 5,
  "daYun": ["..."],
  "gender": "Male",
  "lang": "zh",
  "provider": "gemini",
  "cdkey": "..."
}
```

`cdkey` can also be sent in the `X-CDKEY` header. The route consumes a CDKEY even on cache hits.

## AnalysisResult Contract

Provider output is normalized by backend services to include:

```ts
{
  bazi: BaZiChart;
  birthYear: number;
  startAge: number;
  daYun: string[];
  mainAttribute: string;
  overallScore: number;
  generalComment: string;
  investment: {
    content: string;
    rating: number;
    opportunityYear: string;
    style: string;
  };
  personality: { content: string; rating: number };
  career: { content: string; rating: number };
  wealth: { content: string; rating: number };
  fengShui: { content: string; rating: number };
  marriage: { content: string; rating: number };
  health: { content: string; rating: number };
  family: { content: string; rating: number };
  volatilityAnalysis: string;
  timeline: YearlyFortune[];
}
```

`YearlyFortune`:

```ts
{
  year: number;
  age: number;
  open: number;
  close: number;
  high: number;
  low: number;
  summary: string;
  detailedReview: string;
  isPeak?: boolean;
}
```

## Timeline Rules

- Exactly 100 entries.
- Entry 1: `year = birthYear`, `age = 1`.
- Entry 100: `year = birthYear + 99`, `age = 100`.
- Before `startAge`, describe small-luck / month-pillar influence rather than Da Yun.
- For any year, `high >= max(open, close)` and `low <= min(open, close)`.
- Values must stay within `0..100`.
- Include at least one rising candle (`close > open`) and one falling candle (`close < open`).
- Exactly one entry should have `isPeak: true`.

## Change Checklist

When changing analysis fields:

- Update `types.ts`.
- Update frontend components that render the field.
- Update `backend/src/services/gemini.ts` response schema.
- Update `backend/src/services/gemini.ts` and `backend/src/services/claude.ts` prompts.
- Update `utils/promptGenerator.ts` for manual mode.
- Update `services/demoData.ts` and any example JSON.
- Run `npm run build` at the repository root.

When changing request fields:

- Update `backend/src/routes/analyze.ts` zod schema.
- Update `services/aiService.ts` request body.
- Update cache-key behavior if the new field affects output.
- Update docs or environment examples if deployment behavior changes.
- For solar-time mode changes, update `baziService.ts`; if a tracked Zi Wei service exists, update it to share the same correction utility.

## Future Compatibility Feature Contract

Do not reuse `AnalysisResult` for two-person compatibility. Add a pair-level contract if implementing 合盘:

- `CompatibilityInput`: person A, person B, relationship type, optional timeframe, optional confirmed charts.
- `CompatibilityResult`: overall score, confidence, strengths, frictions, timing, advice, and a branch/stem interaction matrix.
- Keep both natal chart calculations local and confirmed before AI explanation.
- If AI is used, send computed features only; do not ask the model to calculate either chart.

## Report Artifact Contract

Professional reports are presentation artifacts over computed data. They may include `BaZiResult`, `AnalysisResult`, optional computed Zi Wei output, compatibility output, or auspicious-timing output, but must not trigger fresh AI calculation or let AI invent deterministic facts during report composition.

Current scope excludes PDF export and offline PDF rendering. Keep reports as structured text, Markdown, or HTML-style content unless the user explicitly asks to reintroduce a PDF feature later.

For report composition:

- Reuse the current computed result shown in `components/AnalysisSection.tsx`.
- Validate `AnalysisResult` JSON with `scripts/validate_analysis_result.py` before using it as report source data.
- Preserve report-source JSON or enough metadata to reproduce the report.
- Include computation metadata: library versions, true-solar-time mode, longitude/timezone, equation-of-time use when strict mode is active, chart confirmation status, and the AI boundary note.

## Prompt Guardrails

Always include:

- "Input Data (CONFIRMED BY USER - DO NOT RECALCULATE, USE AS TRUTH)"
- "The BaZi chart, Da Yun, annual/day/hour pillars, and other calendar facts were computed by code. Interpret these facts only."
- Exact 100-year timeline requirements.
- Valid JSON only.
- Language instruction for `zh` or `en`.
- A reminder that the chart needs both upward and downward candles.

Avoid:

- Asking the model to recalculate the chart from birth data after the user has confirmed it.
- Asking the model to invent Liu Nian, day/hour GanZhi, Zi Wei stars, Da Yun, or compatibility relations.
- Adding fields that the frontend does not render or validate.
- Replacing deterministic local calculations with AI-generated pillars.
