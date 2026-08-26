"""Classics knowledge layer: card parsing, quote verification, retrieval."""

CARD_TIERS = ("核心论断", "操作规则", "例证", "存疑")

ENABLED_PREFIXES = ("DTS", "ZPZQ", "QTBJ", "SMTH")

RESERVED_PREFIXES = ("YHZP", "SFTK", "ZWDS", "XJFF")

# Which corpus file(s) a card of each enabled prefix is allowed to cite.
# Derived from the 「典籍 → 主题」 table in references/classics/index.md,
# which stated this binding as a contract with nothing enforcing it: quote
# verification proves a quote sits at the cited location, not that the
# location belongs to the book the ID names. Tuple-valued because a single
# classic may be split across volumes (三命通会 first).
PREFIX_CORPUS = {
    "DTS": ("corpus/ditiansui.txt",),
    "ZPZQ": ("corpus/ziping-zhenquan.txt",),
    "QTBJ": ("corpus/qiongtong-baojian.txt",),
    "SMTH": ("corpus/sanming-tonghui.selected.txt",),
}

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
