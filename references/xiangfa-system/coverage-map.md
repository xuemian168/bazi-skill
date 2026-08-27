# Xiangfa Coverage Map

Read this after `source-map.md`. It tells the orchestrator and `xiangfa-blind-master` what can be used, what is partial, and what must remain `evidence_gap`.

## Coverage Status

| Module | Local file | Status | Source basis | Use policy |
|---|---|---:|---|---|
| 宫位象 | `palace-symbols.md` | covered | `SRC-PROJ-METHODS`, `SRC-PROJ-COMPAT` | Safe for natal, compatibility, and timing context when pillars are confirmed. |
| 十神象 | `ten-god-symbols.md` | covered-partial | `SRC-PROJ-BZ`, `SRC-PROJ-METHODS` | Safe for broad life-scene language; do not overfit exact events. |
| 刑冲合害合象 | `branch-relation-symbols.md` | covered-partial | `SRC-PROJ-BZ`, `SRC-PROJ-METHODS`, `SRC-PROJ-COMPAT` | Safe only when relation matrix is computed or supplied. |
| 组合象 | `combination-patterns.md` | partial | `SRC-PROJ-BZ`, `SRC-PROJ-METHODS`, `SRC-CLASSIC-*` provenance | Use common combinations only when required features are present. |
| 运年触发 | `luck-triggering.md` | covered-partial | `SRC-PROJ-METHODS`, `SRC-PROJ-COMPAT` | Safe for stage/trigger interpretation after Da Yun / Liu Nian are computed. |
| 安全改写 | `safety-rewrites.md` | covered | `SRC-PROJ-SAFETY` | Required for user-facing output. |
| 师承口诀 / 铁口直断 | none | gap | none | Return `evidence_gap`; do not invent. |
| 具体疾病、死亡、牢狱、灾祸公式 | none | prohibited | safety policy | Do not output deterministic claims. Use risk/stress language only if evidence supports it. |
| Complete blind-school encyclopedia | none | gap | none | This repo intentionally does not claim exhaustive coverage. |

## Minimum Evidence For Xiangfa

For natal scene language:

- confirmed four pillars;
- computed ten gods relative to day master;
- hidden-stem / visible-stem context when discussing "透" or "藏";
- branch relation matrix when discussing 冲、合、刑、害、破、三合、三会.

For timing scene language:

- natal facts above;
- current Da Yun;
- Liu Nian or candidate day/hour pillars computed by code;
- event type and practical constraints.

For compatibility scene language:

- confirmed charts for both people;
- relationship type and purpose;
- computed cross-chart branch/stem/ten-god relation matrix.

## Output Discipline

The master should usually select 3-5 high-signal images. More images are not better. Each image needs:

- `feature`: the computed fact;
- `rule_id`: the local xiangfa rule;
- `scene`: cautious interpretation;
- `confidence`: high / medium / low;
- `boundary`: what the evidence cannot prove.

