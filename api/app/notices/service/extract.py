from app.ocr.schemas import OcrLine

from ..constants import FIELD_PATTERNS
from ..schemas import ExtractedField


def extract_fields(lines: list[OcrLine]) -> list[ExtractedField]:
    fields: list[ExtractedField] = []
    for index, line in enumerate(lines):
        for label, pattern in FIELD_PATTERNS.items():
            for match in pattern.finditer(line.text):
                fields.append(
                    ExtractedField(
                        label=label,
                        value=match.group(),
                        source_line=index,
                        source_quote=line.text,
                        confidence=round(line.confidence, 2),
                    )
                )
    return fields[:24]
