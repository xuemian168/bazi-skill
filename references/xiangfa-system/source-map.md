# Xiangfa Source Map

Read this before using any `references/xiangfa-system/*` file. The purpose is to keep 盲派象法 / 象法 language source-bounded: every image must point to computed chart facts and a local reference rule.

## Source Hierarchy

1. **Code-computed facts**: BaZi pillars, ten-god tables, hidden stems, branch/stem relation matrices, Da Yun, Liu Nian, day/hour pillars, compatibility features, and optional Zi Wei / astrology / Qi Men / Liu Yao facts. These are always the source of truth.
2. **Project references**: `bazi-domain-reference.md`, `analysis-methods.md`, `compatibility-analysis.md`, `true-solar-time.md`, `common-schools.md`, and task-specific references.
3. **Local xiangfa rule slices**: the files in `references/xiangfa-system/`. These convert confirmed features into scene language.
4. **Public classical source families**: used as provenance context only when a rule has already been distilled into a local slice. Do not quote or invent rules directly from a book title.
5. **Unbundled blind-school oral/modern materials**: not authoritative inside this skill. If a request depends on a named 盲派口诀, teacher lineage, or event formula that is not represented locally, return `evidence_gap`.

## Reference Register

| Source ID | Source | Use inside this skill |
|---|---|---|
| `SRC-PROJ-BZ` | `references/bazi-domain-reference.md` | Stems, branches, hidden stems, five elements, ten gods, branch relation lists, Da Yun reminders. |
| `SRC-PROJ-METHODS` | `references/analysis-methods.md` | Ten-god semantic method, pillar position method, branch-relation weather method, K-line and day/hour ranking method. |
| `SRC-PROJ-COMPAT` | `references/compatibility-analysis.md` | Spouse palace / day-branch weighting, cross-chart branch interaction, ten-god projection. |
| `SRC-PROJ-SAFETY` | `references/project-contracts.md`, `references/report-generation.md` | Output caveats, schema constraints, medical/legal/financial safety language. |
| `SRC-CLASSIC-SMTM` | `三命通會`, public text: <https://zh.wikisource.org/wiki/三命通會> | General 子平 source family for ten-god, pattern, and 神煞 tradition. Use only through local distilled rules. |
| `SRC-CLASSIC-YHZP` | `淵海子平`, public text: <https://zh.wikisource.org/wiki/淵海子平> | General 子平 source family for day-master, month command, ten-god and pattern vocabulary. Use only through local distilled rules. |
| `SRC-CLASSIC-DTS` | `滴天髓`, public text: <https://zh.wikisource.org/wiki/滴天髓> | General source family for balance, flow, transformation, and non-mechanical pattern reasoning. Use only through local distilled rules. |
| `SRC-CLASSIC-QTBJ` | `窮通寶鑑`, public text: <https://zh.wikisource.org/wiki/穷通宝鉴> | 调候 source family. Do not import month-stem formulae unless they are explicitly distilled in a local file. |

## Rule Metadata Standard

Every future xiangfa rule should be writable as:

```yaml
rule_id:
source_basis:
preconditions:
computed_evidence_required:
interpretation_scope:
confidence:
safe_wording:
forbidden_overclaim:
```

If a master output uses a concrete image, include `rule_id` or `source_basis` in `supporting_evidence`. If no local rule supports the claim, write `evidence_gap`.

## Non-Hallucination Rules

- Do not use a classical title as proof by itself.
- Do not claim "盲派断曰" unless the exact rule exists in this repo with source metadata.
- Do not convert symbolic language into deterministic accidents, deaths, diseases, divorce, lawsuits, or guaranteed wealth.
- Do not infer missing chart facts from birth data in text. Ask code to compute first.
- Prefer "可能表现为", "更像是", "容易在某类场景中出现" over certain predictions.

