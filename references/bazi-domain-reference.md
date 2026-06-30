# BaZi Domain Reference

Read this for concise BaZi tables and rules needed by Life K-Line prompts, explanations, or lightweight verification. For normal app execution, prefer `lunar-javascript` over manual calculation.

## Ten Heavenly Stems

| Stem | Yin/Yang | Element |
|---|---|---|
| 甲 | yang | wood |
| 乙 | yin | wood |
| 丙 | yang | fire |
| 丁 | yin | fire |
| 戊 | yang | earth |
| 己 | yin | earth |
| 庚 | yang | metal |
| 辛 | yin | metal |
| 壬 | yang | water |
| 癸 | yin | water |

Yang stems: 甲丙戊庚壬. Yin stems: 乙丁己辛癸.

## Twelve Earthly Branches

| Branch | Element | Clock Range |
|---|---|---|
| 子 | water | 23:00-01:00 |
| 丑 | earth | 01:00-03:00 |
| 寅 | wood | 03:00-05:00 |
| 卯 | wood | 05:00-07:00 |
| 辰 | earth | 07:00-09:00 |
| 巳 | fire | 09:00-11:00 |
| 午 | fire | 11:00-13:00 |
| 未 | earth | 13:00-15:00 |
| 申 | metal | 15:00-17:00 |
| 酉 | metal | 17:00-19:00 |
| 戌 | earth | 19:00-21:00 |
| 亥 | water | 21:00-23:00 |

The project relies on `lunar-javascript` for the exact hour pillar after the selected solar-time correction. If explaining Zi time or strict true solar time, read `true-solar-time.md`; traditions vary around 23:00-01:00, and boundary times may require two candidate hour pillars.

## Hidden Stems

| Branch | Main | Middle | Residual |
|---|---|---|---|
| 子 | 癸 |  |  |
| 丑 | 己 | 癸 | 辛 |
| 寅 | 甲 | 丙 | 戊 |
| 卯 | 乙 |  |  |
| 辰 | 戊 | 乙 | 癸 |
| 巳 | 丙 | 庚 | 戊 |
| 午 | 丁 | 己 |  |
| 未 | 己 | 丁 | 乙 |
| 申 | 庚 | 壬 | 戊 |
| 酉 | 辛 |  |  |
| 戌 | 戊 | 辛 | 丁 |
| 亥 | 壬 | 甲 |  |

`utils/wuxing.ts` weights visible stems, branch main element, and hidden stems for UI energy display. Do not treat that UI score as a canonical classical strength calculation.

## Five Elements

Generating cycle: wood -> fire -> earth -> metal -> water -> wood.

Controlling cycle: wood -> earth -> water -> fire -> metal -> wood.

Use favorable/unfavorable elements as interpretive language, not as deterministic instruction.

## Ten Gods

Ten gods are computed relative to the day stem:

| Relationship to Day Master | Same Polarity | Opposite Polarity |
|---|---|---|
| Same element | 比肩 | 劫财 |
| Day master generates target | 食神 | 伤官 |
| Day master controls target | 偏财 | 正财 |
| Target controls day master | 七杀 | 正官 |
| Target generates day master | 偏印 | 正印 |

Life K-Line dimensions can map ten gods to themes:

- 比劫: peers, competition, self-drive.
- 食伤: expression, output, skill, children themes.
- 财星: money, resources, commercial activity.
- 官杀: career pressure, rules, authority, spouse themes in female charts.
- 印枭: learning, support, documents, elders, recovery.

## Branch Relations

- Six clashes: 子午, 丑未, 寅申, 卯酉, 辰戌, 巳亥.
- Six combinations: 子丑, 寅亥, 卯戌, 辰酉, 巳申, 午未.
- Three combinations: 申子辰 water, 亥卯未 wood, 寅午戌 fire, 巳酉丑 metal.
- Three meetings: 寅卯辰 wood, 巳午未 fire, 申酉戌 metal, 亥子丑 water.
- Harms: 子未, 丑午, 寅巳, 卯辰, 申亥, 酉戌.

Use clashes and combinations to explain volatility, but keep the K-line shape consistent with Da Yun and favorable element logic.

## Da Yun Rules

Direction:

- Yang-year male or yin-year female: forward.
- Yin-year male or yang-year female: backward.

Da Yun is counted from the month pillar. In normal app mode, use the library output and skip the first `getDaYun()` entry because it represents the pre-Da-Yun period. In professional mode, generate default Da Yun by stepping stems and branches together from the month pillar.

For timeline text:

- Ages before `startAge`: mention month-pillar / small-luck influence.
- Each Da Yun covers about ten years after `startAge`.
- Changeover years are naturally volatile and can support larger candle ranges.

## Classical Analysis Order

When drafting prompt guidance or prose, use this order:

1. Day master and season/month branch.
2. Element balance and temperature/dryness.
3. Ten-god distribution and visible roots.
4. Chart pattern and useful/favorable elements.
5. Da Yun sequence and life-stage trend.
6. Annual triggers that explain high-volatility years.

Use classical book names only when the actual rule is being applied. Avoid decorative citation.
