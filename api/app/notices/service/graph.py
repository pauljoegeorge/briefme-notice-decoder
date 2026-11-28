"""Explicit notice-analysis workflow; only OCR performs provider I/O."""

from pathlib import Path
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from PIL import Image, UnidentifiedImageError

from app.image_uploads import FORMAT_TO_SUFFIX, MAX_IMAGE_PIXELS, MAX_UPLOAD_BYTES
from app.ocr.client import OcrReader
from app.ocr.schemas import OcrLine

from ..constants import HIGH_RISK
from ..schemas import AnalysisResult, ExtractedField, Risk
from .compose import compose_result
from .extract import extract_fields
from .triage import classify_kind, classify_risk
from .validate import validate_evidence


class AnalysisState(TypedDict):
    image_path: Path
    lines: NotRequired[list[OcrLine]]
    risk: NotRequired[Risk]
    kind: NotRequired[str]
    fields: NotRequired[list[ExtractedField]]
    evidence_rejected: NotRequired[bool]
    response: NotRequired[AnalysisResult]


def _check_image(state: AnalysisState) -> dict[str, object]:
    image_path = state["image_path"]
    if not image_path.is_file() or not 0 < image_path.stat().st_size <= MAX_UPLOAD_BYTES:
        raise ValueError("Image is missing, empty, or too large.")
    try:
        with Image.open(image_path) as image:
            if (
                image.format not in FORMAT_TO_SUFFIX
                or image.width * image.height > MAX_IMAGE_PIXELS
            ):
                raise ValueError("Image has an unsupported format or dimensions.")
            image.verify()
    except (UnidentifiedImageError, Image.DecompressionBombError) as exc:
        raise ValueError("Image could not be decoded.") from exc
    return {}


def _route_after_ocr(state: AnalysisState) -> Literal["triage", "respond"]:
    return "triage" if state["lines"] else "respond"


def _triage(state: AnalysisState) -> dict[str, Risk | str]:
    text = "\n".join(line.text for line in state["lines"])
    return {"risk": classify_risk(text), "kind": classify_kind(text)}


def _route_after_triage(state: AnalysisState) -> Literal["extract", "respond"]:
    return "respond" if state["risk"] in HIGH_RISK else "extract"


def _extract(state: AnalysisState) -> dict[str, list[ExtractedField]]:
    return {"fields": extract_fields(state["lines"])}


def _validate(state: AnalysisState) -> dict[str, list[ExtractedField] | bool]:
    fields, rejected = validate_evidence(state["lines"], state["fields"])
    return {"fields": fields, "evidence_rejected": rejected}


def _respond(state: AnalysisState) -> dict[str, AnalysisResult]:
    response = compose_result(
        lines=state["lines"],
        fields=state.get("fields", []),
        risk=state.get("risk", "unreadable"),
        kind=state.get("kind", "unknown"),
        evidence_rejected=state.get("evidence_rejected", False),
    )
    return {"response": response}


def build_analysis_graph(ocr: OcrReader) -> CompiledStateGraph:
    def read_ocr(state: AnalysisState) -> dict[str, list[OcrLine]]:
        return {"lines": ocr.read(state["image_path"])}

    graph = StateGraph(AnalysisState)
    graph.add_node("check_image", _check_image)
    graph.add_node("ocr", read_ocr)
    graph.add_node("triage", _triage)
    graph.add_node("extract", _extract)
    graph.add_node("validate", _validate)
    graph.add_node("respond", _respond)
    graph.add_edge(START, "check_image")
    graph.add_edge("check_image", "ocr")
    graph.add_conditional_edges("ocr", _route_after_ocr)
    graph.add_conditional_edges("triage", _route_after_triage)
    graph.add_edge("extract", "validate")
    graph.add_edge("validate", "respond")
    graph.add_edge("respond", END)
    return graph.compile()
