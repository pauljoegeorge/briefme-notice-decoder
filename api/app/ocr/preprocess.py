"""Conservative document geometry for OCR image variants."""

from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image
from rapidocr.utils.output import RapidOCROutput


@dataclass(frozen=True)
class ImageVariant:
    """Corrected OCR image plus the transform back to the upright uploaded photo."""

    image: Image.Image
    to_original: np.ndarray


def _ordered_corners(points: np.ndarray) -> np.ndarray:
    """Order the detected corners top-left, top-right, bottom-right, bottom-left."""
    center = points.mean(axis=0)
    angles = np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0])
    ordered = points[np.argsort(angles)]
    return np.roll(ordered, -np.argmin(ordered.sum(axis=1)), axis=0).astype(np.float32)


def rectify_document(image: Image.Image) -> ImageVariant | None:
    """Return a crop only when a substantial, convex four-corner page is visible."""
    rgb = np.asarray(image.convert("RGB"))
    height, width = rgb.shape[:2]
    # Cap contour-search work on large photos; use full-resolution pixels for the crop.
    scale = min(1.0, 1600 / max(width, height))
    sample = cv2.resize(rgb, None, fx=scale, fy=scale) if scale < 1 else rgb
    gray = cv2.cvtColor(sample, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    area = sample.shape[0] * sample.shape[1]
    for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:20]:
        polygon = cv2.approxPolyDP(contour, 0.025 * cv2.arcLength(contour, True), True)
        if len(polygon) != 4 or not cv2.isContourConvex(polygon):
            continue
        fraction = cv2.contourArea(polygon) / area
        # Reject tiny labels and near-full-frame edges masquerading as the document.
        if not 0.18 <= fraction <= 0.95:
            continue
        corners = _ordered_corners(polygon.reshape(4, 2) / scale)
        top, right, bottom, left = (
            np.linalg.norm(corners[1] - corners[0]),
            np.linalg.norm(corners[2] - corners[1]),
            np.linalg.norm(corners[2] - corners[3]),
            np.linalg.norm(corners[3] - corners[0]),
        )
        out_width, out_height = int(max(top, bottom)), int(max(left, right))
        if min(out_width, out_height) < 100 or out_width * out_height > width * height * 2:
            continue
        target = np.float32(
            [[0, 0], [out_width - 1, 0], [out_width - 1, out_height - 1], [0, out_height - 1]]
        )
        transform = cv2.getPerspectiveTransform(corners, target)
        corrected = cv2.warpPerspective(rgb, transform, (out_width, out_height))
        # OCR runs on the crop; its boxes need the inverse map for original-photo highlights.
        return ImageVariant(Image.fromarray(corrected), np.linalg.inv(transform))
    return None


def deskew_text(image: Image.Image, result: RapidOCROutput) -> ImageVariant | None:
    """Use the OCR line angles when a page outline cannot be found."""
    if result.boxes is None or result.scores is None:
        return None
    angles: list[float] = []
    for box, score in zip(result.boxes, result.scores, strict=True):
        edge = np.asarray(box[1], dtype=float) - np.asarray(box[0], dtype=float)
        if score >= 0.6 and np.linalg.norm(edge) >= 30:
            angles.append(float(np.degrees(np.arctan2(edge[1], edge[0]))))
    if len(angles) < 3:
        return None
    # Median resists a stray text line; disagreement or extreme tilt makes rotation unsafe.
    angle = float(np.median(angles))
    if not 3 <= abs(angle) <= 30 or np.median(np.abs(np.asarray(angles) - angle)) > 7:
        return None
    width, height = image.size
    rotation = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)
    # Expand the canvas so rotation does not cut off the notice edges.
    cosine, sine = abs(rotation[0, 0]), abs(rotation[0, 1])
    out_width, out_height = int(height * sine + width * cosine), int(height * cosine + width * sine)
    rotation[0, 2] += (out_width - width) / 2
    rotation[1, 2] += (out_height - height) / 2
    corrected = cv2.warpAffine(np.asarray(image.convert("RGB")), rotation, (out_width, out_height))
    transform = np.vstack((rotation, [0, 0, 1]))
    return ImageVariant(Image.fromarray(corrected), np.linalg.inv(transform))
