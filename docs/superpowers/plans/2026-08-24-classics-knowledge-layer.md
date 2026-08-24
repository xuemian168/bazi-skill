# 古籍知识层（软件层）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立古籍知识层的软件骨架与输出契约 —— 卡片解析、原文机械核对、引用校验、零依赖检索，并改写四处输出契约，使「引用必须可核对」从 prompt 禁令变为可执行校验。

**Architecture:** 在 `scripts/classics/` 下建一个纯标准库包，职责单一的六个模块（正规化 / 卡片解析 / 语料加载 / 模式A规则 / 模式B规则 / 检索）；两个 CLI 薄壳 `validate_citations.py` 与 `search_classics.py` 只做参数解析与输出格式化。测试用 `unittest` + `tests/fixtures/` 固件语料，全链路不依赖真实典籍语料。

**Tech Stack:** Python 3.14（仅标准库：`argparse` / `dataclasses` / `re` / `hashlib` / `pathlib` / `unittest`）；Markdown 文档。

**Spec:** `docs/superpowers/specs/2026-08-24-classics-knowledge-layer-design.md`

**范围:** 本计划覆盖 Spec 第 4、5、6、8、9 章与第 11 章 Phase 1。
Spec Phase 2（语料入库）与 Phase 3/4（卡片编纂与回归）各自另立计划。

---

## Global Constraints

以下为 Spec 的项目级约束，**每个任务都隐含包含本节**：

- 不引入任何第三方 Python 依赖（jieba、chromadb、sentence-transformers 等一律不用）。Spec §2.2
- 不改宿主项目前端/后端应用代码。Spec §2.2
- 卡片 `id` 一经发布不得变更或复用。Spec §5.1
- corpus 入库后行号不得重排（行号是 `corpus` 字段的定位基础）。Spec §7.2
- 本期启用前缀仅 `DTS` / `ZPZQ` / `QTBJ` / `SMTH`；`YHZP` / `SFTK` / `ZWDS` / `XJFF` 视为非法。Spec §5.2
- 层级枚举恰为四值：`核心论断` / `操作规则` / `例证` / `存疑`。Spec §5.3
- 原文比对不做繁简转换，卡片与 corpus 必须字形一致。Spec §5.5
- 白话必须自行撰写，禁止摘抄现代整理本译文。Spec §5.1
- CLI 风格与 `scripts/validate_analysis_result.py` 一致：位置参数取文件、`-` 取 stdin、
  打印 `VALID` / `INVALID` 加 `- <error>` 行、退出码 `0` 有效 / `1` 无效 / `2` 解析失败。
- 不为盲派、紫微、择日、合盘伪造典籍支撑。Spec §2.2、§10

---

## 对 Spec 的偏离与细化（实施前已记录）

| # | 位置 | 偏离/细化 | 理由 |
|---|---|---|---|
| A | Spec §5.5 标点集合 | 在 spec 列举的全角标点之外，追加 ASCII 半角标点 `,.;:?!"'-[]{}<>` | 语料来源含 PDF 抽取与混排文本，半角标点常见；不追加会导致大量假性核对失败 |
| B | Spec §9.1 模式 B 第 3 条 | 「孤证不立」**不做脚本检查**，保留为 §8.2 第 4 条的裁判 prompt 规则 | 「事件级判断」无法从自由文本可靠分类。一个会漏判的假检查比没有检查更危险 —— 它提供虚假的安全感 |
| C | Spec §9.1 模式 B 输入格式 | 定为 master Output Shape 的 `key: value` 文本块（非 JSON）；并要求 `citation_fit` 每行以卡片 ID 开头，新增 `rival_resolution:` 字段 | masters 实际就输出这种文本块；`rival_resolution` 是把 §8.2 第 3 条变成可机械核对的最小新增 |
| D | Spec §11 Phase 1 | 5 张样例卡片与最小 corpus 放 `tests/fixtures/`；`references/classics/cards/` 本期只建带表头的空文件 | 固件语料不得污染真实语料目录，否则 `PROVENANCE.md` 的 sha256 基线从一开始就是假的。真实卡片随 Phase 2 语料落地 |

---

## File Structure

| 文件 | 职责 | 任务 |
|---|---|---|
| `scripts/classics/__init__.py` | 包标记，导出版本常量 | 1 |
| `scripts/classics/normalize.py` | 原文正规化（Spec §5.5）。唯一职责：字符串 → 可比对字符串 | 1 |
| `scripts/classics/cards.py` | 卡片 Markdown 解析 + `Card` / `Rival` / `CorpusRef` 数据类 | 2 |
| `scripts/classics/corpus.py` | 语料加载、行切片、sha256、`PROVENANCE.md` 解析 | 3 |
| `scripts/classics/checks_cards.py` | 模式 A 的 8 条规则（Spec §9.1） | 4 |
| `scripts/classics/checks_answer.py` | 模式 B 的规则 + `key: value` 文本块解析 | 6 |
| `scripts/classics/search.py` | 2-gram TF 检索 | 7 |
| `scripts/validate_citations.py` | CLI 薄壳，`--cards` / `--answer` | 5, 6 |
| `scripts/search_classics.py` | CLI 薄壳 | 7 |
| `tests/__init__.py` | 把 `scripts/` 加入 `sys.path`（唯一一处，DRY） | 1 |
| `tests/test_*.py` | 单元与端到端测试 | 1-7 |
| `tests/fixtures/cards/*.md` | 5 张样例卡片 | 5 |
| `tests/fixtures/corpus/*.txt` + `PROVENANCE.md` | 最小固件语料 | 5 |
| `references/classics/index.md` | 三向路由表 + 契约摘要 | 8 |
| `references/classics/cards/NN-*.md` | 七个主题文件（本期仅表头） | 8 |
| `references/school-prompts/*.md` | master Output Shape 增字段 | 9 |
| `references/agent-roles.md`、`school-prompts/referee.md` | 源层级 + 审计义务 | 10 |
| `references/report-generation.md`、`school-prompts/safety-editor.md` | 依据索引章节 | 11 |
| `references/bazi-domain-reference.md`、`analysis-methods.md`、`school-prompts/index.md`、`SKILL.md`、`README.md` | 旧措辞改写 + 资源清单 | 12 |

**测试命令（全计划统一）：**

```bash
python3 -m unittest discover -s tests -t . -v
```

---

### Task 1: 包骨架、测试跑道与原文正规化

**Files:**
- Create: `scripts/classics/__init__.py`
- Create: `scripts/classics/normalize.py`
- Create: `tests/__init__.py`
- Test: `tests/test_normalize.py`

**Interfaces:**
- Consumes: 无
- Produces:
  - `classics.normalize.normalize(text: str) -> str`
  - `classics.normalize.PUNCTUATION: frozenset[str]`
  - `tests/__init__.py` 建立 `scripts/` 的 import 路径，后续所有测试依赖它

- [ ] **Step 1: 写失败的测试**

创建 `tests/__init__.py`：

```python
"""Test package bootstrap: put scripts/ on sys.path so `import classics` works."""

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
```

创建 `tests/test_normalize.py`：

```python
import unittest

from classics.normalize import normalize


class NormalizeTest(unittest.TestCase):
    def test_strips_all_whitespace_including_fullwidth(self):
        self.assertEqual(normalize("能知 衰旺　之真机\t"), "能知衰旺之真机")

    def test_strips_spec_punctuation(self):
        self.assertEqual(
            normalize("能知衰旺之真机，其于三命之奥，思过半矣。"),
            "能知衰旺之真机其于三命之奥思过半矣",
        )

    def test_strips_ascii_punctuation(self):
        self.assertEqual(normalize("甲木,乙木.丙火!"), "甲木乙木丙火")

    def test_keeps_cjk_and_digits(self):
        self.assertEqual(normalize("十干12支"), "十干12支")

    def test_does_not_convert_traditional_to_simplified(self):
        self.assertNotEqual(normalize("學"), normalize("学"))

    def test_empty_input(self):
        self.assertEqual(normalize(""), "")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest discover -s tests -t . -v`
Expected: FAIL —— `ModuleNotFoundError: No module named 'classics'`

- [ ] **Step 3: 写最小实现**

创建 `scripts/classics/__init__.py`：

```python
"""Classics knowledge layer: card parsing, quote verification, retrieval."""

CARD_TIERS = ("核心论断", "操作规则", "例证", "存疑")

ENABLED_PREFIXES = ("DTS", "ZPZQ", "QTBJ", "SMTH")

RESERVED_PREFIXES = ("YHZP", "SFTK", "ZWDS", "XJFF")

SCHOOLS = (
    "子平格局",
    "旺衰扶抑",
    "调候",
    "盲派象法",
    "神煞辅助",
    "紫微",
    "择日择时",
    "合盘",
)
```

创建 `scripts/classics/normalize.py`：

```python
"""Normalise text before comparing a card quote against corpus source text.

Rules follow spec 5.5: drop all whitespace and punctuation, keep everything
else verbatim. No traditional/simplified conversion — card and corpus must
already agree on glyph form.

The punctuation set is a deliberate superset of the spec list: PDF-extracted
and mixed-source corpora routinely carry half-width punctuation, and omitting
it would cause spurious verification failures. See plan deviation A.
"""

from __future__ import annotations

PUNCTUATION = frozenset(
    "。，、；：？！「」『』《》〈〉（）()·—…“”‘’"
    ",.;:?!\"'-[]{}<>"
)


def normalize(text: str) -> str:
    """Return `text` with whitespace and punctuation removed."""
    return "".join(ch for ch in text if not ch.isspace() and ch not in PUNCTUATION)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest discover -s tests -t . -v`
Expected: PASS，6 tests

- [ ] **Step 5: 提交**

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
git add scripts/classics tests
git commit -m "feat(classics): add package skeleton and quote normalisation"
```

---

### Task 2: 卡片解析器

**Files:**
- Create: `scripts/classics/cards.py`
- Test: `tests/test_cards.py`

**Interfaces:**
- Consumes: `classics.normalize.normalize`
- Produces:
  - `classics.cards.CorpusRef(path: str, start: int, end: int)`
  - `classics.cards.Rival(card_id: str, note: str)`
  - `classics.cards.Card(id, classic, quote, plain, premises, tier, schools, rivals, boundary, corpus, source_file, line)`
    —— `premises`/`schools`/`rivals` 为 `tuple`，`corpus` 为 `CorpusRef`
  - `classics.cards.parse_cards_text(text: str, source_file: str) -> tuple[list[Card], list[str]]`
  - `classics.cards.load_cards(cards_dir: Path) -> tuple[list[Card], list[str]]`

两个返回值均为 `(cards, errors)`；解析层只报**结构性**错误（字段缺失、格式非法），
语义规则（层级枚举、双向竞合、sha256）留给 Task 4。

- [ ] **Step 1: 写失败的测试**

创建 `tests/test_cards.py`：

```python
import textwrap
import unittest

from classics.cards import CorpusRef, Rival, parse_cards_text

VALID = textwrap.dedent(
    """\
    # 旺衰

    ### DTS-0001
    - 典籍: 滴天髓·通神论·衰旺
    - 原文: 能知衰旺之真机，其于三命之奥，思过半矣。
    - 白话: 判旺衰不看五行数量，而看得令、得地、得势三者的实际承载。
    - 适用前提:
      - 已知月令
      - 已知日主
    - 层级: 核心论断
    - 流派: 旺衰扶抑, 子平格局
    - 竞合:
      - ZPZQ-0001 — 子平真诠主张先以月令定格
    - 反例边界: 从格、化格不适用此条
    - corpus: corpus/ditiansui.txt#L3-L3
    """
)


class ParseCardsTest(unittest.TestCase):
    def test_parses_all_fields(self):
        cards, errors = parse_cards_text(VALID, "20-wangshuai.md")
        self.assertEqual(errors, [])
        self.assertEqual(len(cards), 1)
        card = cards[0]
        self.assertEqual(card.id, "DTS-0001")
        self.assertEqual(card.classic, "滴天髓·通神论·衰旺")
        self.assertEqual(card.tier, "核心论断")
        self.assertEqual(card.premises, ("已知月令", "已知日主"))
        self.assertEqual(card.schools, ("旺衰扶抑", "子平格局"))
        self.assertEqual(card.rivals, (Rival("ZPZQ-0001", "子平真诠主张先以月令定格"),))
        self.assertEqual(card.corpus, CorpusRef("corpus/ditiansui.txt", 3, 3))
        self.assertEqual(card.source_file, "20-wangshuai.md")
        self.assertEqual(card.line, 3)

    def test_single_line_corpus_ref_without_end(self):
        text = VALID.replace("#L3-L3", "#L7")
        cards, errors = parse_cards_text(text, "f.md")
        self.assertEqual(errors, [])
        self.assertEqual(cards[0].corpus, CorpusRef("corpus/ditiansui.txt", 7, 7))

    def test_missing_required_field_is_reported(self):
        text = VALID.replace("- 反例边界: 从格、化格不适用此条\n", "")
        cards, errors = parse_cards_text(text, "f.md")
        self.assertEqual(cards, [])
        self.assertTrue(any("反例边界" in e for e in errors), errors)

    def test_bad_corpus_ref_is_reported(self):
        text = VALID.replace("corpus/ditiansui.txt#L3-L3", "ditiansui.txt:3")
        cards, errors = parse_cards_text(text, "f.md")
        self.assertEqual(cards, [])
        self.assertTrue(any("corpus" in e for e in errors), errors)

    def test_bad_rival_line_is_reported(self):
        text = VALID.replace("ZPZQ-0001 — 子平真诠主张先以月令定格", "ZPZQ-0001")
        cards, errors = parse_cards_text(text, "f.md")
        self.assertEqual(cards, [])
        self.assertTrue(any("竞合" in e for e in errors), errors)

    def test_rivals_optional(self):
        text = VALID.replace(
            "- 竞合:\n      - ZPZQ-0001 — 子平真诠主张先以月令定格\n", ""
        )
        cards, errors = parse_cards_text(text, "f.md")
        self.assertEqual(errors, [])
        self.assertEqual(cards[0].rivals, ())

    def test_malformed_card_id_heading_is_ignored_not_crashed(self):
        cards, errors = parse_cards_text("### not-an-id\n- 典籍: x\n", "f.md")
        self.assertEqual(cards, [])
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest tests.test_cards -v`
Expected: FAIL —— `ModuleNotFoundError: No module named 'classics.cards'`

- [ ] **Step 3: 写最小实现**

创建 `scripts/classics/cards.py`：

```python
"""Parse classics knowledge cards from references/classics/cards/*.md.

Card format is fixed by spec 5.4. This module reports structural problems
only (missing fields, malformed values); semantic rules such as tier
enumeration and bidirectional rival closure live in checks_cards.py.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

CARD_HEADING = re.compile(r"^###\s+([A-Z]{3,4}-\d{4})\s*$")
SCALAR_FIELD = re.compile(r"^-\s+([^:：]+)[:：]\s*(.*)$")
LIST_ITEM = re.compile(r"^\s{2,}-\s+(.*)$")
CORPUS_REF = re.compile(r"^(corpus/[A-Za-z0-9_.\-]+)#L(\d+)(?:-L(\d+))?$")
RIVAL_LINE = re.compile(r"^([A-Z]{3,4}-\d{4})\s*(?:—|--)\s*(.+)$")

SCALAR_KEYS = ("典籍", "原文", "白话", "层级", "流派", "反例边界", "corpus")
LIST_KEYS = ("适用前提", "竞合")
REQUIRED_KEYS = SCALAR_KEYS + ("适用前提",)


@dataclass(frozen=True)
class CorpusRef:
    path: str
    start: int
    end: int


@dataclass(frozen=True)
class Rival:
    card_id: str
    note: str


@dataclass(frozen=True)
class Card:
    id: str
    classic: str
    quote: str
    plain: str
    premises: tuple[str, ...]
    tier: str
    schools: tuple[str, ...]
    rivals: tuple[Rival, ...]
    boundary: str
    corpus: CorpusRef
    source_file: str
    line: int


def _split_blocks(text: str) -> list[tuple[str, int, list[str]]]:
    blocks: list[tuple[str, int, list[str]]] = []
    current: tuple[str, int, list[str]] | None = None
    for offset, raw in enumerate(text.splitlines(), start=1):
        heading = CARD_HEADING.match(raw)
        if heading:
            if current is not None:
                blocks.append(current)
            current = (heading.group(1), offset, [])
            continue
        if current is not None:
            if raw.startswith("### ") or raw.startswith("## "):
                blocks.append(current)
                current = None
                continue
            current[2].append(raw)
    if current is not None:
        blocks.append(current)
    return blocks


def _parse_fields(body: list[str]) -> dict[str, object]:
    fields: dict[str, object] = {}
    pending_list_key: str | None = None
    for raw in body:
        if not raw.strip():
            continue
        item = LIST_ITEM.match(raw)
        if item and pending_list_key:
            fields.setdefault(pending_list_key, []).append(item.group(1).strip())
            continue
        scalar = SCALAR_FIELD.match(raw)
        if not scalar:
            continue
        key, value = scalar.group(1).strip(), scalar.group(2).strip()
        if key in LIST_KEYS:
            pending_list_key = key
            fields.setdefault(key, [])
            if value:
                fields[key].append(value)
            continue
        pending_list_key = None
        fields[key] = value
    return fields


def _build_card(
    card_id: str,
    line: int,
    fields: dict[str, object],
    source_file: str,
    errors: list[str],
) -> Card | None:
    where = f"{source_file}:{line} {card_id}"
    ok = True
    for key in REQUIRED_KEYS:
        value = fields.get(key)
        if value is None or (isinstance(value, str) and not value) or value == []:
            errors.append(f"{where}: 缺少必填字段 `{key}`")
            ok = False

    corpus_raw = fields.get("corpus", "")
    corpus_ref = None
    if isinstance(corpus_raw, str) and corpus_raw:
        match = CORPUS_REF.match(corpus_raw)
        if not match:
            errors.append(
                f"{where}: `corpus` 必须形如 corpus/<file>#L<a>-L<b>，实际为 {corpus_raw!r}"
            )
            ok = False
        else:
            start = int(match.group(2))
            end = int(match.group(3)) if match.group(3) else start
            if end < start:
                errors.append(f"{where}: `corpus` 行号区间倒置 L{start}-L{end}")
                ok = False
            corpus_ref = CorpusRef(match.group(1), start, end)

    rivals: list[Rival] = []
    for entry in fields.get("竞合", []) or []:
        match = RIVAL_LINE.match(entry)
        if not match:
            errors.append(
                f"{where}: `竞合` 条目必须形如 `<ID> — <差异说明>`，实际为 {entry!r}"
            )
            ok = False
            continue
        rivals.append(Rival(match.group(1), match.group(2).strip()))

    if not ok or corpus_ref is None:
        return None

    schools = tuple(
        part.strip()
        for part in re.split(r"[,，]", str(fields["流派"]))
        if part.strip()
    )
    return Card(
        id=card_id,
        classic=str(fields["典籍"]),
        quote=str(fields["原文"]),
        plain=str(fields["白话"]),
        premises=tuple(fields["适用前提"]),
        tier=str(fields["层级"]),
        schools=schools,
        rivals=tuple(rivals),
        boundary=str(fields["反例边界"]),
        corpus=corpus_ref,
        source_file=source_file,
        line=line,
    )


def parse_cards_text(text: str, source_file: str) -> tuple[list[Card], list[str]]:
    """Parse one cards/*.md file body. Returns (cards, structural errors)."""
    cards: list[Card] = []
    errors: list[str] = []
    for card_id, line, body in _split_blocks(text):
        card = _build_card(card_id, line, _parse_fields(body), source_file, errors)
        if card is not None:
            cards.append(card)
    return cards, errors


def load_cards(cards_dir: Path) -> tuple[list[Card], list[str]]:
    """Parse every *.md under `cards_dir`, sorted by filename."""
    cards: list[Card] = []
    errors: list[str] = []
    for path in sorted(cards_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        parsed, parse_errors = parse_cards_text(text, path.name)
        cards.extend(parsed)
        errors.extend(parse_errors)
    return cards, errors
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest discover -s tests -t . -v`
Expected: PASS，13 tests

- [ ] **Step 5: 提交**

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
git add scripts/classics/cards.py tests/test_cards.py
git commit -m "feat(classics): parse knowledge cards from markdown"
```

---

### Task 3: 语料加载、行切片与 PROVENANCE 解析

**Files:**
- Create: `scripts/classics/corpus.py`
- Test: `tests/test_corpus.py`

**Interfaces:**
- Consumes: 无（`corpus.py` 不依赖 `cards.py`，保持单向依赖）
- Produces:
  - `classics.corpus.sha256_of(path: Path) -> str`
  - `classics.corpus.read_lines(path: Path) -> list[str]`
  - `classics.corpus.slice_lines(lines: list[str], start: int, end: int) -> str | None`
    —— 越界返回 `None`
  - `classics.corpus.parse_provenance(path: Path) -> tuple[dict[str, str], list[str]]`
    —— `({rel_path: sha256}, errors)`

- [ ] **Step 1: 写失败的测试**

创建 `tests/test_corpus.py`：

```python
import hashlib
import tempfile
import textwrap
import unittest
from pathlib import Path

from classics.corpus import parse_provenance, read_lines, sha256_of, slice_lines


class CorpusTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_sha256_matches_hashlib(self):
        path = self.root / "a.txt"
        path.write_text("甲乙丙", encoding="utf-8")
        expected = hashlib.sha256("甲乙丙".encode("utf-8")).hexdigest()
        self.assertEqual(sha256_of(path), expected)

    def test_read_lines_drops_line_endings(self):
        path = self.root / "a.txt"
        path.write_text("一\n二\n三\n", encoding="utf-8")
        self.assertEqual(read_lines(path), ["一", "二", "三"])

    def test_slice_lines_is_one_indexed_inclusive(self):
        lines = ["一", "二", "三", "四"]
        self.assertEqual(slice_lines(lines, 2, 3), "二三")
        self.assertEqual(slice_lines(lines, 1, 1), "一")

    def test_slice_lines_out_of_range_returns_none(self):
        lines = ["一", "二"]
        self.assertIsNone(slice_lines(lines, 0, 1))
        self.assertIsNone(slice_lines(lines, 1, 3))

    def test_parse_provenance_extracts_sha256_per_file(self):
        path = self.root / "PROVENANCE.md"
        path.write_text(
            textwrap.dedent(
                """\
                # 语料溯源

                ## corpus/ditiansui.txt
                - 来源: https://example.org/a
                - sha256: aa11
                - 公有领域依据: 清代

                ## corpus/qiongtong-baojian.txt
                - sha256: bb22
                """
            ),
            encoding="utf-8",
        )
        mapping, errors = parse_provenance(path)
        self.assertEqual(errors, [])
        self.assertEqual(
            mapping,
            {"corpus/ditiansui.txt": "aa11", "corpus/qiongtong-baojian.txt": "bb22"},
        )

    def test_parse_provenance_reports_section_without_sha256(self):
        path = self.root / "PROVENANCE.md"
        path.write_text("## corpus/a.txt\n- 来源: x\n", encoding="utf-8")
        mapping, errors = parse_provenance(path)
        self.assertEqual(mapping, {})
        self.assertTrue(any("sha256" in e for e in errors), errors)

    def test_parse_provenance_missing_file(self):
        mapping, errors = parse_provenance(self.root / "nope.md")
        self.assertEqual(mapping, {})
        self.assertTrue(any("PROVENANCE" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest tests.test_corpus -v`
Expected: FAIL —— `ModuleNotFoundError: No module named 'classics.corpus'`

- [ ] **Step 3: 写最小实现**

创建 `scripts/classics/corpus.py`：

```python
"""Corpus access: line reads, 1-indexed slicing, and PROVENANCE.md parsing.

Line numbers are the anchor for every card's `corpus` field, so corpus files
must never be re-flowed after ingest (spec 7.2).
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

SECTION = re.compile(r"^##\s+(corpus/[A-Za-z0-9_.\-]+)\s*$")
SHA_FIELD = re.compile(r"^-\s+sha256\s*[:：]\s*([0-9a-fA-F]+)\s*$")


def sha256_of(path: Path) -> str:
    """Hex sha256 of the file's raw bytes."""
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def read_lines(path: Path) -> list[str]:
    """Corpus lines without trailing newlines."""
    return path.read_text(encoding="utf-8").splitlines()


def slice_lines(lines: list[str], start: int, end: int) -> str | None:
    """Join lines `start`..`end` inclusive, 1-indexed. None if out of range."""
    if start < 1 or end < start or end > len(lines):
        return None
    return "".join(lines[start - 1 : end])


def parse_provenance(path: Path) -> tuple[dict[str, str], list[str]]:
    """Map corpus relative path -> recorded sha256. Returns (mapping, errors)."""
    if not path.is_file():
        return {}, [f"缺少 PROVENANCE 清单: {path}"]

    mapping: dict[str, str] = {}
    errors: list[str] = []
    current: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        section = SECTION.match(raw)
        if section:
            if current is not None and current not in mapping:
                errors.append(f"PROVENANCE 段 `{current}` 缺少 sha256 字段")
            current = section.group(1)
            continue
        if current is None:
            continue
        sha = SHA_FIELD.match(raw)
        if sha:
            mapping[current] = sha.group(1).lower()
    if current is not None and current not in mapping:
        errors.append(f"PROVENANCE 段 `{current}` 缺少 sha256 字段")
    return mapping, errors
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest discover -s tests -t . -v`
Expected: PASS，20 tests

- [ ] **Step 5: 提交**

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
git add scripts/classics/corpus.py tests/test_corpus.py
git commit -m "feat(classics): add corpus access and provenance parsing"
```

---

### Task 4: 模式 A —— 卡片库自检的 8 条规则

**Files:**
- Create: `scripts/classics/checks_cards.py`
- Test: `tests/test_checks_cards.py`

**Interfaces:**
- Consumes: `classics.cards.Card` / `Rival` / `CorpusRef`、`classics.corpus.*`、
  `classics.normalize.normalize`、`classics.CARD_TIERS` / `ENABLED_PREFIXES` / `RESERVED_PREFIXES` / `SCHOOLS`
- Produces:
  - `classics.checks_cards.check_cards(cards: list[Card], classics_root: Path) -> list[str]`
    —— `classics_root` 是含 `corpus/` 子目录的目录；返回错误清单，空表示通过

实现 Spec §9.1 模式 A 的 8 条：必填字段（Task 2 已覆盖结构层，此处覆盖语义层）、
ID 唯一与前缀、层级与流派枚举、原文为 corpus 子串、corpus 行号存在、竞合双向、
sha256 一致、未启用前缀报错。

- [ ] **Step 1: 写失败的测试**

创建 `tests/test_checks_cards.py`：

```python
import tempfile
import unittest
from pathlib import Path

from classics.cards import Card, CorpusRef, Rival
from classics.checks_cards import check_cards
from classics.corpus import sha256_of

QUOTE = "能知衰旺之真机，其于三命之奥，思过半矣。"
CORPUS_BODY = "滴天髓\n通神论·衰旺\n能知衰旺之真机其于三命之奥思过半矣\n"


def make_card(**overrides) -> Card:
    base = dict(
        id="DTS-0001",
        classic="滴天髓·通神论·衰旺",
        quote=QUOTE,
        plain="判旺衰看得令得地得势的实际承载。",
        premises=("已知月令",),
        tier="核心论断",
        schools=("旺衰扶抑",),
        rivals=(),
        boundary="从格、化格不适用",
        corpus=CorpusRef("corpus/ditiansui.txt", 3, 3),
        source_file="20-wangshuai.md",
        line=3,
    )
    base.update(overrides)
    return Card(**base)


class CheckCardsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "corpus").mkdir()
        corpus_file = self.root / "corpus" / "ditiansui.txt"
        corpus_file.write_text(CORPUS_BODY, encoding="utf-8")
        (self.root / "corpus" / "PROVENANCE.md").write_text(
            f"## corpus/ditiansui.txt\n- sha256: {sha256_of(corpus_file)}\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_valid_card_passes(self):
        self.assertEqual(check_cards([make_card()], self.root), [])

    def test_duplicate_id_is_reported(self):
        errors = check_cards([make_card(), make_card()], self.root)
        self.assertTrue(any("重复" in e for e in errors), errors)

    def test_reserved_prefix_is_rejected(self):
        errors = check_cards([make_card(id="YHZP-0001")], self.root)
        self.assertTrue(any("尚未启用" in e for e in errors), errors)

    def test_unknown_prefix_is_rejected(self):
        errors = check_cards([make_card(id="ZZZ-0001")], self.root)
        self.assertTrue(any("前缀" in e for e in errors), errors)

    def test_bad_tier_is_reported(self):
        errors = check_cards([make_card(tier="很重要")], self.root)
        self.assertTrue(any("层级" in e for e in errors), errors)

    def test_bad_school_is_reported(self):
        errors = check_cards([make_card(schools=("玄学派",))], self.root)
        self.assertTrue(any("流派" in e for e in errors), errors)

    def test_quote_absent_from_corpus_is_reported(self):
        errors = check_cards([make_card(quote="此句原文不存在于语料")], self.root)
        self.assertTrue(any("原文" in e for e in errors), errors)

    def test_corpus_line_out_of_range_is_reported(self):
        errors = check_cards(
            [make_card(corpus=CorpusRef("corpus/ditiansui.txt", 99, 99))], self.root
        )
        self.assertTrue(any("行号" in e for e in errors), errors)

    def test_missing_corpus_file_is_reported(self):
        errors = check_cards(
            [make_card(corpus=CorpusRef("corpus/nope.txt", 1, 1))], self.root
        )
        self.assertTrue(any("nope.txt" in e for e in errors), errors)

    def test_one_way_rival_is_reported(self):
        a = make_card(id="DTS-0001", rivals=(Rival("ZPZQ-0001", "对立"),))
        b = make_card(id="ZPZQ-0001", rivals=())
        errors = check_cards([a, b], self.root)
        self.assertTrue(any("双向" in e for e in errors), errors)

    def test_bidirectional_rival_passes(self):
        a = make_card(id="DTS-0001", rivals=(Rival("ZPZQ-0001", "对立"),))
        b = make_card(id="ZPZQ-0001", rivals=(Rival("DTS-0001", "对立"),))
        self.assertEqual(check_cards([a, b], self.root), [])

    def test_rival_pointing_at_unknown_card_is_reported(self):
        errors = check_cards([make_card(rivals=(Rival("QTBJ-9999", "x"),))], self.root)
        self.assertTrue(any("QTBJ-9999" in e for e in errors), errors)

    def test_sha256_mismatch_is_reported(self):
        (self.root / "corpus" / "PROVENANCE.md").write_text(
            "## corpus/ditiansui.txt\n- sha256: deadbeef\n", encoding="utf-8"
        )
        errors = check_cards([make_card()], self.root)
        self.assertTrue(any("sha256" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest tests.test_checks_cards -v`
Expected: FAIL —— `ModuleNotFoundError: No module named 'classics.checks_cards'`

- [ ] **Step 3: 写最小实现**

创建 `scripts/classics/checks_cards.py`：

```python
"""Mode A: card library self-check (spec 9.1)."""

from __future__ import annotations

from pathlib import Path

from . import CARD_TIERS, ENABLED_PREFIXES, RESERVED_PREFIXES, SCHOOLS
from .cards import Card
from .corpus import parse_provenance, read_lines, sha256_of, slice_lines
from .normalize import normalize


def _check_identity(cards: list[Card], errors: list[str]) -> None:
    seen: dict[str, Card] = {}
    for card in cards:
        where = f"{card.source_file}:{card.line} {card.id}"
        if card.id in seen:
            first = seen[card.id]
            errors.append(
                f"{where}: 卡片 ID 重复，已在 {first.source_file}:{first.line} 出现"
            )
        else:
            seen[card.id] = card

        prefix = card.id.split("-", 1)[0]
        if prefix in RESERVED_PREFIXES:
            errors.append(f"{where}: 前缀 `{prefix}` 尚未启用，本期不得使用")
        elif prefix not in ENABLED_PREFIXES:
            errors.append(
                f"{where}: 未知前缀 `{prefix}`，本期合法前缀为 {list(ENABLED_PREFIXES)}"
            )


def _check_enums(cards: list[Card], errors: list[str]) -> None:
    for card in cards:
        where = f"{card.source_file}:{card.line} {card.id}"
        if card.tier not in CARD_TIERS:
            errors.append(
                f"{where}: 层级 `{card.tier}` 不在枚举 {list(CARD_TIERS)} 内"
            )
        for school in card.schools:
            if school not in SCHOOLS:
                errors.append(f"{where}: 流派 `{school}` 不在枚举 {list(SCHOOLS)} 内")


def _check_rivals(cards: list[Card], errors: list[str]) -> None:
    by_id = {card.id: card for card in cards}
    for card in cards:
        where = f"{card.source_file}:{card.line} {card.id}"
        for rival in card.rivals:
            target = by_id.get(rival.card_id)
            if target is None:
                errors.append(f"{where}: 竞合指向不存在的卡片 {rival.card_id}")
                continue
            if card.id not in {back.card_id for back in target.rivals}:
                errors.append(
                    f"{where}: 竞合必须双向，{rival.card_id} 未回指 {card.id}"
                )


def _check_quotes(cards: list[Card], classics_root: Path, errors: list[str]) -> None:
    cache: dict[str, list[str] | None] = {}
    for card in cards:
        where = f"{card.source_file}:{card.line} {card.id}"
        rel = card.corpus.path
        if rel not in cache:
            path = classics_root / rel
            cache[rel] = read_lines(path) if path.is_file() else None
        lines = cache[rel]
        if lines is None:
            errors.append(f"{where}: 语料文件不存在 {rel}")
            continue
        chunk = slice_lines(lines, card.corpus.start, card.corpus.end)
        if chunk is None:
            errors.append(
                f"{where}: corpus 行号超出范围 "
                f"L{card.corpus.start}-L{card.corpus.end}（{rel} 共 {len(lines)} 行）"
            )
            continue
        needle = normalize(card.quote)
        if not needle:
            errors.append(f"{where}: 原文正规化后为空，无法校验")
        elif needle not in normalize(chunk):
            errors.append(
                f"{where}: 原文未出现在 {rel}#L{card.corpus.start}-L{card.corpus.end}"
            )


def _check_provenance(cards: list[Card], classics_root: Path, errors: list[str]) -> None:
    referenced = sorted({card.corpus.path for card in cards})
    if not referenced:
        return
    recorded, provenance_errors = parse_provenance(
        classics_root / "corpus" / "PROVENANCE.md"
    )
    errors.extend(provenance_errors)
    for rel in referenced:
        path = classics_root / rel
        if not path.is_file():
            continue
        if rel not in recorded:
            errors.append(f"PROVENANCE 未登记语料 {rel}")
            continue
        actual = sha256_of(path)
        if actual != recorded[rel]:
            errors.append(
                f"{rel} 的 sha256 与 PROVENANCE 不一致："
                f"实际 {actual}，登记 {recorded[rel]}"
            )


def check_cards(cards: list[Card], classics_root: Path) -> list[str]:
    """Run every mode-A rule. Empty list means the card library is valid."""
    errors: list[str] = []
    _check_identity(cards, errors)
    _check_enums(cards, errors)
    _check_rivals(cards, errors)
    _check_quotes(cards, classics_root, errors)
    _check_provenance(cards, classics_root, errors)
    return errors
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest discover -s tests -t . -v`
Expected: PASS，33 tests

- [ ] **Step 5: 提交**

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
git add scripts/classics/checks_cards.py tests/test_checks_cards.py
git commit -m "feat(classics): add mode A card library checks"
```

---

### Task 5: `validate_citations.py --cards` CLI 与 5 张样例卡片

**Files:**
- Create: `scripts/validate_citations.py`
- Create: `tests/fixtures/cards/20-wangshuai.md`
- Create: `tests/fixtures/cards/30-tiaohou.md`
- Create: `tests/fixtures/cards/50-geju.md`
- Create: `tests/fixtures/corpus/ditiansui.txt`
- Create: `tests/fixtures/corpus/ziping-zhenquan.txt`
- Create: `tests/fixtures/corpus/qiongtong-baojian.txt`
- Create: `tests/fixtures/corpus/sanming-tonghui.selected.txt`
- Create: `tests/fixtures/corpus/PROVENANCE.md`
- Test: `tests/test_cli_cards.py`

**Interfaces:**
- Consumes: `classics.cards.load_cards`、`classics.checks_cards.check_cards`
- Produces:
  - CLI: `python3 scripts/validate_citations.py --cards <classics_root>`
  - `--classics-root` 默认 `references/classics`（相对脚本所在仓库根）

固件卡片使用**真实可考的典籍原文**，但语料文件是最小固件片段。
Phase 2 真实语料入库后须重新核对这 5 张卡片的原文与出处。

- [ ] **Step 1: 写固件与失败的测试**

`tests/fixtures/corpus/ditiansui.txt`：

```text
滴天髓（测试固件·最小片段）
通神论·衰旺
能知衰旺之真机，其于三命之奥，思过半矣。
```

`tests/fixtures/corpus/ziping-zhenquan.txt`：

```text
子平真诠（测试固件·最小片段）
论用神
八字用神，专求月令，以日干配月令地支，而生克不同，格局分焉。
论十干得时不旺失时不弱
书云：得时俱为旺论，失时便作衰看，亦是至理。
```

`tests/fixtures/corpus/qiongtong-baojian.txt`：

```text
穷通宝鉴（测试固件·最小片段）
三春甲木·正月
正月之木，余寒犹存，喜火温暖，则无盘屈之患。
```

`tests/fixtures/corpus/sanming-tonghui.selected.txt`：

```text
三命通会（测试固件·最小片段）
论五行生成
五行者，往来乎天地之间而不穷者也，故谓之行。
```

`tests/fixtures/cards/50-geju.md`：

````markdown
# 格局（测试固件）

### ZPZQ-0001
- 典籍: 子平真诠·论用神
- 原文: 八字用神，专求月令，以日干配月令地支，而生克不同，格局分焉。
- 白话: 取用神先看月令，把日干放到月令地支上看生克，格局由此分野。
- 适用前提:
  - 已知日干
  - 已知月令地支
- 层级: 核心论断
- 流派: 子平格局
- 竞合:
  - DTS-0001 — 滴天髓主张先辨衰旺真机，子平真诠主张先以月令定格，取用先后不同
- 反例边界: 月令被合化或月令本身不成格时，须另寻用神，不可硬套月令
- corpus: corpus/ziping-zhenquan.txt#L3
````

`tests/fixtures/cards/20-wangshuai.md`：

````markdown
# 旺衰（测试固件）

### DTS-0001
- 典籍: 滴天髓·通神论·衰旺
- 原文: 能知衰旺之真机，其于三命之奥，思过半矣。
- 白话: 判旺衰不看五行数量，而看得令、得地、得势三者的实际承载。
- 适用前提:
  - 已知月令
  - 已知日主
  - 已知地支藏干
- 层级: 核心论断
- 流派: 旺衰扶抑, 子平格局
- 竞合:
  - ZPZQ-0001 — 子平真诠主张先以月令定格，滴天髓主张衰旺真机先行
- 反例边界: 从格、化格不适用此条，日主已不以自身强弱论
- corpus: corpus/ditiansui.txt#L3

### ZPZQ-0002
- 典籍: 子平真诠·论十干得时不旺失时不弱
- 原文: 书云：得时俱为旺论，失时便作衰看，亦是至理。
- 白话: 「得月令即旺、失月令即衰」这一旧说有其道理，但子平真诠引它是为了随后辨析其不足。
- 适用前提:
  - 已知月令
  - 已知日干
- 层级: 存疑
- 流派: 旺衰扶抑
- 反例边界: 原书引此说后即加辨析，不可作为独立结论使用
- corpus: corpus/ziping-zhenquan.txt#L5

### SMTH-0001
- 典籍: 三命通会·论五行生成
- 原文: 五行者，往来乎天地之间而不穷者也，故谓之行。
- 白话: 五行之所以叫「行」，取其在天地之间往来不息、不会穷尽之义。
- 适用前提:
  - 需要解释五行何以名「行」
- 层级: 核心论断
- 流派: 旺衰扶抑
- 反例边界: 属名义训释，不可用于推断具体强弱或格局
- corpus: corpus/sanming-tonghui.selected.txt#L3
````

`tests/fixtures/cards/30-tiaohou.md`：

````markdown
# 调候（测试固件）

### QTBJ-0001
- 典籍: 穷通宝鉴·三春甲木·正月
- 原文: 正月之木，余寒犹存，喜火温暖，则无盘屈之患。
- 白话: 正月甲木余寒未退，得火温暖则枝干舒展，不致屈曲难伸。
- 适用前提:
  - 日主为甲木
  - 月令为寅
- 层级: 操作规则
- 流派: 调候
- 反例边界: 若原局火已过旺或木已成焚，则不再以火为调候之喜
- corpus: corpus/qiongtong-baojian.txt#L3
````

`tests/fixtures/corpus/PROVENANCE.md`（`sha256` 值在 Step 3 用命令填入，先写占位段落）：

```markdown
# 语料溯源（测试固件）

本目录为**测试固件**，不是真实语料。原文摘句真实可考，但文件本身是为跑通
校验链路而手工编写的最小片段。真实语料入库见 Spec Phase 2。

## corpus/ditiansui.txt
- 来源: 测试固件（手工编写）
- 版本: fixture-v1
- 抓取日期: 2026-08-24
- sha256: PLACEHOLDER
- 公有领域依据: 滴天髓，清代及以前，原文属公有领域
- 清洗步骤: 手工编写最小片段
- 人工抽检: 不适用（固件）

## corpus/ziping-zhenquan.txt
- 来源: 测试固件（手工编写）
- 版本: fixture-v1
- 抓取日期: 2026-08-24
- sha256: PLACEHOLDER
- 公有领域依据: 子平真诠，清·沈孝瞻，原文属公有领域
- 清洗步骤: 手工编写最小片段
- 人工抽检: 不适用（固件）

## corpus/qiongtong-baojian.txt
- 来源: 测试固件（手工编写）
- 版本: fixture-v1
- 抓取日期: 2026-08-24
- sha256: PLACEHOLDER
- 公有领域依据: 穷通宝鉴，清代，原文属公有领域
- 清洗步骤: 手工编写最小片段
- 人工抽检: 不适用（固件）

## corpus/sanming-tonghui.selected.txt
- 来源: 测试固件（手工编写）
- 版本: fixture-v1
- 抓取日期: 2026-08-24
- sha256: PLACEHOLDER
- 公有领域依据: 三命通会，明·万民英，原文属公有领域
- 清洗步骤: 手工编写最小片段
- 人工抽检: 不适用（固件）
```

创建 `tests/test_cli_cards.py`：

```python
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "scripts" / "validate_citations.py"
FIXTURES = REPO / "tests" / "fixtures"


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )


class CliCardsTest(unittest.TestCase):
    def test_fixture_library_is_valid(self):
        result = run_cli("--cards", str(FIXTURES))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("VALID", result.stdout)

    def test_fixture_library_has_five_cards(self):
        result = run_cli("--cards", str(FIXTURES), "--count")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("cards: 5", result.stdout)

    def test_missing_cards_dir_exits_two(self):
        result = run_cli("--cards", str(REPO / "docs"))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_requires_a_mode(self):
        result = run_cli()
        self.assertNotEqual(result.returncode, 0)

    def test_unreadable_card_file_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            classics_root = Path(tmp)
            cards_dir = classics_root / "cards"
            cards_dir.mkdir()
            (cards_dir / "bad.md").write_bytes(b"### DTS-0001\n- \xff\xfe not valid utf-8\n")
            result = run_cli("--cards", str(classics_root))
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest tests.test_cli_cards -v`
Expected: FAIL —— `scripts/validate_citations.py` 不存在，returncode 为 2 且 stderr 含 "No such file"

- [ ] **Step 3: 填入 sha256 并写 CLI**

先算出四份固件语料的 sha256 并替换 `PLACEHOLDER`：

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill/tests/fixtures/corpus
python3 - <<'PY'
import hashlib, pathlib, re
here = pathlib.Path(".")
prov = here / "PROVENANCE.md"
text = prov.read_text(encoding="utf-8")
for path in sorted(here.glob("*.txt")):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    text = re.sub(
        rf"(## corpus/{re.escape(path.name)}\n(?:- .*\n)*?- sha256: )PLACEHOLDER",
        rf"\g<1>{digest}",
        text,
    )
prov.write_text(text, encoding="utf-8")
assert "PLACEHOLDER" not in text, "still has placeholders"
print("provenance filled")
PY
```

创建 `scripts/validate_citations.py`：

```python
#!/usr/bin/env python3
"""Validate classics citations: card library self-check, or answer citation use."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from classics.cards import load_cards
from classics.checks_cards import check_cards


def report(errors: list[str]) -> int:
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID")
    return 0


def run_cards_mode(classics_root: Path, show_count: bool) -> int:
    cards_dir = classics_root / "cards"
    if not cards_dir.is_dir():
        print(f"缺少卡片目录: {cards_dir}", file=sys.stderr)
        return 2

    try:
        cards, parse_errors = load_cards(cards_dir)
    except Exception as exc:  # noqa: BLE001
        print(f"无法读取卡片文件: {exc}", file=sys.stderr)
        return 2

    if show_count:
        print(f"cards: {len(cards)}")
    return report(parse_errors + check_cards(cards, classics_root))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cards",
        metavar="CLASSICS_ROOT",
        help="Card library self-check. Directory containing cards/ and corpus/",
    )
    parser.add_argument("--count", action="store_true", help="Print parsed card count")
    args = parser.parse_args()

    if not args.cards:
        parser.error("请指定 --cards <CLASSICS_ROOT>")
    return run_cards_mode(Path(args.cards), args.count)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest discover -s tests -t . -v`
Expected: PASS，42 tests

再手工验证负例（破坏一字必须被检出）：

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
cp tests/fixtures/cards/20-wangshuai.md /tmp/card-backup.md
sed -i '' 's/思过半矣/思过半矣矣/' tests/fixtures/cards/20-wangshuai.md
python3 scripts/validate_citations.py --cards tests/fixtures; echo "exit=$?"
cp /tmp/card-backup.md tests/fixtures/cards/20-wangshuai.md
python3 scripts/validate_citations.py --cards tests/fixtures; echo "exit=$?"
```

Expected: 第一次 `INVALID` + 含「原文未出现在」+ `exit=1`；恢复后 `VALID` + `exit=0`

- [ ] **Step 5: 提交**

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
git add scripts/validate_citations.py tests/fixtures tests/test_cli_cards.py
git commit -m "feat(classics): add --cards CLI and five sample cards with fixture corpus"
```

---

### Task 6: 模式 B —— 引用使用校验

**Files:**
- Create: `scripts/classics/checks_answer.py`
- Modify: `scripts/validate_citations.py`
- Test: `tests/test_checks_answer.py`

**Interfaces:**
- Consumes: `classics.cards.Card`、`classics.CARD_TIERS`
- Produces:
  - `classics.checks_answer.parse_answer(text: str) -> dict[str, object]`
  - `classics.checks_answer.check_answer(answer: dict, cards: list[Card]) -> list[str]`
  - CLI: `python3 scripts/validate_citations.py --answer <file|-> [--classics-root DIR]`

输入格式（偏离记录 C）：master Output Shape 的 `key: value` 文本块。相关字段：

```text
citations: DTS-0001, ZPZQ-0001        # 或 no_classical_basis
citation_fit:
  DTS-0001 — 本造月令为寅，日主甲木，地支藏干齐备，满足该条前提
  ZPZQ-0001 — 日干与月令地支均已确认
pattern_call: formal_pattern
rival_resolution: ZPZQ-0001 over DTS-0001 — 本任务目标是定格，月令优先
依据索引                                # 报告型输入的判别标记
```

校验规则：

1. 所有引用 ID 存在于卡片库
2. `citations` 字段存在且非空（ID 列表或 `no_classical_basis`）
3. 每个被引 ID 在 `citation_fit` 中有对应行
4. `pattern_call: formal_pattern` 时，至少一张被引卡片层级为 `核心论断` 或 `操作规则`
5. 若两个被引 ID 互为竞合，必须有同时点到两者的 `rival_resolution` 行
6. 报告型输入（含「依据索引」）：正文出现的每个 ID 都要在依据索引段落中出现

**「孤证不立」不在此实现**（偏离记录 B），保留为裁判 prompt 规则。

- [ ] **Step 1: 写失败的测试**

创建 `tests/test_checks_answer.py`：

```python
import textwrap
import unittest

from classics.cards import Card, CorpusRef, Rival
from classics.checks_answer import NO_BASIS, check_answer, parse_answer


def card(card_id: str, tier: str, rivals=()) -> Card:
    return Card(
        id=card_id,
        classic="典籍",
        quote="原文",
        plain="白话",
        premises=("前提",),
        tier=tier,
        schools=("旺衰扶抑",),
        rivals=rivals,
        boundary="边界",
        corpus=CorpusRef("corpus/a.txt", 1, 1),
        source_file="f.md",
        line=1,
    )


LIBRARY = [
    card("DTS-0001", "核心论断", (Rival("ZPZQ-0001", "取用先后不同"),)),
    card("ZPZQ-0001", "核心论断", (Rival("DTS-0001", "取用先后不同"),)),
    card("SMTH-0001", "例证"),
]

GOOD = textwrap.dedent(
    """\
    school: strength-balance-master
    citations: DTS-0001
    citation_fit:
      DTS-0001 — 本造月令与藏干齐备，满足该条前提
    pattern_call: formal_pattern
    """
)


class ParseAnswerTest(unittest.TestCase):
    def test_parses_citations_and_fit(self):
        answer = parse_answer(GOOD)
        self.assertEqual(answer["citations"], ["DTS-0001"])
        self.assertEqual(answer["citation_fit_ids"], ["DTS-0001"])
        self.assertEqual(answer["pattern_call"], "formal_pattern")
        self.assertFalse(answer["is_report"])

    def test_detects_report_input(self):
        answer = parse_answer("依据索引\n| DTS-0001 | 滴天髓 | 原文 | 理由 |\n")
        self.assertTrue(answer["is_report"])

    def test_no_classical_basis_yields_empty_citations(self):
        answer = parse_answer("citations: no_classical_basis\n")
        self.assertEqual(answer["citations"], [])
        self.assertTrue(answer["no_classical_basis"])


class CheckAnswerTest(unittest.TestCase):
    def test_good_answer_passes(self):
        self.assertEqual(check_answer(parse_answer(GOOD), LIBRARY), [])

    def test_no_classical_basis_passes(self):
        text = "school: xiangfa-blind-master\ncitations: no_classical_basis\n"
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])

    def test_missing_citations_field_is_reported(self):
        errors = check_answer(parse_answer("school: x\n"), LIBRARY)
        self.assertTrue(any("citations" in e for e in errors), errors)

    def test_unknown_card_id_is_reported(self):
        text = "citations: DTS-9999\ncitation_fit:\n  DTS-9999 — 理由\n"
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("DTS-9999" in e for e in errors), errors)

    def test_citation_without_fit_is_reported(self):
        text = "citations: DTS-0001\n"
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("citation_fit" in e for e in errors), errors)

    def test_formal_pattern_on_example_tier_only_is_reported(self):
        text = (
            "citations: SMTH-0001\n"
            "citation_fit:\n  SMTH-0001 — 理由\n"
            "pattern_call: formal_pattern\n"
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("层级" in e for e in errors), errors)

    def test_rival_pair_without_resolution_is_reported(self):
        text = (
            "citations: DTS-0001, ZPZQ-0001\n"
            "citation_fit:\n  DTS-0001 — 理由\n  ZPZQ-0001 — 理由\n"
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("rival_resolution" in e for e in errors), errors)

    def test_rival_pair_with_resolution_passes(self):
        text = (
            "citations: DTS-0001, ZPZQ-0001\n"
            "citation_fit:\n  DTS-0001 — 理由\n  ZPZQ-0001 — 理由\n"
            "rival_resolution: ZPZQ-0001 over DTS-0001 — 本任务以定格为目标\n"
        )
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])

    def test_report_body_id_missing_from_index_is_reported(self):
        text = textwrap.dedent(
            """\
            正文提到 DTS-0001 与 ZPZQ-0001。

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | DTS-0001 | 滴天髓 | 原文 | 理由 |
            """
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("依据索引" in e and "ZPZQ-0001" in e for e in errors), errors)

    def test_report_with_complete_index_passes(self):
        text = textwrap.dedent(
            """\
            citations: DTS-0001
            citation_fit:
              DTS-0001 — 理由

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | DTS-0001 | 滴天髓 | 原文 | 理由 |
            """
        )
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])


class ContinuationTerminationTest(unittest.TestCase):
    """Critical #1: a blank line ends a citation_fit/rival_resolution block,
    and continuation lines must be indented and start with the card id —
    not merely mention one anywhere later in the document."""

    def test_report_index_table_does_not_satisfy_citation_fit_or_rival_resolution(self):
        # The decisive case from the finding: a report's 依据索引 table
        # lists every cited id by construction. Before the fix, an empty
        # citation_fit block and a missing rival_resolution both got
        # silently satisfied by the table rows that followed.
        text = textwrap.dedent(
            """\
            citations: DTS-0001, ZPZQ-0001
            citation_fit:

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | DTS-0001 | 滴天髓 | 原文 | 理由 |
            | ZPZQ-0001 | 子平真诠 | 原文 | 理由 |
            """
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("citation_fit" in e for e in errors), errors)
        self.assertTrue(any("rival_resolution" in e for e in errors), errors)

    def test_placeholder_rival_resolution_is_not_satisfied_by_later_prose(self):
        text = (
            "citations: DTS-0001, ZPZQ-0001\n"
            "citation_fit:\n  DTS-0001 — 理由\n  ZPZQ-0001 — 理由\n"
            "rival_resolution: 见下表\n"
            "\n"
            "完整说明另见 DTS-0001 与 ZPZQ-0001 相关条目。\n"
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("rival_resolution" in e for e in errors), errors)


class FieldRecognitionTest(unittest.TestCase):
    """Critical #2: field keys are recognised case-insensitively and when
    indented, by lowercasing the matched key — not by checking it against a
    closed vocabulary. Round 1 tried a closed vocabulary (KNOWN_FIELDS) and
    rejected any other field-shaped line as an error; that rejected every
    real school-prompt Output Shape, which emits many fields this module
    doesn't otherwise care about (scope, core_thesis, confidence, ...).
    Round 2 replaced it with plain normalise-and-ignore: an unrecognised
    key is stored and ignored, exactly as an unindented lowercase one
    always was."""

    def test_capitalised_pattern_call_is_recognised(self):
        text = (
            "citations: SMTH-0001\n"
            "citation_fit:\n  SMTH-0001 — 理由\n"
            "Pattern_call: formal_pattern\n"
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("层级" in e for e in errors), errors)

    def test_indented_pattern_call_is_recognised(self):
        text = (
            "citations: SMTH-0001\n"
            "citation_fit:\n  SMTH-0001 — 理由\n"
            "  pattern_call: formal_pattern\n"
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("层级" in e for e in errors), errors)

    def test_unrelated_field_is_stored_and_ignored_not_reported_as_an_error(self):
        text = (
            "citations: DTS-0001\n"
            "citation_fit:\n  DTS-0001 — 理由\n"
            "confidence: medium\n"
        )
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])


class NoClassicalBasisTest(unittest.TestCase):
    """Critical #3: no_classical_basis must match the whole value, not
    appear as a substring; and it may not coexist with real citation ids."""

    def test_hint_comment_left_on_the_line_does_not_disable_checks(self):
        text = "citations: DTS-9999   # 或 no_classical_basis\n"
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("DTS-9999" in e for e in errors), errors)

    def test_no_classical_basis_mixed_with_real_ids_is_reported(self):
        text = "citations: DTS-0001, no_classical_basis\ncitation_fit:\n  DTS-0001 — 理由\n"
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any(NO_BASIS in e for e in errors), errors)

    def test_no_classical_basis_glued_to_cjk_text_is_still_detected_as_mixed(self):
        # Round 3: NO_BASIS_TOKEN used \b, the exact construct Important #5
        # established as unreliable at a CJK/ASCII boundary in this module.
        # \b does not fire between "用" and "n", so a token glued directly
        # onto Chinese prose with no separating space used to silently skip
        # this diagnostic (the citation ids themselves were still checked
        # normally either way — this only loses the supplementary hint).
        text = "citations: DTS-0001且无引用no_classical_basis\ncitation_fit:\n  DTS-0001 — 理由\n"
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any(NO_BASIS in e for e in errors), errors)


class UnspacedCjkCardIdTest(unittest.TestCase):
    """Important #5: \\b does not fire between a CJK character and an ASCII
    letter/digit, so ids embedded in unspaced Chinese prose must still be
    found via lookaround rather than \\b."""

    def test_unspaced_cjk_prose_ids_are_detected_in_report_body(self):
        text = textwrap.dedent(
            """\
            本造依DTS-0001定格，又参SMTH-0001之例。

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | DTS-0001 | 滴天髓 | 原文 | 理由 |
            """
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(
            any("依据索引" in e and "SMTH-0001" in e for e in errors), errors
        )


class ReportWindowAnchorTest(unittest.TestCase):
    """Important #6: the 依据索引 anchor must be a heading-shaped line, and
    the last such line wins over an earlier one."""

    def test_prose_mention_without_a_heading_is_not_report_mode(self):
        text = (
            "citations: DTS-0001\n"
            "citation_fit:\n  DTS-0001 — 理由\n"
            "完整出处详见依据索引说明文档。\n"
        )
        answer = parse_answer(text)
        self.assertFalse(answer["is_report"])

    def test_repeated_heading_uses_the_last_occurrence(self):
        text = textwrap.dedent(
            """\
            ## 依据索引

            正文提到 ZPZQ-0001，最终依据见下方表格。

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | DTS-0001 | 滴天髓 | 原文 | 理由 |
            """
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(
            any("依据索引" in e and "ZPZQ-0001" in e for e in errors), errors
        )

    def test_trailing_comment_after_heading_marker_is_detected(self):
        # Round 3: the brief's own canonical marker line (task-6-brief.md:24)
        # carries a trailing comment explaining the marker's purpose. The
        # round-1/2 heading regex required the line to end immediately
        # after 依据索引, so an input written exactly as the brief's own
        # documentation shows was not detected as a report at all, silently
        # skipping rule 6 entirely.
        text = (
            "citations: DTS-0001\n"
            "citation_fit:\n  DTS-0001 — 理由\n"
            "依据索引                                # 报告型输入的判别标记\n"
            "| DTS-0001 | 滴天髓 | 原文 | 理由 |\n"
        )
        answer = parse_answer(text)
        self.assertTrue(answer["is_report"])
        self.assertEqual(check_answer(answer, LIBRARY), [])


class DuplicateCitationsFieldTest(unittest.TestCase):
    """Important #7: a repeated citations: key (e.g. from an aggregated
    multi-persona document) must be reported, not silently overwritten."""

    def test_duplicate_citations_field_is_reported(self):
        text = (
            "citations: DTS-9999\n"
            "citation_fit:\n  DTS-9999 — 理由\n"
            "citations: DTS-0001\n"
            "citation_fit:\n  DTS-0001 — 理由\n"
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("citations" in e and "多次" in e for e in errors), errors)


class InlineCitationFitTest(unittest.TestCase):
    """Minor #9: citation_fit written on a single line (the natural way to
    write one citation) must still be counted, not just the multi-line
    indented form."""

    def test_inline_citation_fit_single_line_is_recognised(self):
        text = "citations: DTS-0001\ncitation_fit: DTS-0001 — 月令齐备\n"
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])


# The realistic Output Shape below is what round 1's KNOWN_FIELDS closed
# vocabulary rejected outright: every field here is one the current
# references/school-prompts/*.md Output Shape blocks already require, and
# round 1 flagged seven of them (scope, core_thesis, supporting_evidence,
# counter_evidence, warnings, confidence, recommended_wording) as
# "无法识别的字段". This is the test whose absence let that ship.
REALISTIC_MASTER_OUTPUT = textwrap.dedent(
    """\
    school: ziping-pattern-master
    scope: 全局
    core_thesis: 月令为寅
    pattern_call: pattern_tendency
    supporting_evidence: 略
    counter_evidence: 略
    warnings: 略
    citations: DTS-0001
    citation_fit:
      DTS-0001 — 月令与藏干齐备
    confidence: medium
    recommended_wording: 略
    """
)


class RealisticMasterOutputShapeTest(unittest.TestCase):
    def test_full_school_prompt_output_shape_with_many_fields_passes(self):
        self.assertEqual(
            check_answer(parse_answer(REALISTIC_MASTER_OUTPUT), LIBRARY), []
        )


class ContinuationLineIsNotAFieldTest(unittest.TestCase):
    """Round 2's flagged interaction with round 1's continuation-state
    fix: a citation_fit continuation line is indented and starts with an
    uppercase card id followed by a space and an em dash, not by a colon,
    so FIELD must not match it — verified explicitly rather than reasoned
    about, including a reason string that itself contains a colon
    (adversarial: if FIELD somehow matched past the id, this colon later
    in the line would be the next thing it could latch onto)."""

    def test_indented_citation_fit_continuation_is_not_parsed_as_a_field(self):
        text = (
            "citations: DTS-0001, ZPZQ-0001\n"
            "citation_fit:\n"
            "  DTS-0001 — 例如：月令与藏干需要匹配\n"
            "  ZPZQ-0001 — 日干与月令地支均已确认\n"
            "rival_resolution: ZPZQ-0001 over DTS-0001 — 本任务以定格为目标\n"
        )
        answer = parse_answer(text)
        # If the first continuation line had been mis-parsed as a field,
        # `current` would no longer be "citation_fit" by the time the
        # second continuation line is reached, and ZPZQ-0001 would be
        # silently dropped from citation_fit_ids.
        self.assertEqual(answer["citation_fit_ids"], ["DTS-0001", "ZPZQ-0001"])
        self.assertEqual(check_answer(answer, LIBRARY), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest tests.test_checks_answer -v`
Expected: FAIL —— `ModuleNotFoundError: No module named 'classics.checks_answer'`

- [ ] **Step 3: 写最小实现**

创建 `scripts/classics/checks_answer.py`：

```python
"""Mode B: verify how an answer uses classics citations (spec 9.1).

Input is the `key: value` text block that school masters and the referee
already emit, or a report containing a 依据索引 section.

「孤证不立」is deliberately NOT checked here: classifying a claim as
event-level is not reliably possible from free text, and a check that
silently misses cases is worse than no check. It stays a referee prompt
rule (spec 8.2 item 4).
"""

from __future__ import annotations

import re

from .cards import Card

_CARD_ID_CORE = r"[A-Z]{3,4}-\d{4}"
# Lookaround instead of \b: \b does not fire between a CJK character and an
# ASCII letter/digit (both count as \w), so unspaced Chinese prose like
# "依DTS-0001定格" would otherwise hide the id entirely.
CARD_ID = re.compile(rf"(?<![A-Za-z0-9])({_CARD_ID_CORE})(?![A-Za-z0-9-])")
# A continuation line of a citation_fit/rival_resolution block: indented,
# and starting with a card id (not merely containing one somewhere).
CONTINUATION = re.compile(rf"^\s+({_CARD_ID_CORE})(?![A-Za-z0-9-])")
FIELD = re.compile(r"^\s*([A-Za-z_]+)\s*[:：]\s*(.*)$")
# A bare heading line: "依据索引" alone, or a markdown ATX heading of it,
# with an optional trailing comment (the brief's own canonical example is
# "依据索引                                # 报告型输入的判别标记" — a line
# ending immediately after the heading text would miss that literal form).
# Anchoring to the whole line (rather than a substring search) means a
# table of contents entry or a closing sentence that merely mentions the
# heading text does not get mistaken for the section boundary.
INDEX_HEADING = re.compile(r"^\s*(?:#{1,6}\s*)?依据索引\s*(?:#.*)?$")
NO_BASIS = "no_classical_basis"
# Lookaround instead of \b, for the same reason CARD_ID uses it: \b does
# not fire between a CJK character and an ASCII letter/digit, so
# "无引用no_classical_basis" (no space before the token) would otherwise
# never match.
NO_BASIS_TOKEN = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(NO_BASIS)}(?![A-Za-z0-9_])")


def parse_answer(text: str) -> dict[str, object]:
    """Extract the citation-relevant shape of an answer or report."""
    lines = text.splitlines()
    fields: dict[str, str] = {}
    citations_field_count = 0
    fit_ids: list[str] = []
    rival_resolutions: list[str] = []
    current: str | None = None
    index_start: int | None = None

    for offset, raw in enumerate(lines):
        if INDEX_HEADING.match(raw):
            # Last occurrence wins: an earlier heading-shaped line (e.g. a
            # template block quoted for illustration) should not anchor the
            # window ahead of the real, final section.
            index_start = offset

        if not raw.strip():
            # A blank line always ends a citation_fit/rival_resolution
            # continuation block; without this, every non-blank line to
            # end-of-document keeps getting scanned for card ids under
            # whichever field was last seen (including 依据索引 table
            # rows, which would then auto-satisfy citation_fit/rival
            # checks on every report by construction).
            current = None
            continue

        field = FIELD.match(raw)
        if field:
            # Lowercasing here (rather than restricting to a closed
            # vocabulary) is the whole fix: it makes `Pattern_call:` and
            # `  pattern_call:` normalise to the same key as `pattern_call:`
            # so rule 4's tier gate still runs. A field the module doesn't
            # otherwise care about (e.g. `confidence:`, `scope:` — real
            # fields the school-prompt Output Shapes already emit) is
            # simply stored and ignored, exactly as before this fix round;
            # there is no vocabulary to be missing from.
            key = field.group(1).lower()
            value = field.group(2).strip()
            current = key
            if key == "citations":
                citations_field_count += 1
                fields[key] = value
            elif key == "citation_fit":
                fields[key] = value
                if value:
                    fit_ids.extend(CARD_ID.findall(value))
            elif key == "rival_resolution":
                if value:
                    rival_resolutions.append(value)
            else:
                fields[key] = value
            continue

        continuation = CONTINUATION.match(raw)
        if not continuation:
            continue
        if current == "citation_fit":
            fit_ids.extend(CARD_ID.findall(raw))
        elif current == "rival_resolution":
            rival_resolutions.append(raw.strip())

    raw_citations = fields.get("citations")
    no_basis = raw_citations is not None and raw_citations.strip() == NO_BASIS
    citations = [] if no_basis else CARD_ID.findall(raw_citations or "")
    mixed_basis = bool(citations) and bool(
        NO_BASIS_TOKEN.search(raw_citations or "")
    )

    body_ids: list[str] = []
    index_ids: list[str] = []
    if index_start is not None:
        body_ids = CARD_ID.findall("\n".join(lines[:index_start]))
        index_ids = CARD_ID.findall("\n".join(lines[index_start:]))

    return {
        "has_citations_field": raw_citations is not None,
        "no_classical_basis": no_basis,
        "mixed_no_classical_basis": mixed_basis,
        "citations": citations,
        "citation_fit_ids": fit_ids,
        "pattern_call": fields.get("pattern_call", ""),
        "rival_resolutions": rival_resolutions,
        "is_report": index_start is not None,
        "body_ids": body_ids,
        "index_ids": index_ids,
        "duplicate_citations_field": citations_field_count > 1,
    }


def check_answer(answer: dict[str, object], cards: list[Card]) -> list[str]:
    """Run every mode-B rule. Empty list means citation use is valid."""
    errors: list[str] = []
    by_id = {card.id: card for card in cards}
    citations: list[str] = answer["citations"]

    if answer["duplicate_citations_field"]:
        errors.append(
            "`citations` 字段出现多次，请为每份分析分别校验"
            "（不支持单份输入中出现多个 citations 块）"
        )

    if answer["mixed_no_classical_basis"]:
        errors.append(f"`citations` 中同时出现引用 ID 与 {NO_BASIS}，请二选一")

    if not answer["has_citations_field"]:
        errors.append(f"缺少 `citations` 字段（无可引时应写 {NO_BASIS}）")
    elif not citations and not answer["no_classical_basis"]:
        errors.append(f"`citations` 为空；无可引时应显式写 {NO_BASIS}")

    for card_id in citations:
        if card_id not in by_id:
            errors.append(f"引用了不存在的卡片 {card_id}")
        if card_id not in answer["citation_fit_ids"]:
            errors.append(f"{card_id} 缺少对应的 citation_fit 说明")

    if answer["pattern_call"] == "formal_pattern":
        strong = {"核心论断", "操作规则"}
        if not any(
            by_id[c].tier in strong for c in citations if c in by_id
        ):
            errors.append(
                "pattern_call 为 formal_pattern 但无「核心论断」或「操作规则」"
                "层级的卡片支撑，应降级为 pattern_tendency"
            )

    cited = set(citations)
    resolved = "\n".join(answer["rival_resolutions"])
    for card_id in sorted(cited):
        card = by_id.get(card_id)
        if card is None:
            continue
        for rival in card.rivals:
            if rival.card_id not in cited or rival.card_id < card_id:
                continue
            if not (card_id in resolved and rival.card_id in resolved):
                errors.append(
                    f"{card_id} 与 {rival.card_id} 互为竞合，"
                    f"必须给出同时点到两者的 rival_resolution"
                )

    if answer["is_report"]:
        indexed = set(answer["index_ids"])
        for card_id in sorted(set(answer["body_ids"])):
            if card_id not in indexed:
                errors.append(f"正文引用的 {card_id} 未出现在「依据索引」章节")
        for card_id in sorted(indexed):
            if card_id not in by_id:
                errors.append(f"「依据索引」列出了不存在的卡片 {card_id}")

    return errors
```

修改 `scripts/validate_citations.py` —— 追加 import、追加 `run_answer_mode`、改写 `main`：

```python
from classics.checks_answer import check_answer, parse_answer
```

```python
def run_answer_mode(answer_path: str, classics_root: Path) -> int:
    cards_dir = classics_root / "cards"
    if not cards_dir.is_dir():
        print(f"缺少卡片目录: {cards_dir}", file=sys.stderr)
        return 2

    try:
        cards, parse_errors = load_cards(cards_dir)
    except Exception as exc:  # noqa: BLE001
        print(f"无法读取卡片文件: {exc}", file=sys.stderr)
        return 2

    if parse_errors:
        print("卡片库本身无效，先修复后再校验答案：", file=sys.stderr)
        for error in parse_errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    if answer_path == "-":
        try:
            text = sys.stdin.read()
        except Exception as exc:  # noqa: BLE001
            print(f"无法读取标准输入: {exc}", file=sys.stderr)
            return 2
    else:
        path = Path(answer_path)
        if not path.is_file():
            print(f"找不到答案文件: {path}", file=sys.stderr)
            return 2
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            print(f"无法读取答案文件: {exc}", file=sys.stderr)
            return 2

    return report(check_answer(parse_answer(text), cards))
```

Guarded per Task 5's precedent (`run_cards_mode` already wraps `load_cards`):
calling `load_cards()`, `path.read_text()`, or `sys.stdin.read()` without
exception handling lets a decoding/permission error raise uncaught,
producing a raw traceback and Python's default exit code 1 —
indistinguishable from a legitimate `INVALID` result. All three read
points here get the same try/except → stderr → `return 2` treatment,
keeping the 0/1/2 exit-code contract intact. Covered by
`tests/test_cli_cards.py::CliAnswerTest::test_unreadable_answer_file_exits_two`
and `::test_unreadable_stdin_exits_two` (the stdin test forces
`LANG=en_US.UTF-8`/`LC_ALL=en_US.UTF-8` on the subprocess — under an
unset/POSIX locale Python decodes stdin with surrogateescape and invalid
bytes pass through silently with no exception at all, which would make
the test pass whether or not the guard exists).

```python
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--cards",
        metavar="CLASSICS_ROOT",
        help="Card library self-check. Directory containing cards/ and corpus/",
    )
    mode.add_argument(
        "--answer",
        metavar="FILE",
        help="Answer or report to check, or '-' for stdin",
    )
    parser.add_argument(
        "--classics-root",
        default="references/classics",
        help="Card library root used by --answer (default: references/classics)",
    )
    parser.add_argument("--count", action="store_true", help="Print parsed card count")
    args = parser.parse_args()

    if args.cards is not None:
        return run_cards_mode(Path(args.cards), args.count)
    return run_answer_mode(args.answer, Path(args.classics_root))
```

`if args.cards:` dispatches on truthiness, so `--cards ""` (e.g. from a CI
script passing `--cards "$ROOT"` with `ROOT` unset) falls through to answer
mode with `args.answer` still `None`, crashing `Path(None)` with a raw
`TypeError` and exit 1 — exactly the contract violation the guards above
exist to prevent. `if args.cards is not None:` dispatches on presence
instead, so an empty value still reaches `run_cards_mode`'s own
missing-directory guard and exits 2 cleanly. Covered by
`tests/test_cli_cards.py::CliCardsTest::test_empty_cards_value_exits_two`.

### Post-review hardening of `checks_answer.py`'s parser (2026-08-25)

A whole-branch review of Task 6 found the `parse_answer` state machine
above returns `VALID` over answers it never actually inspected, most
sharply for report-type input (Task 11's primary consumer): a report's
依据索引 table lists every cited id by construction, so an unbounded
continuation-scanning bug let that table silently satisfy both the
citation_fit rule and the rival_resolution rule on every report. Nine
fixes landed together (three Critical, five Important, one Minor folded
into Critical #1's rewrite because the fix touched the same lines):

1. **Continuation never terminates** — a blank line now resets the
   `current` field-context, and citation_fit/rival_resolution
   continuation lines must be indented *and* start with the card id
   (`^\s+([A-Z]{3,4}-\d{4})`), not merely mention one anywhere later in
   the document.
2. **Field keys were case- and indentation-sensitive** — `Pattern_call:`
   (capitalised) and `  pattern_call:` (indented) used to fail to match
   at all, silently skipping the formal_pattern tier gate. Field keys are
   now matched case-insensitively after optional leading whitespace.
   (This item's original fix also rejected any field-shaped line whose
   key wasn't in a closed vocabulary as an error — that broke every real
   master output and was itself corrected in round 2 below; the fix that
   stands is the case/indentation normalisation only.)
3. **`no_classical_basis` matched as a substring** — `citations:
   DTS-9999, no_classical_basis` (or the spec's own hint-comment example,
   `# 或 no_classical_basis`, left on the line by mistake) used to
   disable rules 1/3/5 wholesale. `no_classical_basis` now must be the
   *entire* stripped value; the token appearing alongside real ids is
   itself now a reported error.
4. **`sys.stdin.read()` was unguarded** — the same treatment as
   `load_cards()`/`path.read_text()` above; see the `run_answer_mode`
   rationale note.
5. **`\b` does not fire between CJK and ASCII** — `re.findall(r"\b...\b",
   "依DTS-0001定")` returns nothing, since Python's `re` treats CJK as
   `\w`. `CARD_ID` now uses lookaround
   (`(?<![A-Za-z0-9])...(?![A-Za-z0-9-])`) instead of `\b`, so ids in
   unspaced Chinese prose are still found.
6. **依据索引 anchor matched anywhere in a line** — a table-of-contents
   entry or a closing sentence mentioning the heading text used to
   collapse or displace the report body/index window. `INDEX_HEADING`
   now only matches a heading-shaped line
   (`^\s*(?:#{1,6}\s*)?依据索引\s*$`), and the *last* such line wins
   over an earlier one (e.g. a template block quoted for illustration).
7. **Repeated `citations:` key silently overwrote** — a two-block
   aggregated document (e.g. Task 10's referee combining several school
   outputs) whose first block cited a nonexistent id used to return
   `VALID`, since only the last block's value was ever read. A duplicate
   `citations:` key is now a reported error.
8. **`--cards ""` crashed instead of exiting 2** — see the `main()`
   rationale note above.
9. **Inline `citation_fit: DTS-0001 — 理由` was not counted** — the
   natural single-line form; fixed as part of #1's rewrite of the
   continuation logic.

All nine are covered by dedicated tests in `tests/test_checks_answer.py`
(`ContinuationTerminationTest`, `FieldRecognitionTest`,
`NoClassicalBasisTest`, `UnspacedCjkCardIdTest`, `ReportWindowAnchorTest`,
`DuplicateCitationsFieldTest`, `InlineCitationFitTest`) and
`tests/test_cli_cards.py` (`test_unreadable_stdin_exits_two`,
`test_empty_cards_value_exits_two`) — 12 + 2 = 14 new tests, each
independently confirmed to fail against the pre-fix code before the fix
landed.

#### Round 2 correction (2026-08-25): item #2's fix instruction was wrong

Item #2's `KNOWN_FIELDS` closed vocabulary (`school`, `citations`,
`citation_fit`, `pattern_call`, `rival_resolution`) rejected any other
field-shaped line as `无法识别的字段`. Running a realistic
`ziping-pattern-master` output through the CLI — every field the current
`references/school-prompts/*.md` Output Shape blocks already require
(`scope`, `core_thesis`, `supporting_evidence`, `counter_evidence`,
`warnings`, `confidence`, `recommended_wording`, plus the five known
ones) — returned `INVALID` with seven `无法识别的字段` errors. As shipped,
mode B rejected every real master output; this was a defect in the
review's own fix instruction, not in how Task 6 executed it.

The actual defect item #2 was chasing is narrower than a vocabulary: a
*known* field written with the wrong case or with leading indentation
was silently dropped, so its rule never ran. Lowercasing the matched key
after `lstrip()` fixes exactly that and needs no vocabulary — `Pattern_call:`
normalises to `pattern_call` and rule 4 runs; `Confidence:` normalises to
`confidence`, gets stored, and is ignored harmlessly, exactly as an
unindented lowercase field the module doesn't otherwise care about
always was. `KNOWN_FIELDS`, the `unknown_fields` tracking, and the
`无法识别的字段` error were deleted entirely.

Accepted residual risk, deliberately not solved: a genuinely misspelled
`pattern_cal:` is still stored under the wrong key and rule 4 silently
does not run for it. No closed vocabulary can distinguish a typo from a
legitimately new field without also breaking every new field, and
breaking all valid input is far worse than missing a typo — the same
"a check that silently misses cases is worse than no check" reasoning
that keeps 孤证不立 out of this module (see the module docstring). A
fuzzy-match/edit-distance heuristic was considered and rejected for the
same reason.

Added `RealisticMasterOutputShapeTest` (the full example above, asserting
`check_answer` returns `[]` — the test whose absence let this ship),
`FieldRecognitionTest::test_unrelated_field_is_stored_and_ignored_not_reported_as_an_error`,
and `ContinuationLineIsNotAFieldTest` (an indented citation_fit
continuation line, including one whose reason text itself contains a
colon, must not be parsed as a field — verified explicitly since the
interaction between round 1's continuation-termination fix and round 2's
key-normalisation fix is exactly the kind of thing worth checking rather
than reasoning about). Removed
`FieldRecognitionTest::test_unrecognised_field_key_is_reported`, which
asserted the now-deleted behaviour. Net: −1 test, +3 tests = +2 over the
70 above.

#### Round 3 correction (2026-08-25): two properties introduced by the round-1/2 fixes themselves went unhardened

A re-review of rounds 1+2 confirmed all nine original findings and the
round-2 correction hold, and surfaced two new issues in the fixes
themselves:

1. **`INDEX_HEADING` too strict, reopening the false-VALID path (Important).**
   The round-1 fix required the heading line to end immediately after
   `依据索引`. But the brief's own canonical marker line
   (`task-6-brief.md:24`) is
   `依据索引                                # 报告型输入的判别标记` — a
   trailing comment explaining the marker. An input written exactly as
   the brief's documentation shows was not detected as a report at all,
   silently skipping rule 6 entirely — the same false-VALID class
   Important #6 existed to close, reopened through a formatting path.
   Worth noting: Critical #3's fix already treated "the user pastes the
   template's `# 或 no_classical_basis` comment verbatim" as a realistic
   input and tested for it; the identical risk on the heading marker was
   left unhardened. Fixed by allowing an optional trailing comment:
   `INDEX_HEADING = re.compile(r"^\s*(?:#{1,6}\s*)?依据索引\s*(?:#.*)?$")`.
   Verified all of: bare `依据索引` matches; `## 依据索引` matches; the
   brief's exact trailing-comment line now matches; a prose
   cross-reference (`完整出处详见依据索引。`) still does not match; a TOC
   entry (`1. 依据索引`) still does not match; last-match-wins still
   holds with two headings present.
2. **`NO_BASIS_TOKEN` still used `\b` (Minor, folded in deliberately).**
   `\b` is the exact construct Important #5 established as unreliable at
   a CJK/ASCII boundary in this codebase; `NO_BASIS_TOKEN.search("无引用no_classical_basis")`
   returned no match. Impact is small — only the supplementary 二选一
   diagnostic is lost, the cited ids are still validated normally either
   way — but the file carried both idioms two lines apart, inviting the
   same bug back the next time someone copies the nearby pattern. Fixed
   with the same lookaround shape as `CARD_ID`:
   `NO_BASIS_TOKEN = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(NO_BASIS)}(?![A-Za-z0-9_])")`.

Added `ReportWindowAnchorTest::test_trailing_comment_after_heading_marker_is_detected`
and `NoClassicalBasisTest::test_no_classical_basis_glued_to_cjk_text_is_still_detected_as_mixed`,
both confirmed to fail against the round-2 code before their fixes
landed. Net: +2 tests over the 72 above.

- [ ] **Step 4: 运行测试确认通过**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest discover -s tests -t . -v`
Expected: PASS，74 tests（42 基线 + 13 个 Step 1 的 `test_checks_answer.py`
+ 1 个 `CliAnswerTest::test_unreadable_answer_file_exits_two` + 12 个
round 1 post-review 新增的 `test_checks_answer.py` 用例 + 2 个 round 1
post-review 新增的 `test_cli_cards.py` 用例 − 1 个 round 2 移除的用例 + 3 个
round 2 新增的用例 + 2 个 round 3 新增的用例）

端到端手工验证：

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
printf 'citations: DTS-0001\ncitation_fit:\n  DTS-0001 — 月令与藏干齐备\npattern_call: formal_pattern\n' \
  | python3 scripts/validate_citations.py --answer - --classics-root tests/fixtures; echo "exit=$?"
printf 'citations: DTS-0001, ZPZQ-0001\ncitation_fit:\n  DTS-0001 — x\n  ZPZQ-0001 — y\n' \
  | python3 scripts/validate_citations.py --answer - --classics-root tests/fixtures; echo "exit=$?"
```

Expected: 第一条 `VALID` + `exit=0`；第二条 `INVALID` + 含 `rival_resolution` + `exit=1`

- [ ] **Step 5: 提交**

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
git add scripts/classics/checks_answer.py scripts/validate_citations.py tests/test_checks_answer.py
git commit -m "feat(classics): add mode B answer citation checks"
```

---

### Task 7: 零依赖检索 `search_classics.py`

**Files:**
- Create: `scripts/classics/search.py`
- Create: `scripts/search_classics.py`
- Test: `tests/test_search.py`

**Interfaces:**
- Consumes: `classics.normalize.normalize`、`classics.cards.Card`、`classics.corpus.read_lines`
- Produces:
  - `classics.search.bigrams(text: str) -> list[str]`
  - `classics.search.score(query_grams: list[str], doc: str) -> float`
  - `classics.search.search_cards(cards, query, topic=None, school=None, limit=10) -> list[tuple[float, Card]]`
  - `classics.search.search_corpus(classics_root, query, limit=10, window=1) -> list[tuple[float, str, int, str]]`
  - CLI: `python3 scripts/search_classics.py <query> [--classics-root DIR] [--topic T] [--school S] [--corpus] [--limit N]`

评分：查询 2-gram 在文档中的词频之和，除以 `sqrt(文档长度)` 以抑制长文档偏置。
`topic` 匹配卡片来源文件名，`school` 匹配 `card.schools`。

- [ ] **Step 1: 写失败的测试**

创建 `tests/test_search.py`：

```python
import subprocess
import sys
import unittest
from pathlib import Path

from classics.cards import load_cards
from classics.search import bigrams, score, search_cards, search_corpus

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests" / "fixtures"
CLI = REPO / "scripts" / "search_classics.py"


class BigramTest(unittest.TestCase):
    def test_bigrams_of_normalised_text(self):
        self.assertEqual(bigrams("衰旺真机"), ["衰旺", "旺真", "真机"])

    def test_punctuation_is_normalised_away_before_splitting(self):
        self.assertEqual(bigrams("衰旺，真机"), ["衰旺", "旺真", "真机"])

    def test_single_character_query_yields_no_bigram(self):
        self.assertEqual(bigrams("木"), [])

    def test_score_is_zero_when_nothing_matches(self):
        self.assertEqual(score(bigrams("紫微"), "能知衰旺之真机"), 0.0)

    def test_score_is_positive_on_overlap(self):
        self.assertGreater(score(bigrams("衰旺"), "能知衰旺之真机"), 0.0)


class SearchCardsTest(unittest.TestCase):
    def setUp(self):
        self.cards, errors = load_cards(FIXTURES / "cards")
        self.assertEqual(errors, [])

    def test_finds_the_wangshuai_card(self):
        hits = search_cards(self.cards, "衰旺真机")
        self.assertTrue(hits)
        self.assertEqual(hits[0][1].id, "DTS-0001")

    def test_school_filter_excludes_others(self):
        hits = search_cards(self.cards, "余寒", school="调候")
        self.assertTrue(hits)
        self.assertTrue(all(h[1].schools == ("调候",) for h in hits))

    def test_topic_filter_matches_source_filename(self):
        hits = search_cards(self.cards, "月令", topic="30-tiaohou")
        self.assertTrue(all("30-tiaohou" in h[1].source_file for h in hits))

    def test_limit_is_honoured(self):
        self.assertLessEqual(len(search_cards(self.cards, "月令", limit=2)), 2)

    def test_no_match_returns_empty(self):
        self.assertEqual(search_cards(self.cards, "紫微斗数飞星"), [])


class SearchCorpusTest(unittest.TestCase):
    def test_locates_line_in_corpus(self):
        hits = search_corpus(FIXTURES, "余寒犹存")
        self.assertTrue(hits)
        _, rel, line, _ = hits[0]
        self.assertEqual(rel, "corpus/qiongtong-baojian.txt")
        self.assertEqual(line, 3)


class SearchCliTest(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            capture_output=True,
            text=True,
            cwd=str(REPO),
        )

    def test_card_search_prints_id(self):
        result = self._run("衰旺真机", "--classics-root", str(FIXTURES))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DTS-0001", result.stdout)

    def test_corpus_search_prints_location(self):
        result = self._run("余寒犹存", "--classics-root", str(FIXTURES), "--corpus")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("qiongtong-baojian.txt", result.stdout)
        self.assertIn("#L3", result.stdout)

    def test_no_hit_exits_one(self):
        result = self._run("紫微斗数飞星", "--classics-root", str(FIXTURES))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest tests.test_search -v`
Expected: FAIL —— `ModuleNotFoundError: No module named 'classics.search'`

- [ ] **Step 3: 写最小实现**

创建 `scripts/classics/search.py`：

```python
"""Zero-dependency Chinese retrieval over cards and corpus.

2-gram split plus term-frequency weighting, normalised by sqrt(doc length)
to keep long corpus lines from dominating. No jieba, no embeddings — the
skill has no runtime and must stay standard-library only.
"""

from __future__ import annotations

import math
from pathlib import Path

from .cards import Card
from .corpus import read_lines
from .normalize import normalize


def bigrams(text: str) -> list[str]:
    """Overlapping 2-grams of the normalised text."""
    cleaned = normalize(text)
    return [cleaned[i : i + 2] for i in range(len(cleaned) - 1)]


def score(query_grams: list[str], doc: str) -> float:
    """Sum of query-gram frequencies in `doc`, damped by document length."""
    if not query_grams:
        return 0.0
    cleaned = normalize(doc)
    if not cleaned:
        return 0.0
    total = sum(cleaned.count(gram) for gram in query_grams)
    if total == 0:
        return 0.0
    return total / math.sqrt(len(cleaned))


def _card_haystack(card: Card) -> str:
    return " ".join(
        (card.quote, card.plain, card.classic, card.boundary, *card.premises)
    )


def search_cards(
    cards: list[Card],
    query: str,
    topic: str | None = None,
    school: str | None = None,
    limit: int = 10,
) -> list[tuple[float, Card]]:
    """Rank cards by relevance to `query`, optionally filtered."""
    grams = bigrams(query)
    hits: list[tuple[float, Card]] = []
    for card in cards:
        if topic and topic not in card.source_file:
            continue
        if school and school not in card.schools:
            continue
        value = score(grams, _card_haystack(card))
        if value > 0:
            hits.append((value, card))
    hits.sort(key=lambda item: (-item[0], item[1].id))
    return hits[:limit]


def search_corpus(
    classics_root: Path,
    query: str,
    limit: int = 10,
    window: int = 1,
) -> list[tuple[float, str, int, str]]:
    """Rank corpus lines. Returns (score, relative path, line number, context)."""
    grams = bigrams(query)
    corpus_dir = classics_root / "corpus"
    if not corpus_dir.is_dir():
        return []

    hits: list[tuple[float, str, int, str]] = []
    for path in sorted(corpus_dir.glob("*.txt")):
        lines = read_lines(path)
        rel = f"corpus/{path.name}"
        for index, line in enumerate(lines, start=1):
            value = score(grams, line)
            if value <= 0:
                continue
            low = max(0, index - 1 - window)
            high = min(len(lines), index + window)
            hits.append((value, rel, index, " / ".join(lines[low:high])))
    hits.sort(key=lambda item: (-item[0], item[1], item[2]))
    return hits[:limit]
```

创建 `scripts/search_classics.py`：

```python
#!/usr/bin/env python3
"""Search the classics card library, or fall back to raw corpus lines."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from classics.cards import load_cards
from classics.search import search_cards, search_corpus


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Search text")
    parser.add_argument(
        "--classics-root",
        default="references/classics",
        help="Directory containing cards/ and corpus/ (default: references/classics)",
    )
    parser.add_argument("--topic", help="Restrict to a cards/*.md filename fragment")
    parser.add_argument("--school", help="Restrict to one school name")
    parser.add_argument(
        "--corpus", action="store_true", help="Search raw corpus lines instead of cards"
    )
    parser.add_argument("--limit", type=int, default=10, help="Max hits (default: 10)")
    args = parser.parse_args()

    root = Path(args.classics_root)

    if args.corpus:
        hits = search_corpus(root, args.query, limit=args.limit)
        if not hits:
            print("no hits")
            return 1
        for value, rel, line, context in hits:
            print(f"{value:.4f}  {rel}#L{line}  {context}")
        return 0

    cards_dir = root / "cards"
    if not cards_dir.is_dir():
        print(f"缺少卡片目录: {cards_dir}", file=sys.stderr)
        return 2

    cards, errors = load_cards(cards_dir)
    if errors:
        print("卡片库无效，先运行 validate_citations.py --cards", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    hits = search_cards(
        cards, args.query, topic=args.topic, school=args.school, limit=args.limit
    )
    if not hits:
        print("no hits")
        return 1
    for value, card in hits:
        print(f"{value:.4f}  {card.id}  [{card.tier}]  {card.classic}")
        print(f"          {card.plain}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest discover -s tests -t . -v`
Expected: PASS，64 tests

- [ ] **Step 5: 提交**

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
git add scripts/classics/search.py scripts/search_classics.py tests/test_search.py
git commit -m "feat(classics): add zero-dependency card and corpus search"
```

---

### Task 8: `references/classics/index.md` 与七个主题文件

**Files:**
- Create: `references/classics/index.md`
- Create: `references/classics/cards/10-yueling.md`
- Create: `references/classics/cards/20-wangshuai.md`
- Create: `references/classics/cards/30-tiaohou.md`
- Create: `references/classics/cards/40-shishen.md`
- Create: `references/classics/cards/50-geju.md`
- Create: `references/classics/cards/60-shensha.md`
- Create: `references/classics/cards/70-yunsui.md`
- Create: `references/classics/corpus/.gitkeep`
- Test: `tests/test_index_contract.py`

**Interfaces:**
- Consumes: `classics.cards.load_cards`（用于验证空主题文件可被解析）
- Produces: `references/classics/index.md` 作为 master 与裁判的唯一入口文档

本期主题文件**只写表头与说明，不含卡片**（偏离记录 D）。
真实卡片随 Spec Phase 3 按主题落地。

- [ ] **Step 1: 写失败的测试**

创建 `tests/test_index_contract.py`：

```python
import unittest
from pathlib import Path

from classics import CARD_TIERS, ENABLED_PREFIXES, SCHOOLS
from classics.cards import load_cards

REPO = Path(__file__).resolve().parents[1]
CLASSICS = REPO / "references" / "classics"
INDEX = CLASSICS / "index.md"

TOPICS = (
    "10-yueling",
    "20-wangshuai",
    "30-tiaohou",
    "40-shishen",
    "50-geju",
    "60-shensha",
    "70-yunsui",
)


class IndexContractTest(unittest.TestCase):
    def test_index_exists(self):
        self.assertTrue(INDEX.is_file(), f"missing {INDEX}")

    def test_all_topic_files_exist(self):
        for topic in TOPICS:
            path = CLASSICS / "cards" / f"{topic}.md"
            self.assertTrue(path.is_file(), f"missing {path}")

    def test_index_has_three_routing_tables(self):
        text = INDEX.read_text(encoding="utf-8")
        for heading in ("主题 → 卡片文件", "流派 → 主题", "典籍 → 主题"):
            self.assertIn(heading, text, f"index.md missing routing table: {heading}")

    def test_index_documents_every_tier(self):
        text = INDEX.read_text(encoding="utf-8")
        for tier in CARD_TIERS:
            self.assertIn(tier, text, f"index.md missing tier: {tier}")

    def test_index_documents_every_enabled_prefix(self):
        text = INDEX.read_text(encoding="utf-8")
        for prefix in ENABLED_PREFIXES:
            self.assertIn(prefix, text, f"index.md missing prefix: {prefix}")

    def test_index_documents_no_classical_basis(self):
        self.assertIn("no_classical_basis", INDEX.read_text(encoding="utf-8"))

    def test_index_routes_every_school(self):
        text = INDEX.read_text(encoding="utf-8")
        for school in SCHOOLS:
            self.assertIn(school, text, f"index.md missing school: {school}")

    def test_empty_topic_files_parse_cleanly(self):
        cards, errors = load_cards(CLASSICS / "cards")
        self.assertEqual(errors, [])
        self.assertEqual(cards, [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest tests.test_index_contract -v`
Expected: FAIL —— `missing .../references/classics/index.md`

- [ ] **Step 3: 写文档**

创建 `references/classics/index.md`：

````markdown
# 古籍知识层索引

本目录是八字典籍条文的唯一入口。读取顺序：先读本文件路由，再只读需要的
`cards/NN-*.md`；`corpus/` 是证据底库，**不作为阅读材料**，仅在裁判核对引文或
master 报 `evidence_gap` 需深挖时，经 `scripts/search_classics.py` 定位。

## 源政策

- 排盘事实以代码计算为准。典籍条文只用于解释、比较、排序与措辞。
- 引用必须带卡片 ID，且能通过 `scripts/validate_citations.py` 核对。
  无卡片支撑的书名提及一律删除。
- 确无可引条文时，写 `no_classical_basis`。这与给出真实引用同等合法，
  不构成缺陷 —— 必填 `citations` 的目的是逼出「有没有依据」这个显式回答，
  不是逼出引用。

## 主题 → 卡片文件

| 主题 | 文件 | 覆盖内容 |
|---|---|---|
| 月令 | `cards/10-yueling.md` | 月令司令、得时失时 |
| 旺衰 | `cards/20-wangshuai.md` | 旺衰强弱、扶抑 |
| 调候 | `cards/30-tiaohou.md` | 调候、寒暖燥湿 |
| 十神 | `cards/40-shishen.md` | 十神性情与作用 |
| 格局 | `cards/50-geju.md` | 格局成败救应 |
| 神煞 | `cards/60-shensha.md` | 神煞 |
| 运岁 | `cards/70-yunsui.md` | 大运流年 |

## 流派 → 主题

| 流派 | 应读主题 | 本期典籍支撑 |
|---|---|---|
| 子平格局 | 格局, 月令, 十神 | 子平真诠 |
| 旺衰扶抑 | 旺衰, 月令 | 滴天髓 |
| 调候 | 调候, 月令 | 穷通宝鉴 |
| 神煞辅助 | 神煞 | 三命通会 |
| 盲派象法 | 十神, 运岁 | 无 —— 一律 `no_classical_basis` |
| 紫微 | 无 | 无 —— 二期（紫微斗数全书） |
| 择日择时 | 无 | 无 —— 二期（协纪辨方书） |
| 合盘 | 十神, 运岁 | 无 —— 无专书 |

## 典籍 → 主题

| 前缀 | 典籍 | 主要主题 | 语料 |
|---|---|---|---|
| `DTS` | 滴天髓 | 旺衰, 月令 | `corpus/ditiansui.txt` |
| `ZPZQ` | 子平真诠 | 格局, 月令, 十神 | `corpus/ziping-zhenquan.txt` |
| `QTBJ` | 穷通宝鉴 | 调候 | `corpus/qiongtong-baojian.txt` |
| `SMTH` | 三命通会 | 神煞, 十神, 运岁 | `corpus/sanming-tonghui.selected.txt` |

二期保留前缀，**本期使用即报错**：`YHZP` 渊海子平、`SFTK` 神峰通考、
`ZWDS` 紫微斗数全书、`XJFF` 协纪辨方书。
启用条件：其语料已入库并在 `corpus/PROVENANCE.md` 登记。

## 层级与权重

| 层级 | 含义 | 裁判用法 |
|---|---|---|
| `核心论断` | 提纲挈领的原则性主张 | 可单独支撑结构性判断；源层级高于方法适配 |
| `操作规则` | 可直接套用的判定规则或取用口径 | 可单独支撑结构性判断 |
| `例证` | 具体命例或举例说明 | **不可单独支撑结构性判断**；源层级低于方法适配 |
| `存疑` | 版本歧异、语义不明或流派争议未决 | 仅作「另有一说」提示，不得作结论依据 |

## 卡片契约

```markdown
### <前缀>-<四位序号>
- 典籍: 书名·篇·节
- 原文: 必须是所声明语料文件的精确子串（正规化后）
- 白话: 自行撰写，禁止摘抄现代整理本译文
- 适用前提:
  - 触发该条所需的盘面事实（裁判据此判定引用是否成立）
- 层级: 核心论断 | 操作规则 | 例证 | 存疑
- 流派: 逗号分隔，取值见「流派 → 主题」表
- 竞合:
  - <对立卡片ID> — 差异说明（必须双向，对方也要回指本卡）
- 反例边界: 该条不适用的情形。必填
- corpus: corpus/<file>#L<起>-L<止>
```

`反例边界` 必填是刻意的：命理误判绝大多数来自把有条件的规则当无条件用。
确实找不到边界时，写「未见明确边界，按存疑级处理」并把 `层级` 降为 `存疑`。

## 常用命令

```bash
python3 scripts/validate_citations.py --cards references/classics
python3 scripts/search_classics.py "衰旺真机" --school 旺衰扶抑
python3 scripts/search_classics.py "余寒犹存" --corpus
```
````

七个主题文件各写表头。以 `references/classics/cards/20-wangshuai.md` 为例：

```markdown
# 旺衰

旺衰强弱与扶抑。卡片契约见 `../index.md`。

本期尚无卡片 —— 卡片编纂随语料入库推进（见 Spec Phase 2、Phase 3）。
```

其余六个同构，仅替换标题与一句覆盖说明：

- `10-yueling.md` —— `# 月令`，「月令司令、得时失时。」
- `30-tiaohou.md` —— `# 调候`，「调候与寒暖燥湿。」
- `40-shishen.md` —— `# 十神`，「十神性情与作用。」
- `50-geju.md` —— `# 格局`，「格局成败救应。」
- `60-shensha.md` —— `# 神煞`，「神煞。」
- `70-yunsui.md` —— `# 运岁`，「大运流年。」

创建空的 `references/classics/corpus/.gitkeep`（语料随 Phase 2 入库）：

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
mkdir -p references/classics/corpus && touch references/classics/corpus/.gitkeep
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest discover -s tests -t . -v`
Expected: PASS，72 tests

再确认空卡片库对 CLI 是有效状态：

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
python3 scripts/validate_citations.py --cards references/classics --count; echo "exit=$?"
```

Expected: `cards: 0` + `VALID` + `exit=0`

- [ ] **Step 5: 提交**

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
git add references/classics tests/test_index_contract.py
git commit -m "docs(classics): add index routing and seven topic card files"
```

---

### Task 9: master Output Shape 增加引用字段（Spec §8.1）

**Files:**
- Modify: `references/school-prompts/ziping-pattern-master.md`
- Modify: `references/school-prompts/strength-balance-master.md`
- Modify: `references/school-prompts/tiaohou-season-master.md`
- Modify: `references/school-prompts/shensha-support-master.md`
- Modify: `references/school-prompts/xiangfa-blind-master.md`
- Modify: `references/school-prompts/ziwei-master.md`
- Modify: `references/school-prompts/day-selection-master.md`
- Modify: `references/school-prompts/compatibility-master.md`
- Test: `tests/test_prompt_contract.py`

**Interfaces:**
- Consumes: `references/classics/index.md`（Task 8）
- Produces: 每个 master 的 `Output Shape` 含 `citations:` 与 `citation_fit:`；
  有典籍支撑的四个 master 的 Knowledge Slice 指向 `references/classics/index.md`

- [ ] **Step 1: 写失败的测试**

创建 `tests/test_prompt_contract.py`：

```python
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROMPTS = REPO / "references" / "school-prompts"

MASTERS = (
    "ziping-pattern-master",
    "strength-balance-master",
    "tiaohou-season-master",
    "shensha-support-master",
    "xiangfa-blind-master",
    "ziwei-master",
    "day-selection-master",
    "compatibility-master",
)

CLASSICS_BACKED = (
    "ziping-pattern-master",
    "strength-balance-master",
    "tiaohou-season-master",
    "shensha-support-master",
)

NO_BASIS_ONLY = ("xiangfa-blind-master", "ziwei-master", "day-selection-master")


def read(name: str) -> str:
    return (PROMPTS / f"{name}.md").read_text(encoding="utf-8")


class PromptContractTest(unittest.TestCase):
    def test_every_master_declares_citations_field(self):
        for name in MASTERS:
            self.assertIn("citations:", read(name), f"{name} missing citations field")

    def test_every_master_declares_citation_fit_field(self):
        for name in MASTERS:
            self.assertIn(
                "citation_fit:", read(name), f"{name} missing citation_fit field"
            )

    def test_every_master_mentions_no_classical_basis(self):
        for name in MASTERS:
            self.assertIn(
                "no_classical_basis", read(name), f"{name} missing no_classical_basis"
            )

    def test_classics_backed_masters_point_at_index(self):
        for name in CLASSICS_BACKED:
            self.assertIn(
                "references/classics/index.md", read(name), f"{name} missing index route"
            )

    def test_unsupported_masters_are_pinned_to_no_classical_basis(self):
        for name in NO_BASIS_ONLY:
            text = read(name)
            self.assertIn(
                "一律 `no_classical_basis`", text, f"{name} must be pinned to no basis"
            )

    def test_ziping_master_keeps_pattern_call_downgrade_rule(self):
        text = read("ziping-pattern-master")
        self.assertIn("pattern_tendency", text)
        self.assertIn("核心论断", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest tests.test_prompt_contract -v`
Expected: FAIL —— `ziping-pattern-master missing citations field`

- [ ] **Step 3: 改写八个 prompt 文件**

对**全部八个** master，在各自 `## Output Shape` 的 ```text 块内，
`confidence:` 之前插入两行：

```text
citations:      # 必填。[DTS-0142, ZPZQ-0007]；确无可引则写 no_classical_basis
citation_fit:   # 每个被引 ID 一行，行首为该 ID，说明它为何适用于本盘
```

对**有典籍支撑的四个** master（`ziping-pattern-master`、`strength-balance-master`、
`tiaohou-season-master`、`shensha-support-master`），在 `## Knowledge Slice` 段末追加：

```markdown
典籍条文见 `references/classics/index.md`。按「流派 → 主题」表只读本流派对应的
`cards/NN-*.md`；不要通读 `corpus/`，需要原文时用
`python3 scripts/search_classics.py "<关键词>" --corpus` 定位。
每条引用必须带卡片 ID，并在 `citation_fit` 中逐条对上该卡的「适用前提」。
```

对 `ziping-pattern-master.md`，在 `## Method Checklist` 第 3 条之后插入一条：

```markdown
3b. 宣称 `formal_pattern` 前，确认至少有一张「核心论断」或「操作规则」级卡片支撑；
    否则降级为 `pattern_tendency`。
```

对 `shensha-support-master.md`，把现有的「full BaZi ShenSha calculation is not
currently a source-of-truth feature」一段之后补一句，反映本期升级：

```markdown
三命通会神煞篇条文已入卡片库（`cards/60-shensha.md`），神煞解释因此有条文支撑；
但神煞的**计算**仍不是 source-of-truth —— 不得自行推算神煞落宫，只能解释
evidence packet 中已给出的神煞项。
```

对 `xiangfa-blind-master.md`，把 Knowledge Slice 第一条改写为：

```markdown
- 本流派无公有领域权威文本可依。象法口诀多为近现代整理本，版权风险高，
  因此本 skill **不为盲派伪造典籍支撑**：`citations` 一律 `no_classical_basis`。
- 明确标注「无典籍支撑」比含糊其辞更可靠。报告尾注须注明
  「该部分为象法推演，无典籍条文支撑」。
```

对 `ziwei-master.md` 与 `day-selection-master.md`，各在 Knowledge Slice 段末追加：

```markdown
本期无典籍支撑（二期分别引入紫微斗数全书 / 协纪辨方书）。
`citations` 一律 `no_classical_basis`。
```

对 `compatibility-master.md`，在 Knowledge Slice 段末追加：

```markdown
合盘无专门古籍，本期 `citations` 一律 `no_classical_basis`；引用十神、旺衰等
通用条文时可带对应卡片 ID，但不得声称存在「合盘专书」依据。
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest discover -s tests -t . -v`
Expected: PASS，78 tests

- [ ] **Step 5: 提交**

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
git add references/school-prompts tests/test_prompt_contract.py
git commit -m "feat(prompts): require citations and citation_fit in every master output"
```

---

### Task 10: 裁判源层级与审计义务（Spec §8.2）

**Files:**
- Modify: `references/agent-roles.md:30` 附近的源层级段落
- Modify: `references/school-prompts/referee.md`
- Test: `tests/test_referee_contract.py`

**Interfaces:**
- Consumes: `references/classics/index.md`、`scripts/validate_citations.py`
- Produces: 裁判文档含六级源层级与四项审计义务

- [ ] **Step 1: 写失败的测试**

创建 `tests/test_referee_contract.py`：

```python
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AGENT_ROLES = REPO / "references" / "agent-roles.md"
REFEREE = REPO / "references" / "school-prompts" / "referee.md"


class RefereeContractTest(unittest.TestCase):
    def setUp(self):
        self.agent_roles = AGENT_ROLES.read_text(encoding="utf-8")
        self.referee = REFEREE.read_text(encoding="utf-8")

    def test_source_hierarchy_splits_classics_into_two_tiers(self):
        for text, name in ((self.agent_roles, "agent-roles"), (self.referee, "referee")):
            self.assertIn("核心论断", text, f"{name} missing strong classics tier")
            self.assertIn("例证", text, f"{name} missing example classics tier")

    def test_referee_must_run_the_validator(self):
        self.assertIn("validate_citations.py", self.referee)

    def test_referee_must_void_unmet_premises(self):
        self.assertIn("适用前提", self.referee)
        self.assertIn("作废", self.referee)

    def test_referee_must_record_rival_resolution(self):
        self.assertIn("rival_resolution", self.referee)
        self.assertIn("竞合", self.referee)

    def test_referee_keeps_lone_evidence_rule(self):
        self.assertIn("孤证不立", self.referee)

    def test_lone_evidence_is_documented_as_prompt_rule_not_script_check(self):
        self.assertIn("不由脚本检查", self.referee)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest tests.test_referee_contract -v`
Expected: FAIL —— `agent-roles missing strong classics tier`

- [ ] **Step 3: 改写两个文档**

在 `references/agent-roles.md` 中，把源层级那一行（现为
`code facts > project contract > task-specific method fit > cross-school consensus > narrative preference`）
替换为：

```markdown
The referee is not a vote counter. If schools disagree, decide by evidence
quality and source hierarchy:

1. code facts
2. project contract
3. 典籍条文（`核心论断` / `操作规则` 级）
4. task-specific method fit
5. 典籍条文（`例证` 级）
6. cross-school consensus
7. narrative preference

典籍刻意拆成两档插在方法适配的两侧：核心论断压过方法适配，例证级低于方法适配。
这是为了避免退化成「引了本书就赢」。`存疑` 级条文不进入源层级，只能作
「另有一说」提示。
```

在 `references/school-prompts/referee.md` 中，写入同一份源层级（**不要写成
「见 agent-roles.md」** —— 该文件会被单独加载，必须自带完整内容）：

```markdown
## 源层级

1. code facts
2. project contract
3. 典籍条文（`核心论断` / `操作规则` 级）
4. task-specific method fit
5. 典籍条文（`例证` 级）
6. cross-school consensus
7. narrative preference

典籍刻意拆成两档插在方法适配的两侧：核心论断压过方法适配，例证级低于方法适配。
这是为了避免退化成「引了本书就赢」。`存疑` 级条文不进入源层级，只能作
「另有一说」提示。
```

并追加：

```markdown
## 引用审计义务

裁判在综合之前必须完成以下四项：

1. **核对存在性** —— 运行
   `python3 scripts/validate_citations.py --answer <master 输出> --classics-root references/classics`，
   确认每个被引卡片 ID 真实存在。
2. **核对适用前提** —— 逐条检查该卡「适用前提」是否被 evidence packet 满足。
   不满足则该引用**作废**，并在输出中记录作废原因。作废后若该判断再无支撑，
   须降级措辞。
3. **记录竞合取舍** —— 若两个 master 引用了互为「竞合」的卡片，必须在最终输出写出
   `rival_resolution: <采纳ID> over <落选ID> — <理由>`。**禁止静默取一。**
4. **孤证不立** —— 事件级或人生结果级判断需 ≥2 条独立证据（不同典籍，或
   「典籍条文 + 盘面特征」组合）。

第 4 条**不由脚本检查**：「事件级判断」无法从自由文本可靠分类，一个会漏判的
自动检查比没有检查更危险 —— 它会给出虚假的安全感。因此这条由裁判自行执行，
并在输出中显式说明每个事件级判断依据了哪两条证据。
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest discover -s tests -t . -v`
Expected: PASS，84 tests

- [ ] **Step 5: 提交**

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
git add references/agent-roles.md references/school-prompts/referee.md tests/test_referee_contract.py
git commit -m "feat(referee): insert classics into source hierarchy and add citation audit"
```

---

### Task 11: 报告「依据索引」章节（Spec §8.3）

**Files:**
- Modify: `references/report-generation.md`
- Modify: `references/school-prompts/safety-editor.md`
- Test: `tests/test_report_contract.py`

**Interfaces:**
- Consumes: `scripts/validate_citations.py --answer`
- Produces: 报告文档定义「依据索引」固定章节与四列表头；`safety-editor` 增检查项

- [ ] **Step 1: 写失败的测试**

创建 `tests/test_report_contract.py`：

```python
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REPORT = REPO / "references" / "report-generation.md"
SAFETY = REPO / "references" / "school-prompts" / "safety-editor.md"


class ReportContractTest(unittest.TestCase):
    def setUp(self):
        self.report = REPORT.read_text(encoding="utf-8")
        self.safety = SAFETY.read_text(encoding="utf-8")

    def test_report_defines_index_section(self):
        self.assertIn("依据索引", self.report)

    def test_report_defines_four_columns(self):
        for column in ("卡片ID", "典籍出处", "原文", "本盘适用理由"):
            self.assertIn(column, self.report, f"missing column: {column}")

    def test_report_keeps_body_free_of_inline_markers(self):
        self.assertIn("正文不带角标", self.report)

    def test_report_requires_validator_run(self):
        self.assertIn("validate_citations.py", self.report)

    def test_report_documents_no_basis_annotation(self):
        self.assertIn("无典籍条文支撑", self.report)

    def test_safety_editor_checks_index_section(self):
        self.assertIn("依据索引", self.safety)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest tests.test_report_contract -v`
Expected: FAIL —— `AssertionError: '依据索引' not found`

- [ ] **Step 3: 改写两个文档**

在 `references/report-generation.md` 的章节结构定义之后，追加：

````markdown
## 依据索引（固定章节）

每份使用典籍条文的报告，末尾必须有「依据索引」章节：

```markdown
## 依据索引

| 卡片ID | 典籍出处 | 原文 | 本盘适用理由 |
|---|---|---|---|
| DTS-0142 | 滴天髓·通神论·衰旺 | 能知衰旺之真机，其于三命之奥，思过半矣。 | 本造月令为寅，藏干齐备，满足该条前提 |
```

规则：

- **正文不带角标。** 中文报告行内堆角标可读性差，且容易退化成本 skill 明令禁止的
  装饰性引用。可追溯性由尾注承担。
- 正文每个结构性论断必须能在依据索引中找到对应行。
- 无典籍支撑的段落（如象法推演）在该段落末尾单独注明
  「该部分为象法推演，无典籍条文支撑」，不进入依据索引表。
- 组稿完成后运行：

  ```bash
  python3 scripts/validate_citations.py --answer report.md --classics-root references/classics
  ```

  它会检查正文出现的每个卡片 ID 都在依据索引中，且索引中没有不存在的卡片。
````

在 `references/report-generation.md` 的 QA 检查清单中追加一条：

```markdown
- Confirm the report has a 依据索引 section covering every structural claim, and that
  `validate_citations.py --answer` passes on the composed report.
```

在 `references/school-prompts/safety-editor.md` 的 Method Checklist 中，
在现有第 5 条之后追加：

```markdown
6. If report: does it have a 依据索引 section, does every structural claim in the body
   appear there, and are no-basis sections explicitly annotated as
   「无典籍条文支撑」?
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest discover -s tests -t . -v`
Expected: PASS，90 tests

- [ ] **Step 5: 提交**

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
git add references/report-generation.md references/school-prompts/safety-editor.md tests/test_report_contract.py
git commit -m "feat(report): add mandatory 依据索引 section and safety check"
```

---

### Task 12: 改写三处旧措辞并更新资源清单（Spec §8.4）

**Files:**
- Modify: `references/bazi-domain-reference.md:124`
- Modify: `references/analysis-methods.md:14`
- Modify: `references/school-prompts/index.md:10`
- Modify: `SKILL.md`
- Modify: `README.md`
- Test: `tests/test_citation_policy.py`

**Interfaces:**
- Consumes: 前 11 个任务的全部产出
- Produces: 全仓库引用政策一致；`SKILL.md` 与 `README.md` 反映知识层与两个新脚本

- [ ] **Step 1: 写失败的测试**

创建 `tests/test_citation_policy.py`：

```python
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

POLICY_FILES = (
    REPO / "references" / "bazi-domain-reference.md",
    REPO / "references" / "analysis-methods.md",
    REPO / "references" / "school-prompts" / "index.md",
)

STALE_PHRASES = (
    "Avoid decorative citation.",
    "Do not cite a classical text decoratively.",
    "Do not quote classical book names decoratively.",
)


class CitationPolicyTest(unittest.TestCase):
    def test_stale_prohibition_wording_is_gone(self):
        for path in POLICY_FILES:
            text = path.read_text(encoding="utf-8")
            for phrase in STALE_PHRASES:
                self.assertNotIn(phrase, text, f"{path.name} still has: {phrase}")

    def test_each_policy_file_points_at_the_validator(self):
        for path in POLICY_FILES:
            text = path.read_text(encoding="utf-8")
            self.assertIn("validate_citations.py", text, f"{path.name} missing validator")

    def test_each_policy_file_requires_card_ids(self):
        for path in POLICY_FILES:
            text = path.read_text(encoding="utf-8")
            self.assertIn("卡片 ID", text, f"{path.name} missing card ID requirement")

    def test_school_prompts_index_documents_no_classical_basis(self):
        text = (REPO / "references" / "school-prompts" / "index.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("no_classical_basis", text)

    def test_skill_md_routes_classics_tasks(self):
        text = (REPO / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/classics/index.md", text)
        self.assertIn("validate_citations.py", text)
        self.assertIn("search_classics.py", text)

    def test_readme_lists_the_new_scripts(self):
        text = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertIn("validate_citations.py", text)
        self.assertIn("search_classics.py", text)
        self.assertIn("references/classics/", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest tests.test_citation_policy -v`
Expected: FAIL —— `bazi-domain-reference.md still has: Avoid decorative citation.`

- [ ] **Step 3: 改写五个文件**

`references/bazi-domain-reference.md` 末行替换为：

```markdown
Cite a classical text only through a card ID from `references/classics/index.md`.
Every citation must survive `python3 scripts/validate_citations.py`. Delete any
book-name mention that has no backing 卡片 ID —— 装饰性引用一律删除。
```

`references/analysis-methods.md:14` 替换为：

```markdown
Cite a classical text only through a card ID from `references/classics/index.md`,
and verify it with `python3 scripts/validate_citations.py`. A book name without a
backing 卡片 ID is decoration —— delete it.
```

`references/school-prompts/index.md:10`（Source Policy 的最后一条）替换为：

```markdown
- Cite classics only through card IDs from `references/classics/index.md`; every
  citation must pass `python3 scripts/validate_citations.py`. A book name without a
  backing 卡片 ID is decoration —— delete it. When no card applies, write
  `no_classical_basis` —— that is as legitimate an answer as a real citation, and
  carries no penalty. The point of the required `citations` field is to force an
  explicit answer to "is there a basis", not to force a citation.
```

在 `SKILL.md` 的 Workflow 第 1 步分类清单中，追加一条路由：

```markdown
   - 古籍条文、典籍引用、条文出处、引用核对，或需要为判断补依据: read
     `references/classics/index.md`, then only the topic card files your school needs;
     verify with `scripts/validate_citations.py`; locate raw source text with
     `scripts/search_classics.py --corpus`. Never read `references/classics/corpus/`
     end to end.
```

在 `SKILL.md` 的 `## Resources` 清单中追加三条：

```markdown
- `references/classics/index.md`: 古籍知识层入口，三向路由、卡片契约、层级定义与引用规范。
- `scripts/validate_citations.py`: 卡片库自检（`--cards`）与答案/报告引用校验（`--answer`）。
- `scripts/search_classics.py`: 零依赖检索，卡片优先、原文回落。
```

在 `SKILL.md` 的 `## Useful Commands` 追加：

````markdown
校验卡片库：

```bash
python3 scripts/validate_citations.py --cards references/classics
```

校验一份 master 输出或报告的引用使用：

```bash
python3 scripts/validate_citations.py --answer answer.md --classics-root references/classics
```

检索条文：

```bash
python3 scripts/search_classics.py "衰旺真机" --school 旺衰扶抑
python3 scripts/search_classics.py "余寒犹存" --corpus
```
````

在 `README.md` 的「目录结构」小节追加两条：

```markdown
- `references/classics/`：古籍知识层。`index.md` 三向路由、`cards/` 按命理主题分片的条文卡片、
  `corpus/` 精选原文底库与 `PROVENANCE.md` 溯源清单。
- `scripts/validate_citations.py`、`scripts/search_classics.py`：引用校验与零依赖检索。
```

在 `README.md` 的「核心原则」小节追加一条：

```markdown
- 引用必须可核对：典籍条文一律通过卡片 ID 引用，原文可机械比对语料原文；
  确无可引时显式写 `no_classical_basis`。这套机制不追求让预测更准（命理判断不可证伪），
  而是让输出可追溯、可反驳、边界清楚。
```

在 `README.md` 的架构图中，把 `R["references/..."]` 节点之后补一个知识层节点：

```mermaid
    R --> RC["references/classics/<br/>条文卡片 + 精选原文 + 引用契约"]
    RC --> E
```

- [ ] **Step 4: 运行全套测试确认通过**

Run: `cd /Users/xuemian/SynologyDrive/QUT/bazi-skill && python3 -m unittest discover -s tests -t . -v`
Expected: PASS，96 tests

确认旧措辞已全部清除：

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
grep -rn "decoratively\|decorative citation" references/ SKILL.md README.md; echo "exit=$?"
```

Expected: 无输出，`exit=1`（grep 未命中）

确认两个 CLI 在真实（空）卡片库上行为正确：

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
python3 scripts/validate_citations.py --cards references/classics --count; echo "exit=$?"
python3 scripts/search_classics.py "衰旺" --classics-root references/classics; echo "exit=$?"
```

Expected: 前者 `cards: 0` + `VALID` + `exit=0`；后者 `no hits` + `exit=1`

- [ ] **Step 5: 提交**

```bash
cd /Users/xuemian/SynologyDrive/QUT/bazi-skill
git add references SKILL.md README.md tests/test_citation_policy.py
git commit -m "feat(policy): make citation rules executable and wire classics layer into SKILL/README"
```

---

## 完成后的状态

- `python3 -m unittest discover -s tests -t . -v` —— 96 tests，全绿
- `scripts/validate_citations.py` 双模式可用，固件语料下全链路跑通
- `scripts/search_classics.py` 卡片与原文双路检索可用
- 四处输出契约改写完成，三处旧措辞不再出现
- `references/classics/` 骨架就位，`cards/` 七个主题文件待 Phase 3 填充
- 零第三方依赖

**下一步：** Spec Phase 2 语料入库另立计划。入库后须回头核对 Task 5 那 5 张样例卡片的
原文与出处，并把它们从 `tests/fixtures/` 迁移为 `references/classics/cards/` 的真实卡片。
