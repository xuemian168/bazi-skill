# Luck Triggering Symbols

Source basis: `SRC-PROJ-METHODS` K-line / day-hour selection method and `SRC-PROJ-COMPAT` Da Yun synchronization method.

## Core Model

### `XF-LUCK-STATIC-DYNAMIC-001`

- Principle: natal chart is the static structure; Da Yun sets the decade-stage; Liu Nian / Liu Yue / day-hour features trigger concrete weather.
- Safe wording: "原局给结构，大运给阶段，流年/流月/日时给触发点".
- Boundary: do not use natal structure alone to time a specific event.

### `XF-LUCK-DAYUN-001`

- Feature: current Da Yun.
- Scene: long-running environment, resource trend, pressure trend, opportunity style, life-stage focus.
- Preconditions: Da Yun direction and start age are computed or user-confirmed.
- Boundary: a supportive Da Yun does not remove practical constraints or guarantee outcomes.

### `XF-LUCK-LIUNIAN-001`

- Feature: Liu Nian stem/branch and its relation to natal chart / Da Yun.
- Scene: yearly trigger, theme foregrounding, volatility, opening/closing of a practical window.
- Preconditions: Liu Nian is computed by code; branch/stem relations are supplied.
- Boundary: do not locate month/day/hour unless those are computed.

### `XF-LUCK-STACKING-001`

- Feature: repeated support or repeated conflict across natal, Da Yun, Liu Nian, Liu Yue, day, and hour.
- Scene: signal gets louder when several layers point to the same theme.
- Boundary: stacking raises confidence; it still does not prove one fixed event.

### `XF-LUCK-BOUNDARY-001`

- Feature: birth time or event time near a branch boundary, strict true-solar-time uncertainty, or missing longitude.
- Scene: hour-pillar and hour-specific象 should be downgraded.
- Boundary: produce two candidate readings or ask for more precise location/time; do not hide the uncertainty.

## Timing Output

For auspicious timing or day/hour ranking:

- Use computed candidate day/hour pillars and event-type score.
- Explain why a window is better than alternatives.
- Provide best pick, backup, and avoid list when useful.
- Do not say the chosen time guarantees acceptance, wealth, marriage, cure, or success.

