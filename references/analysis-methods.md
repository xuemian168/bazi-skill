# Distilled Analysis Methods

Read this when the task asks for 方法蒸馏, scoring logic, prompt improvement, explanation quality, K-line generation, eight-dimension analysis, or day/hour ranking. These methods are distilled from the project documentation and reference stack in `components/AlgorithmGuide.tsx`, `public/llms-full.txt`, `utils/CLAUDE.md`, and `services/CLAUDE.md`.

## Reference Stack

Use the references as a layered method stack:

- Traditional BaZi texts: chart structure, ten gods, useful/unfavorable elements, pattern logic, Da Yun and Liu Nian interpretation.
- Astronomy/calendar works: solar terms, calendar conversion, GanZhi chronology, true-solar-time handling.
- Cross-disciplinary works: use social and psychological mappings as explanatory metaphors, not as scientific proof.
- Project implementation docs: deterministic calculation and data-contract rules override interpretive prose.

Do not cite a classical text decoratively. Cite or mention a source family only when the method uses that layer.

## Core Separation

Keep four layers separate:

1. Calculation facts: pillars, GanZhi, Da Yun, true solar time, and optional Zi Wei facts only when a tracked implementation or supplied evidence packet computes them.
2. Relationship features: five elements, ten gods, branch relations, hidden stems, weather categories.
3. Scores and ranking: transparent weights and tie-breaks.
4. Narrative: user-facing interpretation, caveats, and practical advice.

AI may help with layer 4 and, if necessary, soft scoring. It should not invent layer 1 facts.

Hard boundary:

- Code calculates BaZi, Da Yun, Liu Nian, day/hour pillars, compatibility matrices, and auspicious timing candidate features. Zi Wei chart facts are included only when a tracked implementation or supplied evidence packet computes them.
- AI interprets and explains those computed features.
- If a result depends on a fact that has not been computed, compute it first or mark it unavailable; do not let AI fill it in.

## Five-Element Method

Use two levels:

- Display energy: follow `utils/wuxing.ts` weights: visible stem 10, branch main element 7, hidden-stem main 5, middle 3, residual 2, then normalize to the largest element as 100.
- Interpretive balance: use the project guide's balance idea: `balance = 1 - standardDeviation / average`. Treat `>0.8` as balanced and `<0.5` as strongly biased.

When there is tension between UI energy and classical strength, say so. UI energy is a visualization, not a full canonical strength judgment.

## Ten-God Semantic Method

Compute ten gods from day stem polarity and five-element relation. Then translate into themes:

- 比劫: self-drive, peers, competition, siblings, cooperation pressure.
- 食伤: output, creativity, expression, technical skill, openness.
- 财星: money, resources, execution toward material goals, spouse themes in male charts.
- 官杀: role pressure, authority, rules, responsibility, spouse themes in female charts.
- 印枭: learning, documents, support, recovery, elders, reflection.

For modern wording:

- Map 食伤 strength to openness/expressiveness only as a metaphor.
- Map 官杀 structure to conscientiousness/rule pressure only as a metaphor.
- Avoid clinical personality claims.

## Position Method

Use pillar positions as context:

- Year pillar: family background, early environment, public/ancestral context.
- Month pillar: parents, work environment, youth and career base; strongest seasonal context.
- Day pillar: self/day master and spouse palace.
- Hour pillar: later life, children, legacy, long-tail outcomes.

When analyzing relationships, combine ten-god identity with pillar position. Example: a 財星 in month pillar speaks differently from a 財星 isolated in hour pillar.

## Branch-Relation Weather Method

Use the app's priority order for quick yearly or daily weather:

1. 六合 -> sunny / smooth.
2. 三合 with two natal matches -> sunny / strong help.
3. 三合 with one natal match -> partly cloudy / potential support.
4. 相冲 -> stormy / change and turbulence.
5. 相刑 -> rainy / friction and repeated obstacles.
6. 相害 -> foggy / hidden resistance.
7. 子午卯酉 -> peach-blossom / relationship or visibility trigger.
8. No relation -> cloudy / ordinary.

Use this as a feature score, not a final fortune judgment. Da Yun and ten-god context can override a simple weather label.

## K-Line Scoring Method

The project guide expresses scores on a 1-10 conceptual scale; the app contract stores OHLC on a 0-100 scale. Normalize consistently.

Suggested factor weights:

- 40% annual branch relation to natal branches.
- 30% current Da Yun stem/branch and its five-element fit.
- 20% annual stem as ten-god relation to day master.
- 10% five-element balancing effect for the natal chart.

Scoring:

- Start from neutral: 5/10 or 50/100.
- Harmonies and useful-element support: +1 to +3 on a 10-point scale.
- Clashes/control against useful structure: -1 to -3.
- Punishment/harm: -0.5 to -1.5.
- Da Yun support or drag: roughly +/-0.5 to +/-1.5.
- Keep values bounded and avoid monotone timelines.

OHLC logic:

- `open` should usually relate to the previous year's `close`.
- `close` represents the year's end-state after annual and Da Yun effects.
- `high` reflects best opportunity; keep `high >= max(open, close)`.
- `low` reflects challenge; keep `low <= min(open, close)`.
- Wider `high-low` is appropriate for clash years, Da Yun changeovers, strong competing signals, or high-risk opportunity years.

Color rule:

- `close > open`: rising candle.
- `close < open`: falling candle.
- The UI uses China A-share semantics: green up, red down.

## Peak-Year Method

Select exactly one peak:

1. Highest `high`.
2. If tied, highest `close`.
3. If still tied, prefer the year inside a supportive Da Yun.
4. Avoid choosing a year dominated by severe clash/punishment unless the narrative frames it as a high-risk breakthrough.

Backend provider services already normalize `isPeak` to one highest-high entry; prompts should still ask for exactly one.

## Eight-Dimension Methods

Use these weights as prompt scaffolding or reviewer heuristics. They are not hard scientific scores.

### Investment

- 财星 quality: 30%.
- 食伤生财 path: 25%.
- 官杀 pressure and constraint: 20%.
- Annual/Da Yun finance opportunity: 25%.

Output should include `opportunityYear`, `style`, `rating`, and a risk caveat. Prefer "risk style" over direct investment recommendations.

### Personality

- Day master strength and season.
- Five-element balance or bias.
- Dominant ten-god group.
- Cross-disciplinary metaphor: 食伤 -> openness/expression, 官杀 -> structure/discipline, 印星 -> learning/reflection, 比劫 -> agency/competition, 财星 -> pragmatism/resource focus.

Avoid diagnostic language.

### Career

- Day master strength: 30%.
- Useful/favorable element and corresponding industry direction: 35%.
- 官印 structure: 20%.
- 食伤 talent/output: 15%.

Use ten-god career mapping: 官杀 management/rules, 印 education/research/culture, 食伤 creative/technical/media, 财 commercial/finance/sales, 比劫 competitive or partnership fields.

### Wealth

- 财星 quality: 35%.
- Pattern level: 30%.
- Da Yun support for wealth: 25%.
- 比劫 loss/competition risk: 10%.

Classify level carefully: subsistence, comfortable, affluent, very high potential. Do not guarantee wealth.

### Feng Shui / Direction

- Useful element: 50%.
- Unfavorable element avoidance: 30%.
- Annual direction concerns: 20%.

Element-direction mapping:

- Wood: east/southeast, green.
- Fire: south, red/purple.
- Earth: center/southwest/northeast, yellow/earth tones.
- Metal: west/northwest, white/metallic.
- Water: north, black/blue.

Keep advice practical: workspace, color, environment, and development direction.

### Marriage

- Spouse star: 35% (female charts often 官杀; male charts often 财星).
- Peach blossom / visibility triggers: 20%.
- Day branch spouse-palace harmony/clash: 25%.
- Annual/Da Yun relationship timing: 20%.

Avoid deterministic marriage claims; phrase as relationship patterns and timing tendencies.

### Health

- Five-element balance: 40%.
- Day master strength: 25%.
- Punishment/clash/harm stressors: 20%.
- Annual health pressure: 15%.

Use only general wellness language. Never diagnose, never replace medical advice.

### Family / Six Kin

- Compute six-kin themes through ten gods.
- Combine with pillar position and strength.
- High score: relevant kin stars present, balanced, and not heavily clashed.
- Low score: missing, excessive, or repeatedly clashed kin indicators.

Frame as relationship dynamics, not fixed family fate.

## Day/Hour Selection Method

For 吉日/吉时, reuse the same feature stack at day/hour granularity:

- Day branch relation to participant chart: primary stability signal.
- Hour branch relation to day branch and participant chart: timing signal.
- Day/hour ten-god relation to the participant's day master: personal fit signal.
- Event type: determines whether to favor stability, visibility, movement, authority, wealth, or harmony.
- Practical constraints: timezone, working hours, fatigue, travel, availability.

Suggested scoring:

- 30% event-type fit.
- 25% day branch and day stem quality.
- 20% hour branch/stem quality.
- 15% personal chart compatibility.
- 10% practical feasibility and confidence.

If no personal chart is supplied, redistribute the personal 15% into event-type fit and practical feasibility.

Tie-breaks:

1. Fewer direct clashes with participant day/year branch.
2. Better event-type fit.
3. More practical window.
4. Higher confidence in input data.

For one-day 吉时 requests, rank Chinese two-hour periods and provide a best pick, backup, and avoid list.

## Compatibility Method

For 合盘, read `compatibility-analysis.md` and keep the distinction clear:

- Single-person marriage analysis studies one chart's relationship tendencies.
- Compatibility analysis compares two confirmed charts and their interaction features.
- Use cross-chart day master relation, element complement, branch interaction matrix, ten-god projection, and Da Yun synchronization.
- Score the interaction with visible components and report confidence separately.
- For marriage timing or wedding-date selection, combine compatibility analysis with the day/hour selection method.

## Narrative Quality Checks

Before finalizing any analysis:

- Every numeric score must have at least one visible reason.
- Every strong claim must point to a feature: Da Yun, branch relation, ten god, element balance, or chart position.
- Do not mix scales without saying whether the score is 1-10 or 0-100.
- Do not contradict confirmed chart facts.
- Do not introduce uncomputed GanZhi, Da Yun, Zi Wei, compatibility, or timing facts in narrative text.
- Include cultural-reference caveats for fortune, health, relationship, and investment content.
