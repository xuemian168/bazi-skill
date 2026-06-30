# Compatibility Analysis Reference

Read this for 合盘, 合婚, 八字合盘, synastry, relationship compatibility, partner matching, family compatibility, business-partner matching, or app features that compare two people's charts.

## Scope

Compatibility is a two-chart interaction analysis. It is not the same as the single-person `marriage` field in `AnalysisResult`.

Frame output as interaction dynamics, timing tendencies, and practical communication advice. Do not say two people are destined, doomed, guaranteed to marry, or guaranteed to fail.

## Required Inputs

Ask only for missing essentials:

- Relationship type: romantic, marriage, dating, parent-child, family, business partners, team, other.
- Person A and Person B chart data:
  - Preferred: confirmed BaZi charts with gender/role and Da Yun if available.
  - Acceptable: birth date, birth time, location/longitude, calendar type, gender/role.
  - Minimal: four pillars for each person.
- Purpose: overall fit, marriage timing, conflict diagnosis, business partnership, communication advice, date/hour selection.
- Optional timeframe: current year, next 3 years, marriage window, business launch window.

For uncertain birth time or a birth time near a solar-time-adjusted branch boundary, mark hour-pillar and Zi Wei conclusions as low confidence. Keep year/month/day comparisons but avoid hour-specific certainty. Read `true-solar-time.md` when strict true solar time or boundary ambiguity matters.

## Calculation Authority

- Compute each person's chart locally with `lunar-javascript` when raw birth data is supplied.
- If the user provides confirmed charts, treat them as truth.
- Do not ask AI to invent or calculate either person's pillars, Da Yun, Liu Nian, compatibility relations, or Zi Wei palaces.
- Use AI only to explain or summarize computed compatibility features.

## Feature Layers

### 1. Individual Baselines

Summarize each person briefly before comparing:

- Day master, season/month context, element bias.
- Dominant ten-god group.
- Relationship style clues from spouse palace/day branch and relevant spouse star.
- Current Da Yun stage if available.

Keep this short. The focus is the interaction.

### 2. Day-Master Relationship

Compare A day stem and B day stem:

- Same element: resonance, shared temperament; can become competition.
- A generates B: A may support, teach, or spend energy on B.
- B generates A: B may support A.
- A controls B: structure, attraction through difference, or pressure.
- B controls A: same, reversed.

Use polarity and ten-god relation for nuance. Example: one person's stem can appear as the other's 正官, 七杀, 正财, or 食伤, changing the felt dynamic.

### 3. Element Complement

Compare each person's strong elements with the other's useful/favorable needs:

- Partner supplies useful element -> supportive.
- Partner amplifies an already excessive/unfavorable element -> friction or imbalance.
- Missing element is supplied gently -> complement.
- Both charts over-index the same element -> resonance plus excess risk.

Use the UI energy score as a visualization, not as a full classical strength judgment.

### 4. Branch Interaction Matrix

Compare branches across both charts. Weight positions:

- Day branch to day branch: highest relationship weight; spouse-palace interaction.
- Day branch to partner's month branch: high daily-life/work-family friction or support.
- Month branch to month branch: living rhythm, family/work environment.
- Year branch to year branch: background, social/family context.
- Hour branch to hour branch: long-term plans, children, legacy, late-life rhythm; low confidence if birth time uncertain.

Relations:

- 六合 and strong 三合 support affinity, cooperation, and smoother repair.
- 冲 indicates movement, conflict, attraction with instability, or life-direction differences.
- 刑 indicates repeated friction, sensitivity, or unresolved patterns.
- 害 indicates hidden resentment, indirect obstruction, or mismatched assumptions.
- 桃花 triggers visibility/romance but is not automatically stable.

Do not count every minor relation equally. Prefer a weighted matrix and explain the top 3-5 features.

### 5. Heavenly-Stem Relations

Check cross-chart stem relations:

- Five combinations: 甲己, 乙庚, 丙辛, 丁壬, 戊癸.
- Direct clashes: 甲庚, 乙辛, 丙壬, 丁癸.
- Generation/control chains involving day stems, month stems, and visible spouse/wealth/official stars.

Treat "合化" cautiously. A stem combination does not transform unless seasonal/root support exists; otherwise phrase it as "binding/attraction" rather than true transformation.

### 6. Ten-God Projection

For each person, ask: "What does the other person's visible energy become relative to my day master?"

Examples:

- Partner reads as 财星: pragmatism, attraction to resources, spouse-symbol resonance for some charts.
- Partner reads as 官杀: structure, respect, pressure, rules, responsibility.
- Partner reads as 印星: support, protection, learning, dependency risk.
- Partner reads as 食伤: expression, playfulness, creativity, critique risk.
- Partner reads as 比劫: similarity, loyalty, competition, peer dynamic.

Support all relationship types. Do not force heterosexual spouse-star rules when gender/role is unknown or not relevant.

### 7. Da Yun Synchronization

Compare current and next Da Yun cycles:

- Both entering supportive phases -> easier growth window.
- One rises while the other is under pressure -> support/resentment imbalance risk.
- Both under clash-heavy or unfavorable cycles -> external stress tests relationship.
- Da Yun changes within 1-2 years of each other -> major transition window.

For marriage or business timing, combine both charts' Da Yun plus candidate year/day/hour, not one person's chart alone.

### 8. Zi Wei Optional Cross-Check

Use Zi Wei only if both charts are computed reliably:

- Compare life palace themes and body palace behavior.
- Check whether relationship/marriage-related palaces show similar or conflicting styles.
- Compare current Da Xian pressure/support.
- Treat this as secondary evidence. Do not hand-roll Zi Wei star placement.

## Suggested Score Model

Use a 100-point score with visible components:

- 20: core temperament fit (day master, dominant ten-god groups).
- 20: element complement and useful-element support.
- 20: spouse/day-branch and key branch relations.
- 15: communication/conflict pattern from ten-god projection.
- 15: Da Yun timing synchronization.
- 10: practical context and confidence.

If this is business compatibility, shift weights:

- 20 temperament fit.
- 20 resource/skill complement.
- 20 authority/role clarity.
- 15 conflict/decision style.
- 15 timing synchronization.
- 10 practical context and confidence.

Report confidence separately. Low confidence if either birth time is missing, location/timezone is uncertain, or charts were manually entered without confirmation.

## Output Format

Recommended structure:

```markdown
## 合盘结论
Overall score: 76/100
Confidence: medium

Best fit:
- ...

Main frictions:
- ...

Timing:
- ...

Practical advice:
- ...

Caveat:
- Cultural analysis only; relationship quality depends on communication and choices.
```

For app/JSON design, use structured fields:

```ts
interface CompatibilityResult {
  overallScore: number;
  confidence: 'high' | 'medium' | 'low';
  relationshipType: string;
  summary: string;
  strengths: CompatibilityPoint[];
  frictions: CompatibilityPoint[];
  timing: CompatibilityTiming[];
  advice: string[];
  matrix: CompatibilityMatrixItem[];
}
```

## Implementation Notes For This Project

If adding this to `lifeline-k-`:

- Add a dedicated `compatibilityService.ts` rather than embedding it in single-person analysis.
- Reuse `calculateBaZi`, `calculateWuXingEnergy`, `calculateShiShen`, and branch-relation constants from `utils/wuxing.ts`.
- Add a pair-level type instead of reusing `AnalysisResult`.
- Let users confirm both charts before analysis.
- Keep deterministic compatibility features local; if AI is used, send computed features and ask for explanation only.
- Consider separate views:
  - two chart cards,
  - element complement radar,
  - branch interaction matrix,
  - Da Yun overlap timeline,
  - concise advice panel.

## Safety And Tone

- Avoid one-sided blame. Describe patterns as mutual dynamics.
- Avoid "克夫", "克妻", "孤寡", or fatalistic phrasing. Translate into concrete interaction risk.
- For conflict indicators, provide repair strategies.
- For high compatibility, still mention practical risks and autonomy.
