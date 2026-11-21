import re

from .schemas import FieldLabel, Risk

RISK_PATTERNS: dict[Risk, re.Pattern[str]] = {
    "legal": re.compile(r"裁判所|訴訟|立退|退去命令|契約解除|eviction|court order", re.I),
    "immigration": re.compile(r"在留|入管|出入国|visa|immigration", re.I),
    "medical": re.compile(r"診断|処方|検査結果|投薬|prescription|diagnosis", re.I),
    "threatening": re.compile(r"最終通告|差押|強制執行|seizure|final notice", re.I),
    "money": re.compile(r"納付|請求|振込|支払|円|¥|payment|invoice|tax", re.I),
}
RISK_ORDER: tuple[Risk, ...] = ("legal", "immigration", "medical", "threatening", "money")

KIND_PATTERNS = [
    (re.compile(r"再配達|不在連絡票|お届け|redelivery|delivery", re.I), "delivery notice"),
    (re.compile(r"ごみ|ゴミ|資源|収集|garbage|recycling", re.I), "waste collection notice"),
    (re.compile(r"断水|停電|点検|工事|maintenance|water outage", re.I), "maintenance notice"),
    (re.compile(r"納付|請求|振込|支払|payment|invoice", re.I), "payment notice"),
    (re.compile(r"区役所|市役所|役場|ward office|city office", re.I), "local government notice"),
]

FIELD_PATTERNS: dict[FieldLabel, re.Pattern[str]] = {
    "Date": re.compile(
        r"令和\s*\d{1,2}年\s*\d{1,2}月\s*\d{1,2}日|"
        r"\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{1,2}月\s*\d{1,2}日"
    ),
    "Amount": re.compile(r"[¥￥]\s?[\d,]+|[\d,]+\s?円"),
    "Phone": re.compile(r"0\d{1,4}[-‐–]?\d{1,4}[-‐–]?\d{3,4}"),
}

HIGH_RISK: frozenset[Risk] = frozenset({"legal", "immigration", "medical", "threatening"})
