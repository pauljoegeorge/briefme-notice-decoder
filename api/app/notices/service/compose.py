from app.ocr.schemas import OcrLine

from ..constants import HIGH_RISK
from ..schemas import AnalysisResult, ExtractedField, Risk


def compose_result(
    lines: list[OcrLine], fields: list[ExtractedField], risk: Risk, kind: str
) -> AnalysisResult:
    if not lines:
        return AnalysisResult(
            risk="unreadable",
            kind="unknown",
            lines=[],
            fields=[],
            what_happened="No text could be read from this photo.",
            action_needed="Please retake the photo with the full notice visible.",
            key_details="No details extracted.",
            warning="The app could not read the notice.",
        )

    if risk in HIGH_RISK:
        what = f"This appears to be a {risk} document."
        action = "Check the original and contact the issuing office or an appropriate professional."
        warning = "This prototype cannot interpret or advise on this kind of document."
    else:
        what = f"This appears to be a {kind}."
        action = "An action may be needed. Check the original notice and its contact details."
        warning = (
            "Verify any amount and deadline against the original."
            if risk == "money"
            else "Preliminary rule-based reading; verify against the original."
        )

    if sum(line.confidence for line in lines) / len(lines) < 0.55:
        warning += " OCR confidence is low. Verify each detail on the original or retake the photo."
    details = ", ".join(f"{field.label.lower()}: {field.value}" for field in fields[:5])
    return AnalysisResult(
        risk=risk,
        kind=kind,
        lines=lines,
        fields=fields,
        what_happened=what,
        action_needed=action,
        key_details=details or "No date, amount, or phone number found.",
        warning=warning,
    )
