# Auspicious Timing Reference

Read this for 吉日吉时, 择日, 择时, daily/hourly ranking, launch timing, signing timing, moving timing, travel timing, or similar requests.

## Scope

Treat auspicious timing as candidate-window ranking and cultural interpretation. Do not promise deterministic outcomes. Do not advise delaying urgent medical, legal, safety, or emergency actions for timing reasons.

## Required Inputs

Ask only for missing essentials:

- Event type: signing, launch, opening, moving, wedding/engagement, travel, exam/interview, medical appointment, ritual, other.
- Date range: one day, several candidate days, or a search window.
- Location and timezone for the event.
- Available time window: full day or constrained hours.
- Participants: optional birth data or confirmed BaZi if personal compatibility is requested.
- Optional external timing evidence: computed Qi Men plate(s) or user-confirmed plate facts.
- Hard exclusions: dates/times that cannot be used.

If the user only gives one date and asks for a 吉时, rank the usable two-hour Chinese periods within that date.

## Calculation Stance

- Use local event timezone and clock time for event selection unless the user explicitly asks for true solar time.
- If the user asks for strict true solar time, use `true-solar-time.md`; date/hour selection should use the event location's timezone standard meridian, not a fixed China meridian.
- For app implementation, use a deterministic calendar library such as `lunar-javascript` to derive day GanZhi, hour GanZhi, lunar date, solar terms, and obvious almanac fields if available.
- If a person-specific chart is supplied, treat the confirmed chart as truth. Do not recalculate it unless the user asks.
- If no personal chart is supplied, produce a general event-oriented ranking only.
- If Qi Men is used, its plate facts must be computed by code or supplied as confirmed evidence; do not ask AI to construct a plate from the event time.
- Do not ask AI to calculate candidate day/hour pillars. Generate candidates and feature tables in code, then let AI explain or rank from those supplied facts.

## Event-Type Priorities

Use event type to weight the interpretation:

| Event | Prefer | Avoid / Penalize |
|---|---|---|
| Signing, contract, finance | stability, clear authority, wealth/resource support | strong clash, high volatility, vague or rushed windows |
| Product launch, opening | visibility, growth, support, good opening momentum | stagnant or heavily clashing windows |
| Moving, renovation | stable earth/supportive branches, practical daylight windows | high-conflict or fatigue-prone late hours |
| Wedding, engagement | harmony, combination, peach-blossom only if balanced | strong clash with couple charts, lonely/isolating signals |
| Travel | movement with support, clear weather/logistics fit | clash-heavy or impractical departure times |
| Exam, interview | clarity, learning/support, authority harmony | scattered, over-pressured, or late-night fatigue windows |
| Medical appointment | practical availability and clinician guidance first | never override medical urgency |

## Day/Hour Ranking Heuristics

Score each candidate window with transparent components. Keep the method simple enough for users to inspect.

Base components:

- Calendar fit: day stem/branch and hour stem/branch are coherent with the event type.
- Branch relations: combinations and supportive relations improve the score; clashes, harms, punishments, or repeated pressure lower it.
- Personal fit: penalize direct clashes with the user's day branch/year branch or supplied chart-sensitive branches; favor useful/favorable elements if known.
- Practical fit: daylight, user constraints, business hours, travel feasibility, and fatigue matter.
- Confidence: lower confidence when birth time, location, timezone, or exact candidate windows are uncertain.

Suggested 100-point format:

- 35 points: event-type fit.
- 25 points: day/hour GanZhi harmony.
- 20 points: personal chart compatibility.
- 15 points: practical constraints.
- 5 points: confidence / data completeness.

Adjust weights when no personal chart is available by redistributing personal-fit points into event-type fit and practical fit.

For a more project-aligned scoring model, use `analysis-methods.md`:

- Rank day quality first, then hour quality.
- Treat the day branch relation as the stability signal and the hour branch relation as the execution signal.
- Use the hour stem's ten-god relation to the participant's day master when a personal chart is available.
- Penalize direct clashes with the participant's day branch more heavily than generic weather labels.
- Prefer windows that are both auspicious and usable; a theoretically good late-night hour can lose on practical feasibility.

## Output Format

For a single date, return a compact ranked table:

| Rank | Time Window | GanZhi | Score | Best For | Notes |
|---|---|---|---:|---|---|

Then add:

- Best pick: one clear recommended window.
- Backup pick: one alternate window.
- Avoid: one or more windows to skip, if supported by the scoring.
- Rationale: short explanation using day/hour relation, event fit, and personal fit if supplied.
- Caveat: cultural reference only; practical constraints come first.

For a date-range search, rank dates first, then show the best 1-3 time windows inside each top date.

## Prompting For AI Analysis

When asking an AI provider to explain timing, include:

- Event type and constraints.
- Candidate windows with computed day/hour GanZhi and any personal chart facts.
- Optional computed Qi Men plate facts if the event workflow supports them.
- A strict instruction to rank only the supplied candidates unless asked to search.
- A request for structured output with score, reason, risks, and confidence.

Do not ask the model to invent calendar data. Compute or supply the day/hour pillars first.

## Implementation Notes For This Project

If adding this to a host project:

- Add a dedicated service such as `services/auspiciousTimingService.ts` rather than mixing it into `baziService.ts`.
- Keep deterministic calendar calculation local.
- Add types for candidate windows, score breakdown, and event type.
- Build UI around ranked windows, filters, and explanations; do not reuse the 100-year K-line schema.
- If AI is used, send computed candidate facts and ask only for explanation or wording, not primary calculation.
