# Western Astrology Reference

Read this for 星座, 西洋占星, zodiac signs, natal chart, rising sign, moon sign, horoscope, Western astrology synastry, composite chart, or cross-system BaZi + astrology reports.

## Scope

Western astrology is an optional evidence layer for bazi-skill. It can enrich reports with a cross-cultural symbolic lens, but it does not replace BaZi, Zi Wei, true-solar-time handling, or deterministic project contracts.

Use it only when Western astrology facts are computed by a deterministic library/service or explicitly confirmed by the user.

## Verification Gate

Do not assume a host project contains a Western astrology service, ephemeris, or UI module. Before referencing implementation paths, verify tracked files and package dependencies with the current repository.

Valid source facts include:

- Sun sign, moon sign, rising/ascendant sign.
- Planetary placements with sign, house, degree, and retrograde status.
- House system and zodiac type if supplied.
- Major aspects and orbs.
- Element and modality distributions.
- Synastry aspects, overlay houses, composite chart facts, or transit facts if computed.

AI must not calculate these facts from raw birth data. This includes seemingly simple sun-sign lookup, because boundary dates, timezone, location, ephemeris, and zodiac system can change the result.

## Calculation Authority

Code or supplied evidence owns:

- Zodiac placements.
- Ascendant and houses.
- Aspects and orbs.
- Transits, progressions, returns, and timing windows.
- Synastry and composite chart relations.

AI may only:

- Interpret supplied placements and aspects.
- Explain why a supplied aspect or distribution matters.
- Compare Western astrology themes with computed BaZi/Zi Wei themes.
- Write calibrated report prose and caveats.
- Mark missing facts as `evidence_gap`.

## Integration With BaZi

Treat Western astrology as a parallel symbolic language:

- BaZi remains the primary Chinese astrology layer for this skill.
- Western astrology can confirm, nuance, or challenge BaZi themes when the supplied facts support that comparison.
- Do not force one-to-one mappings such as "火 = Aries" or "官杀 = Saturn" unless the evidence packet explicitly defines a project-specific mapping.
- Prefer language like "呼应", "形成张力", "补充一个观察角度", or "证据不足".

Useful comparison axes:

- Element emphasis: BaZi five elements vs Western fire/earth/air/water distribution.
- Structure vs expression: ten-god themes vs Saturn/Mars/Mercury/Venus/Jupiter themes if computed.
- Relationship style: spouse palace/relationship stars vs Venus, Mars, Moon, seventh-house, and synastry facts if supplied.
- Timing: Da Yun/Liu Nian vs computed transit/progression windows if supplied.

## Compatibility And Synastry

For 合盘/合婚, use Western astrology only if both charts or synastry facts are computed or user-confirmed.

Acceptable evidence:

- A/B natal placements.
- A/B Venus, Mars, Moon, Sun, ascendant, seventh-house facts.
- Computed inter-chart aspects with orbs.
- House overlays or composite chart placements.
- Transit timing affecting the relationship if computed.

Do not infer synastry from birth data inside the prompt. Do not invent aspects such as "Sun conjunct Moon" unless that relation is present in the evidence packet.

## Output Pattern

When facts are present:

```text
western_astrology_layer:
  confirmed_facts:
  interpretation:
  resonance_with_bazi:
  tension_with_bazi:
  relationship_or_timing_notes:
  evidence_gaps:
  confidence:
```

When facts are absent:

```text
western_astrology_layer:
  evidence_gap: Western astrology facts were not computed or user-confirmed, so this layer is not used.
```

## Safety And Tone

- Frame output as cultural/symbolic reflection, not scientific proof or fate.
- Do not make medical, legal, financial, or relationship guarantees.
- Preserve uncertainty when birth time is unknown, because ascendant, houses, moon sign near boundaries, and timing techniques may change.
- If Western astrology disagrees with BaZi evidence, state the disagreement instead of forcing harmony.
