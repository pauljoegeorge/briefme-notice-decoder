from ..constants import KIND_PATTERNS, RISK_ORDER, RISK_PATTERNS
from ..schemas import Risk


def classify_risk(text: str) -> Risk:
    for risk in RISK_ORDER:
        if RISK_PATTERNS[risk].search(text):
            return risk
    return "routine"


def classify_kind(text: str) -> str:
    return next(
        (name for pattern, name in KIND_PATTERNS if pattern.search(text)), "notice or document"
    )
