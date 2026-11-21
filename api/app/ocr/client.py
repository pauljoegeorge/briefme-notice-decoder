from functools import cached_property
from pathlib import Path
from typing import Protocol

from PIL import Image
from rapidocr import EngineType, ModelType, OCRVersion, RapidOCR

from .schemas import OcrLine


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
        with Image.open(image_path) as image:
            width, height = image.size
        result = self.engine(str(image_path))
        boxes = result.boxes if result.boxes is not None else ()
        lines: list[OcrLine] = []
        for text, score, box in zip(result.txts or (), result.scores or (), boxes, strict=True):
            xs = [float(point[0]) for point in box]
            ys = [float(point[1]) for point in box]
            left, right = min(xs), max(xs)
            top, bottom = min(ys), max(ys)
            lines.append(
                OcrLine(
                    text=text,
                    confidence=float(score),
                    x=left / width,
                    y=top / height,
                    width=(right - left) / width,
                    height=(bottom - top) / height,
                )
            )
        return lines
