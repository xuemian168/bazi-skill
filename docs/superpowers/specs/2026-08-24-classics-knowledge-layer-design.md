# 古籍知识层设计（Classics Knowledge Layer）

- 日期：2026-08-24
- 状态：已批准，待实施
- 影响范围：`references/`、`scripts/`、`SKILL.md`、`README.md`
- 不影响：宿主项目应用代码（前端/后端）

---

## 1. 背景与问题

`bazi-skill` 当前的架构分层是清晰的：代码算事实 → 多流派大师解读 → 裁判综合 → 脚本校验。
问题出在**知识层是空的**。

具体证据：

- `references/school-prompts/*.md` 中每个 master 的 "Knowledge Slice" 均标注为
  "Distilled from `bazi-domain-reference.md`, `analysis-methods.md`" —— 知识来源自我循环，
  没有任何外部典籍支撑。
- `references/school-prompts/xiangfa-blind-master.md:10` 自承
  "Current project references do not contain a complete blind-school 口诀 knowledge base"。
- `references/school-prompts/shensha-support-master.md:11` 自承神煞不是 source-of-truth 特性。
- `references/bazi-domain-reference.md:124`、`references/analysis-methods.md:14`、
  `references/school-prompts/index.md:10` 三处都规定「不要装饰性引用书名」。
  这条规则的意图是对的，但在没有可引典籍的前提下，它实际起的作用是
  「因为无书可引，所以禁止引」。

结果是：master 的判断在**推理形式上**受约束（不许重算、不许编事实），
但在**知识内容上**不受约束 —— 任何一句「此造身弱用印」都无法被追溯、核对或反驳。

### 1.1 同类项目调研

| 仓库 | 做法 | 借鉴点 | 许可 |
|---|---|---|---|
| `HeiGeAi/HeiGe-SuanMing` | `references/` 下 23 个按方法论分层的 md；强制「孤证不立」+ 每条结论标注依据 | 分层编号思路、双证据规则（方法论，非内容） | PolyForm 非商用 —— **仅参考结构，不复制任何内容** |
| `Sudo-Biao/suangua` | 8600+ 行古籍知识库 + BM25 检索 | 证明确定性检索脚本可行，无需向量库 | — |
| `gaaiyun/FOR-BAZI` | 五部经典 JSON + ChromaDB | 语料切分思路 | MIT |
| `youngzs/xuanxue` | mkdocs 组织的典籍研究 | 篇目切分参考；**混入现代评注，不作为语料来源** | — |

### 1.2 关键约束

1. **skill 没有运行时**。它是按需加载的 markdown 集合，跑不了向量数据库或常驻服务。
   因此 RAG 路线必须退化为「结构化卡片 + 纯标准库检索脚本」。
2. **版权**：四部典籍原文属公有领域；但现代整理本的**标点、校勘、注释、白话翻译受版权保护**。
   入库只能用原文，白话必须自行撰写。
3. **不可证伪性**：命理典籍之间互相矛盾且均不可实证。设计目标不是「消除矛盾」。

---

## 2. 目标与非目标

### 2.1 目标

1. 为八字核心链路（月令、旺衰、调候、十神、格局、神煞、运岁）建立**可机械核对**的典籍条文库。
2. 让每条结构性判断带上**可追溯的出处、适用前提、反例边界**。
3. 让**跨流派冲突可见**，并强制裁判显式记录取舍理由。
4. 用确定性脚本保证引用不退化为装饰。

### 2.2 明确的非目标

1. **不追求提高预测准确率**。命理判断不可证伪，本设计不声称提升「准」。
   可交付的是：可追溯、可反驳、边界清楚。
2. 不改宿主项目前端/后端应用代码。
3. 不引入第三方 Python 依赖（jieba、chromadb、sentence-transformers 等一律不用）。
4. 本期不覆盖紫微、择日、合盘的典籍层。
5. 不为盲派象法伪造典籍支撑。

---

## 3. 决策记录

| # | 决策 | 选项 | 采纳 | 理由 |
|---|---|---|---|---|
| D1 | 知识形态 | 纯卡片 / 纯全文 / 混合 / 仅书目 | **混合两层：卡片为主 + 全文兜底** | 卡片保证引用精度与 token 可控；全文提供引文核对底库 |
| D2 | 典籍范围 | 四书 / 六书 / 全域八书 | **八字核心四书**（滴天髓、子平真诠、穷通宝鉴、三命通会） | 精准覆盖日常排盘最高频的四条链路；紫微/择日在 repo 中本就是未实现状态，先堆知识会跑在代码前面 |
| D3 | 引用可见度 | 仅内部 / 按需展开 / 三层 / 行内角标 | **三层：master 必填 → 裁判审计 → 报告尾注** | 可审计且不破坏阅读体验；行内角标会退化成现已禁止的装饰性引用 |
| D4 | 全文入库粒度 | 精选篇卷 / 全文全入 / 不 vendor / 延后 | **精选篇卷** | 三命通会十二卷中大半为纳音、星命、六壬杂论，与八字链路无关，全量入库会让检索被噪音淹没 |
| D5 | 卡片分片轴 | 按主题 / 按典籍 / 按 master | **按命理主题** | master 按分析层面提问而非按书提问，单次加载命中率最高；同主题下不同典籍的对立主张物理相邻，冲突可见 |

### D5 备选方案与否决理由

- **按典籍分片**（`cards/dts.md`、`cards/zpzq.md`）：校对最容易，新增典籍符合 OCP。
  否决：master 查「调候」需跨 4 个文件全读，token 浪费；冲突被典籍边界拆散。
- **按 master 分片**（`knowledge/ziping.md` 等）：加载最简单。
  否决：违反 DRY —— 滴天髓同一条会在旺衰/调候/格局三处复制，改一处要改三处；
  且跨流派冲突彻底不可见，主动削弱本设计的核心目标。

---

## 4. 架构

### 4.1 目录布局

```
references/classics/
  index.md                          # 三向路由表 + 引用规范 + 层级定义
  cards/
    10-yueling.md                   # 月令司令、得时失时
    20-wangshuai.md                 # 旺衰强弱、扶抑
    30-tiaohou.md                   # 调候、寒暖燥湿
    40-shishen.md                   # 十神性情与作用
    50-geju.md                      # 格局成败救应
    60-shensha.md                   # 神煞
    70-yunsui.md                    # 大运流年
  corpus/
    PROVENANCE.md                   # 语料溯源清单
    ditiansui.txt
    ziping-zhenquan.txt
    qiongtong-baojian.txt
    sanming-tonghui.selected.txt
scripts/
  validate_citations.py             # 卡片自检 + 答案引用核对
  search_classics.py                # 零依赖检索，卡片优先、原文回落
docs/superpowers/specs/
  2026-08-24-classics-knowledge-layer-design.md   # 本文件
```

### 4.2 加载路径（渐进披露）

```
SKILL.md
  └─(需要典籍时)→ references/classics/index.md
        └─(按主题路由)→ cards/NN-<topic>.md   ← master 通常只读 1-2 个
              └─(仅两种情况)→ corpus/*.txt
                    (a) 裁判核对引文原文
                    (b) master 返回 evidence_gap 需深挖
```

**关键约束：corpus 是证据底库，不是阅读材料。**
LLM 不通读原文 —— 通读原文是断章取义风险最高的操作。
访问 corpus 一律经由 `search_classics.py` 定位到具体段落。

### 4.3 组件职责

| 组件 | 唯一职责 | 不负责 |
|---|---|---|
| `index.md` | 路由与规范。主题↔卡片段、流派↔主题、典籍↔主题三向索引 | 承载条文内容 |
| `cards/*.md` | 承载可引用的条文卡片，单一真相源 | 计算、排盘、检索 |
| `corpus/*.txt` | 原文底库，供机械核对与深挖 | 直接喂给 LLM 阅读 |
| `PROVENANCE.md` | 语料溯源与完整性校验基线 | 内容本身 |
| `validate_citations.py` | 确定性校验 | 生成、修复内容 |
| `search_classics.py` | 定位检索 | 解释、判断 |

---

## 5. 卡片契约

### 5.1 字段定义

| 字段 | 必填 | 类型 | 说明 |
|---|---|---|---|
| `id` | 是 | `PREFIX-NNNN` | 稳定标识，一经发布不得变更或复用 |
| `典籍` | 是 | 字符串 | `书名·篇·节`，尽可能定位到最小篇目 |
| `原文` | 是 | 字符串 | **必须是所声明 corpus 文件的精确子串**（正规化后） |
| `白话` | 是 | 字符串 | 自行撰写，禁止摘抄现代整理本译文 |
| `适用前提` | 是 | 列表 | 触发该条所需的盘面事实；裁判据此判定引用是否成立 |
| `层级` | 是 | 枚举 | `核心论断` / `操作规则` / `例证` / `存疑` |
| `流派` | 是 | 列表 | 对应 master 名，可多值 |
| `竞合` | 否 | 列表 | 与之对立或竞争的卡片 ID + 一句差异说明；**必须双向** |
| `反例边界` | 是 | 字符串 | 该条**不适用**的情形。防规则外推 |
| `corpus` | 是 | `corpus/<file>#L<a>-L<b>` | 原文定位 |

`反例边界` 设为必填是有意的：命理误判绝大多数来自把有条件的规则当无条件用。
若确实找不到边界，写「未见明确边界，按存疑级处理」并将 `层级` 降为 `存疑`。

### 5.2 ID 前缀

本期启用：

| 前缀 | 典籍 |
|---|---|
| `DTS` | 滴天髓 |
| `ZPZQ` | 子平真诠 |
| `QTBJ` | 穷通宝鉴 |
| `SMTH` | 三命通会 |

二期保留前缀 —— **本期视为非法**，卡片不得使用；校验器报错并提示「前缀尚未启用」：
`YHZP` 渊海子平、`SFTK` 神峰通考、`ZWDS` 紫微斗数全书、`XJFF` 协纪辨方书。

启用一个新前缀的唯一条件：其 corpus 文件已入库并在 `PROVENANCE.md` 登记。

### 5.3 层级定义与权重

| 层级 | 含义 | 裁判用法 |
|---|---|---|
| `核心论断` | 典籍中提纲挈领的原则性主张 | 可单独支撑结构性判断；在源层级中高于方法适配 |
| `操作规则` | 可直接套用的判定规则或取用口径 | 可单独支撑结构性判断 |
| `例证` | 具体命例或举例说明 | **不可单独支撑结构性判断**；在源层级中低于方法适配 |
| `存疑` | 版本歧异、语义不明、或流派争议未决 | 仅可作为「另有一说」提示，不得作为结论依据 |

### 5.4 完整示例

```markdown
### DTS-0142
- 典籍: 滴天髓·通神论·衰旺
- 原文: 能知衰旺之真机其于三命之奥思过半矣
- 白话: 判旺衰不看五行数量，而看得令、得地、得势三者的实际承载。
- 适用前提:
  - 已知月令
  - 已知日主
  - 已知地支藏干
- 层级: 核心论断
- 流派: 旺衰扶抑, 子平格局
- 竞合:
  - ZPZQ-0031 — 子平真诠主张先以月令定格，再论强弱；滴天髓主张强弱真机先行
- 反例边界: 从格、化格不适用此条；日主已不以自身强弱论
- corpus: corpus/ditiansui.txt#L88-L89
```

对应的 `ZPZQ-0031` 必须回指 `DTS-0142`，否则 `--cards` 校验失败。

### 5.5 原文正规化规则

`原文` 与 corpus 比对前，双方均执行：

1. 删除所有空白字符（含全角空格）
2. 删除标点：`。，、；：？！「」『』《》〈〉（）()·—…“”‘’`
3. 保留全部 CJK 字符与数字
4. 不做繁简转换 —— 卡片与 corpus 必须字形一致（由入库时统一）

---

## 6. 索引契约（`index.md`）

必须包含三张路由表：

1. **主题 → 卡片文件 + ID 段**（供 master 定位该读哪个文件）
2. **流派 → 主题清单**（供 master 知道自己该看哪些主题）
3. **典籍 → 主题分布 + corpus 文件**（供裁判核对与深挖）

外加：卡片契约摘要、层级定义、引用书写规范、`no_classical_basis` 的使用条件。

---

## 7. 语料契约

### 7.1 来源优先级

1. **维基文库 / ctext.org** —— 公有领域出处最清晰、定位稳定、无现代评注混入
2. GitHub 纯文本（已确认 `mymmsc/books` 有 `三命通会.txt` 606KB、`渊海子平.txt` 166KB）
3. PDF 抽取（`pdftotext`）—— 滴天髓、穷通宝鉴目前只找到 PDF，需人工校对

### 7.2 清洗规则

- 只保留正文原文
- 剔除现代评注、白话译文、页眉页脚、页码、OCR 噪声行
- 统一字形（繁简择一并全文一致）
- 保留自然分段，行号稳定（行号是 `corpus` 字段的定位基础，入库后不得重排）

### 7.3 `PROVENANCE.md` 必填项

每份语料一条记录：来源 URL、版本/edition 描述、抓取日期、`sha256`、
公有领域依据（作者卒年或朝代）、清洗步骤摘要、人工抽检结论。

`sha256` 由 `validate_citations.py --cards` 校验，语料被意外改动会被立即发现。

### 7.4 三命通会取卷范围

只入与八字链路相关的卷次：神煞、十神、格局、大运相关篇目。
具体卷次在 Phase 2 入库时确定并记入 `PROVENANCE.md`，后续可增量补入。

---

## 8. 输出契约变更

### 8.1 master 输出（改 `references/school-prompts/*.md` 的 Output Shape）

新增两个字段：

```text
citations:      # 必填。[DTS-0142, ZPZQ-0007]；确无可引则写 no_classical_basis
citation_fit:   # 每条引用为何适用于本盘，须逐条对上卡片的「适用前提」
```

新增硬规则：

> 结构性判断（宣称某格、某神为用、某某为病）必须有 ≥1 张 `核心论断` 或 `操作规则`
> 级卡片支撑。否则 `pattern_call` 降级为 `pattern_tendency`。

该规则复用 `ziping-pattern-master.md` 已有的 `pattern_call` 枚举，不引入新概念。

### 8.2 裁判源层级（改 `references/agent-roles.md:30` 与 `school-prompts/referee.md`）

原：

```
code facts > project contract > method fit > cross-school consensus > narrative preference
```

改为：

```
code facts
  > project contract
  > 典籍条文（核心论断 / 操作规则级）
  > task-specific method fit
  > 典籍条文（例证级）
  > cross-school consensus
  > narrative preference
```

典籍**拆成两档插在不同位置**，是为了避免退化成「引了本书就赢」。

裁判新增四项义务：

1. 运行 `validate_citations.py` 核对每个 citation ID 存在。
2. 逐条检查卡片「适用前提」是否被 evidence packet 满足；不满足则该引用作废，
   并在输出中记录作废原因。
3. 若两个 master 引用了互为 `竞合` 的卡片，**必须在最终输出显式记录采纳了哪条、
   为何采纳**。禁止静默取一。
4. 孤证不立：事件级或人生结果级判断需 ≥2 条独立证据
   （不同典籍，或「典籍条文 + 盘面特征」组合）。

### 8.3 报告尾注（改 `references/report-generation.md`）

新增固定章节「依据索引」，表格列：

| 卡片ID | 典籍出处 | 原文 | 本盘适用理由 |

正文**不带角标**（保持现有可读性偏好），但正文每个结构性论断必须能在尾注中
找到对应行。`validate_citations.py --answer` 校验这一覆盖关系。

### 8.4 重写三处旧措辞

| 位置 | 原措辞 | 新措辞要点 |
|---|---|---|
| `references/bazi-domain-reference.md:124` | "Use classical book names only when the actual rule is being applied. Avoid decorative citation." | 引用必须带卡片 ID 且通过 `validate_citations.py` 核对；无卡片支撑的书名提及一律删除 |
| `references/analysis-methods.md:14` | "Do not cite a classical text decoratively." | 同上 |
| `references/school-prompts/index.md:10` | "Do not quote classical book names decoratively." | 同上，并补充 `no_classical_basis` 的正确用法 |

规则精神不变（禁止装饰性引用），实现从**不可执行的禁令**变为**可执行的校验**。

---

## 9. 校验器规格

### 9.1 `scripts/validate_citations.py`

纯 Python 标准库，与现有 `scripts/validate_analysis_result.py` 的 CLI 风格一致
（位置参数取文件、`-` 取 stdin、退出码 0/1、逐条打印错误）。

**模式 A：`--cards`（卡片库自检，提交前 / CI）**

1. 必填字段齐全
2. `id` 全局唯一，前缀合法
3. `层级` 与 `流派` 取值在枚举内
4. `原文` 正规化后是所声明 corpus 文件的子串
5. `corpus` 行号范围存在且包含该原文
6. `竞合` 双向闭合（A→B 则必须 B→A）
7. `corpus/*.txt` 的 `sha256` 与 `PROVENANCE.md` 记录一致
8. 卡片使用了未启用前缀（见 5.2），或前缀已启用但缺对应 corpus 文件 → 报错

**模式 B：`--answer <file|->`（引用使用校验）**

输入可以是 master 输出、裁判综合结果、或报告规格三者之一，
由文件中是否存在「依据索引」章节自动判别类型。

对全部三种输入：

1. 所有引用 ID 在卡片库中存在
2. 结构性判断有足够层级的卡片支撑（否则要求降级为 `pattern_tendency`）
3. 事件级判断满足「孤证不立」（≥2 条独立证据）
4. 若存在 `竞合` 引用，检查是否记录了取舍理由

仅对报告规格额外校验：

5. 「依据索引」章节存在，且覆盖正文全部结构性论断

### 9.2 `scripts/search_classics.py`

- 零第三方依赖。中文按 **2-gram 切分 + TF 加权**，不引 jieba。
- 默认检索卡片（返回 ID + 典籍 + 白话 + 层级）
- `--corpus` 落到原文，返回文件名 + 行号 + 上下文窗口
- `--topic <name>` 限定主题文件，`--school <name>` 限定流派

---

## 10. 各 master 处理矩阵

| Master | 本期典籍支撑 | 处理 |
|---|---|---|
| `ziping-pattern-master` | 子平真诠、渊海子平（二期） | 格局主源，卡片重点 |
| `strength-balance-master` | 滴天髓 | 旺衰主源，卡片重点 |
| `tiaohou-season-master` | 穷通宝鉴 | 调候主源，**Phase 3 首个交付**（日干×月令近乎结构化表格，最快见效） |
| `shensha-support-master` | 三命通会（神煞卷） | **本期受益最大**：从「非 source-of-truth」升级为「有条文支撑，但仍非计算权威」 |
| `xiangfa-blind-master` | 无 | 明确定位为「象法推理框架（无古籍支撑层）」，强制 `citations: no_classical_basis`；报告尾注注明「该部分为象法推演，无典籍条文支撑」 |
| `ziwei-master` | 无（二期：紫微斗数全书） | 保持 `no_classical_basis` |
| `day-selection-master` | 无（二期：协纪辨方书） | 保持 `no_classical_basis` |
| `compatibility-master` | 无（无专书） | 保持 `no_classical_basis`；二期考虑从三命通会六亲篇归纳 |
| `referee` | — | 新增审计义务（见 8.2） |
| `safety-editor` | — | 新增检查项：尾注章节是否存在且覆盖完整 |

盲派不伪造典籍支撑，是本设计的诚实性底线：
明确标注「无典籍支撑」比含糊其辞更可靠。

---

## 11. 分期计划

### Phase 1 —— 骨架与契约（不依赖语料）

- 建 `references/classics/` 目录结构
- 写 `index.md`（三向路由 + 卡片契约 + 层级定义）
- 实现 `validate_citations.py`（模式 A + B）
- 改写 8.1–8.4 四处输出契约
- 手工编写 5 张样例卡片 + 对应的最小 corpus 片段，跑通全链路

**Phase 1 完成即可验证设计是否成立，无需等待语料。**

### Phase 2 —— 语料入库

- 按 7.1 优先级获取四书文本
- 按 7.2 清洗，按 7.3 记录 PROVENANCE
- 质量门：每份语料人工抽检 10 段，比对可信版本

### Phase 3 —— 卡片编纂（增量，可持续）

顺序：调候（穷通宝鉴）→ 旺衰（滴天髓）→ 格局（子平真诠）→ 神煞（三命通会）
→ 十神 → 运岁 → 月令

每个主题完成即可投入使用，不必等全部完成。

### Phase 4 —— 检索与回归

- 实现 `search_classics.py`
- 建立黄金样本：固定 3 个命盘，对比加入卡片前后的
  **引用覆盖率**与**冲突暴露数**
- 更新 `README.md` 架构图与 `SKILL.md` 资源清单

---

## 12. 风险与缓解

| # | 风险 | 影响 | 缓解 |
|---|---|---|---|
| R1 | 卡片编纂是人力活，四书全编是长期工程 | 进度慢 | Phase 1 骨架先跑通；卡片按主题增量生长，每主题独立可用 |
| R2 | PDF 抽取的滴天髓/穷通宝鉴含 OCR 错字，导致原文核对失败 | 编纂受阻 | 优先维基文库；核对失败本身是校验器在正确工作，不是缺陷 |
| R3 | 版权 —— 误入现代整理本的标点、校注、译文 | 法律风险 | 只入原文；白话自行撰写；PROVENANCE 逐份记录公有领域依据；现代评注一律不入 |
| R4 | 引用过度反噬可读性 | 用户体验下降 | 正文不带角标，仅尾注；`safety-editor` 增加可读性检查 |
| R5 | 典籍互相矛盾且不可证伪 | 无法得出唯一结论 | **不试图消除矛盾**。设计目标是暴露矛盾并强制裁判显式取舍（8.2 第 3 条） |
| R6 | 卡片库与 corpus 漂移 | 引用失真 | `sha256` 基线 + `--cards` 校验；corpus 入库后行号不得重排 |
| R7 | master 为凑 `citations` 字段而牵强引用 | 引用质量下降 | `citation_fit` 必须逐条对上「适用前提」；裁判有义务作废不匹配的引用；`no_classical_basis` 是合法且无惩罚的答案 |

R7 值得单独强调：**必填 `citations` 的设计意图不是逼出引用，而是逼出「有没有依据」这个显式回答。**
`no_classical_basis` 与一个真实引用同等合法。

---

## 13. 验收标准

Phase 1：

1. `python3 scripts/validate_citations.py --cards` 在 5 张样例卡片上退出码 0
2. 故意破坏任一必填字段 / 制造单向 `竞合` / 篡改 `原文` 一字，均能被检出并退出码 1
3. `--answer` 能检出：引用不存在的 ID、结构性判断缺乏足够层级支撑、竞合未记录取舍
4. 四处契约改写完成，三处旧措辞不再出现「禁止引用书名」的表述

Phase 3（每个主题）：

1. 该主题卡片全部通过 `--cards`
2. 对应 master 在黄金样本上，`citations` 给出**真实卡片 ID**（而非 `no_classical_basis`）
   的结构性判断占比 ≥ 80%。分母为该 master 的全部结构性判断
3. 至少暴露 1 组跨典籍 `竞合` 关系

整体：

1. 同一命盘在加入知识层前后，报告新增「依据索引」章节且覆盖全部结构性论断
2. `README.md` 架构图反映知识层
3. 不引入任何第三方 Python 依赖

---

## 14. 越界清单（本设计明确不做）

- 不改宿主项目前端/后端代码
- 不实现向量检索或引入 embedding 依赖
- 不为盲派、紫微、择日、合盘伪造典籍支撑
- 不生成 PDF（沿用现有约束）
- 不声称提升预测准确率
