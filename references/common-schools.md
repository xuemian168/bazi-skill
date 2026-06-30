# Common Schools And Extension Lenses

Read this for additional mainstream schools beyond the default BaZi/Zi Wei/Western astrology set: 纳音, 刑冲合害, 奇门遁甲, 六爻, 梅花易数, 大六壬, modern astrology, traditional astrology, or other cross-school additions.

## Selection Policy

Use these schools as optional lenses. Do not activate every school by default.

- Prefer BaZi core schools for natal structure and K-line scoring.
- Add 纳音 only as auxiliary image language when labels are computed or supplied.
- Add 刑冲合害细分 when branch/stem interaction is central to relationship, timing, or event narrative.
- Add 奇门遁甲 for event timing, launch/submission windows, negotiation, travel, and directional questions only when a deterministic Qi Men plate is supplied.
- Add 六爻 for one-question divination only when a deterministic hexagram is supplied or the user provides a confirmed cast.
- Add Western modern/traditional astrology only when computed astrology facts are supplied.

## Calculation Authority

Code or supplied evidence owns:

- NaYin labels for pillars or candidate dates.
- Branch/stem relation matrices and relation strength/position weights.
- Qi Men plates: Ju, palace layout, gates, stars, gods, stems, value chief/envoy, empty palaces, timing metadata.
- Liu Yao hexagrams: original hexagram, changing lines, resulting hexagram, six relatives, six spirits, day/month influences, useful-god selection if available.
- Mei Hua or Da Liu Ren facts if a future implementation supplies them.
- Western astrology placements, dignity/debility, house rulers, aspects, transits, synastry, or composite facts.

AI must not calculate these from raw dates, times, random numbers, coins, or memory. If the fact is not in the evidence packet, return `evidence_gap`.

## School Notes

### NaYin 辅助

NaYin is useful for poetic material/image language and auxiliary resonance. It should not override day master strength, ten gods, Da Yun, or branch relations.

Use for:

- Report color and concise imagery.
- Cross-checking repeated material themes across pillars.
- Candidate-day nuance when NaYin labels are computed.

Do not use for:

- Primary useful-god selection.
- Concrete event prediction.
- Relationship verdicts.

### Branch-Relation Deep Dive

This lens focuses on supplied branch/stem interactions:

- 六合, 三合, 半合, 冲, 刑, 害, 破.
- Heavenly-stem combinations and clashes.
- Position weights: day branch/spouse palace, month branch/work-family base, hour branch/long-tail plans.
- Relation stacking across natal chart, Da Yun, Liu Nian, candidate day, candidate hour, or pair charts.

It is a high-value reviewer for 合盘 and 择时 because many errors come from over-counting minor relations or ignoring position weight.

### Qi Men Dun Jia 奇门遁甲

Qi Men is a separate plate system, not a BaZi shortcut. Use only when a computed plate exists.

Typical questions:

- Which submission/launch/signing window is better?
- Which direction or action strategy fits an event?
- How does a negotiation/interview/travel window look?

Required evidence:

- Question/event type and location/timezone.
- Computed plate time and method.
- Palace data with gates, stars, gods, stems, and relevant markers.
- Candidate windows if ranking.

### Liu Yao 六爻

Liu Yao is a one-question system. It should not be merged into natal BaZi unless the user asks for a specific question.

Typical questions:

- Should I submit this paper now?
- Will this collaboration move forward?
- Is this offer/interview worth pursuing?

Required evidence:

- The exact question and casting time/source.
- Original hexagram, changing lines, resulting hexagram.
- Six relatives, six spirits, day/month influences, and useful-god labels if computed.

Do not invent a cast. If the user has not cast or the app has not generated one, ask for a deterministic cast workflow or return `evidence_gap`.

## Western Astrology Split

Use `western-astrology-master` for general astrology facts. Use the split masters when the task benefits from a sharper lens:

- `modern-astrology-master`: psychological themes, growth patterns, communication/relationship style, narrative report wording.
- `traditional-astrology-master`: sect, dignity/debility, house rulership, planetary condition, timing testimony when these facts are supplied.

Do not let either school calculate placements or override BaZi facts.

## Recommended Orchestrator Use

- Natal/report: BaZi core schools + optional NaYin + optional modern/traditional astrology + safety.
- Relationship: compatibility + branch-relation deep dive + optional Zi Wei + optional Western synastry + safety.
- Auspicious timing: day-selection + branch-relation deep dive + optional Qi Men plate + safety.
- One-question divination: Liu Yao or Qi Men, not every natal school.
- Academic submission timing: day-selection + personal chart fit + optional Qi Men + optional ShenSha/document-support labels.

## Safety

- Treat all schools as symbolic/cultural analysis.
- Never delay urgent medical, legal, safety, or emergency actions for a divination result.
- Do not stack many weak auxiliary signals to manufacture certainty.
- Preserve disagreement between schools; the orchestrator resolves it with source quality and task fit.
