from pathlib import Path

from app.ocr.client import OcrReader

from ..schemas import AnalysisResult
from .compose import compose_result
from .extract import extract_fields
from .triage import classify_kind, classify_risk


class NoticeAnalyzer:
    def __init__(self, ocr: OcrReader) -> None:
        self.ocr = ocr

    def analyze(self, image_path: Path) -> AnalysisResult:
        lines = self.ocr.read(image_path)
        text = "\n".join(line.text for line in lines)
        return compose_result(
            lines=lines,
            fields=extract_fields(lines),
            risk=classify_risk(text) if lines else "unreadable",
            kind=classify_kind(text),
        )
