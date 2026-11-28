from app.ocr.schemas import OcrLine

from ..schemas import ExtractedField


def validate_evidence(
    lines: list[OcrLine], fields: list[ExtractedField]
) -> tuple[list[ExtractedField], bool]:
    """Keep only fields whose value and quote occur on the cited OCR line."""
    valid: list[ExtractedField] = []
    for field in fields:
        if field.source_line >= len(lines):
            continue
        line = lines[field.source_line]
        if field.source_quote in line.text and field.value in field.source_quote:
            valid.append(field)
    return valid, len(valid) != len(fields)
