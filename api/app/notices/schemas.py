from typing import Literal

from pydantic import BaseModel, Field

from app.ocr.schemas import OcrLine

Risk = Literal["routine", "money", "legal", "immigration", "medical", "threatening", "unreadable"]
FieldLabel = Literal["Date", "Amount", "Phone"]


class ExtractedField(BaseModel):
    label: FieldLabel
    value: str
    source_line: int = Field(ge=0)
    source_quote: str
    confidence: float = Field(ge=0, le=1)


class AnalysisResult(BaseModel):
    risk: Risk
    kind: str
    lines: list[OcrLine]
    fields: list[ExtractedField]
    what_happened: str
    action_needed: str
    key_details: str
    warning: str
