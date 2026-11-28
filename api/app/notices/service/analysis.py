from pathlib import Path

from langsmith import tracing_context

from app.ocr.client import OcrReader

from ..schemas import AnalysisResult
from .graph import build_analysis_graph


class NoticeAnalyzer:
    def __init__(self, ocr: OcrReader) -> None:
        self.graph = build_analysis_graph(ocr)

    def analyze(self, image_path: Path) -> AnalysisResult:
        # Graph state contains private OCR text; never inherit ambient LangSmith tracing.
        with tracing_context(enabled=False):
            state = self.graph.invoke({"image_path": image_path})
        return state["response"]
