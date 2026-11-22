from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image
from rapidocr.utils.output import RapidOCROutput

from app.ocr.client import RapidOcrReader, _lines
from app.ocr.preprocess import ImageVariant, deskew_text, rectify_document


def result(text: str, confidence: float, box: list[list[float]]) -> RapidOCROutput:
    return RapidOCROutput(
        boxes=np.asarray([box], dtype=np.float32), txts=(text,), scores=(confidence,)
    )


def test_rectification_maps_back_to_original() -> None:
    pixels = np.zeros((500, 400, 3), dtype=np.uint8)
    corners = np.float32([[60, 40], [330, 65], [350, 440], [40, 420]])
    cv2.fillConvexPoly(pixels, corners.astype(np.int32), (255, 255, 255))

    variant = rectify_document(Image.fromarray(pixels))

    assert variant is not None
    width, height = variant.image.size
    rectified_corners = np.float32(
        [[[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]]]
    )
    restored = cv2.perspectiveTransform(rectified_corners, variant.to_original)[0]
    assert np.allclose(restored, corners, atol=5)


def test_deskew_requires_consistent_text_angles() -> None:
    image = Image.new("RGB", (200, 200), "white")
    boxes = np.float32(
        [
            [[20, 20], [120, 38], [118, 50], [18, 32]],
            [[25, 60], [125, 78], [123, 90], [23, 72]],
            [[30, 100], [130, 118], [128, 130], [28, 112]],
        ]
    )
    ocr = RapidOCROutput(boxes=boxes, scores=(0.9, 0.9, 0.9))

    variant = deskew_text(image, ocr)

    assert variant is not None
    rotated = cv2.perspectiveTransform(boxes[:1], np.linalg.inv(variant.to_original))[0]
    assert abs(rotated[0, 1] - rotated[1, 1]) < 1
    assert deskew_text(image, RapidOCROutput(boxes=boxes[:2], scores=(0.9, 0.9))) is None


def test_mapped_ocr_box_uses_original_coordinates() -> None:
    ocr = result("notice", 0.9, [[0, 0], [10, 0], [10, 5], [0, 5]])
    translation = np.float64([[1, 0, 20], [0, 1, 30], [0, 0, 1]])

    line = _lines(ocr, translation, (100, 100))[0]

    assert (line.x, line.y, line.width, line.height) == pytest.approx((0.2, 0.3, 0.1, 0.05))


def test_reader_prefers_better_corrected_result(monkeypatch, tmp_path: Path) -> None:
    image_path = tmp_path / "notice.png"
    Image.new("RGB", (100, 100), "white").save(image_path)
    reader = RapidOcrReader()
    weak = result("abc", 0.7, [[0, 0], [10, 0], [10, 5], [0, 5]])
    strong = result("longer notice text", 0.95, [[0, 0], [10, 0], [10, 5], [0, 5]])
    outputs = iter((weak, strong))
    reader.__dict__["engine"] = lambda _image: next(outputs)
    corrected = ImageVariant(
        Image.new("RGB", (100, 100)), np.float64([[1, 0, 20], [0, 1, 30], [0, 0, 1]])
    )
    monkeypatch.setattr("app.ocr.client.rectify_document", lambda _image: corrected)

    lines = reader.read(image_path)

    assert len(lines) == 1
    assert lines[0].text == "longer notice text"
    assert (lines[0].x, lines[0].y) == pytest.approx((0.2, 0.3))


def test_reader_keeps_original_when_correction_is_worse(monkeypatch, tmp_path: Path) -> None:
    image_path = tmp_path / "notice.png"
    Image.new("RGB", (100, 100), "white").save(image_path)
    reader = RapidOcrReader()
    strong = result("original notice text", 0.95, [[0, 0], [10, 0], [10, 5], [0, 5]])
    weak = result("abc", 0.7, [[0, 0], [10, 0], [10, 5], [0, 5]])
    outputs = iter((strong, weak))
    reader.__dict__["engine"] = lambda _image: next(outputs)
    corrected = ImageVariant(Image.new("RGB", (100, 100)), np.eye(3))
    monkeypatch.setattr("app.ocr.client.rectify_document", lambda _image: corrected)

    lines = reader.read(image_path)

    assert [line.text for line in lines] == ["original notice text"]


def test_reader_applies_exif_orientation(monkeypatch, tmp_path: Path) -> None:
    image_path = tmp_path / "notice.jpg"
    exif = Image.Exif()
    exif[274] = 6
    Image.new("RGB", (40, 20), "white").save(image_path, exif=exif)
    reader = RapidOcrReader()
    sizes: list[tuple[int, int]] = []

    def fake_engine(image: Image.Image) -> RapidOCROutput:
        sizes.append(image.size)
        return RapidOCROutput()

    reader.__dict__["engine"] = fake_engine
    monkeypatch.setattr("app.ocr.client.rectify_document", lambda _image: None)
    monkeypatch.setattr("app.ocr.client.deskew_text", lambda _image, _result: None)

    assert reader.read(image_path) == []
    assert sizes == [(20, 40)]
