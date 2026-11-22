from functools import cached_property
from pathlib import Path
from typing import Protocol

import cv2
import numpy as np
from PIL import Image, ImageOps
from rapidocr import EngineType, ModelType, OCRVersion, RapidOCR
from rapidocr.utils.output import RapidOCROutput

from .preprocess import ImageVariant, deskew_text, rectify_document
from .schemas import OcrLine

CORRECTED_QUALITY_GAIN = 1.12
CORRECTED_QUALITY_MARGIN = 2.0


class OcrReader(Protocol):
    def read(self, image_path: Path) -> list[OcrLine]: ...


class RapidOcrReader:
    @cached_property
    def engine(self) -> RapidOCR:
        return RapidOCR(
            params={
                "Rec.engine_type": EngineType.ONNXRUNTIME,
                "Rec.lang_type": "japan",
                "Rec.model_type": ModelType.MOBILE,
                "Rec.ocr_version": OCRVersion.PPOCRV4,
            }
        )

    def read(self, image_path: Path) -> list[OcrLine]:
        with Image.open(image_path) as uploaded:
            # Use the same upright orientation that the browser shows for the original photo.
            original = ImageOps.exif_transpose(uploaded).convert("RGB")
        result: RapidOCROutput = self.engine(original)
        # A reliable page outline gives perspective correction; otherwise use OCR line angles.
        corrected = rectify_document(original) or deskew_text(original, result)
        # Identity mapping means OCR boxes already refer to the original photo.
        variant = ImageVariant(original, np.eye(3))
        if corrected is not None:
            corrected_result: RapidOCROutput = self.engine(corrected.image)
            # A correction can remove text, so use it only after a clear score improvement.
            if _quality(corrected_result) > (
                _quality(result) * CORRECTED_QUALITY_GAIN + CORRECTED_QUALITY_MARGIN
            ):
                variant, result = corrected, corrected_result
        return _lines(result, variant.to_original, original.size)


def _quality(result: RapidOCROutput) -> float:
    """Compare recognized text coverage; this is not a measure of factual correctness."""
    return sum(
        min(len(text.strip()), 60) * float(score)
        for text, score in zip(result.txts or (), result.scores or (), strict=True)
        if score >= 0.6
    )


def _lines(result: RapidOCROutput, to_original: np.ndarray, size: tuple[int, int]) -> list[OcrLine]:
    """Map OCR boxes to the original photo and express them as 0–1 UI coordinates."""
    width, height = size
    boxes = result.boxes if result.boxes is not None else ()
    lines: list[OcrLine] = []
    for text, score, box in zip(result.txts or (), result.scores or (), boxes, strict=True):
        # Transform all four corners before taking the enclosing box for the current UI.
        corners = cv2.perspectiveTransform(
            np.asarray(box, dtype=np.float32).reshape(1, 4, 2), to_original
        )[0]
        left, right = np.clip((corners[:, 0].min(), corners[:, 0].max()), 0, width)
        top, bottom = np.clip((corners[:, 1].min(), corners[:, 1].max()), 0, height)
        if right <= left or bottom <= top:
            continue
        lines.append(
            OcrLine(
                text=text,
                confidence=float(score),
                x=float(left / width),
                y=float(top / height),
                width=float((right - left) / width),
                height=float((bottom - top) / height),
            )
        )
    return lines
