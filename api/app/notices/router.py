import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.image_uploads import MAX_UPLOAD_BYTES, InvalidImage, validate_image

from .dependencies import get_analyzer
from .schemas import AnalysisResult
from .service import NoticeAnalyzer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["notice analyses"])


@router.post("/notice-analyses", summary="Analyze a notice image")
def analyze_upload(
    file: Annotated[UploadFile, File()],
    analyzer: Annotated[NoticeAnalyzer, Depends(get_analyzer)],
) -> AnalysisResult:
    data = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Image is larger than 15 MB.")
    try:
        suffix = validate_image(data, file.content_type)
    except InvalidImage as exc:
        raise HTTPException(422, str(exc)) from exc

    with TemporaryDirectory(prefix="notice-decoder-") as temporary:
        image_path = Path(temporary) / f"notice{suffix}"
        image_path.write_bytes(data)
        try:
            return analyzer.analyze(image_path)
        except (OSError, ValueError) as exc:
            logger.warning("Notice analysis failed: %s", type(exc).__name__)
            raise HTTPException(422, "The notice could not be read. Try a clearer photo.") from exc
