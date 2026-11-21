import warnings
from io import BytesIO

from PIL import Image, UnidentifiedImageError

MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
MIME_TO_FORMAT = {"image/jpeg": "JPEG", "image/png": "PNG", "image/webp": "WEBP"}
FORMAT_TO_SUFFIX = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}


class InvalidImage(ValueError):
    pass


def validate_image(data: bytes, content_type: str | None) -> str:
    if content_type not in MIME_TO_FORMAT:
        raise InvalidImage("Upload a JPEG, PNG, or WebP image.")
    if not data:
        raise InvalidImage("Image is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise InvalidImage("Image is larger than 15 MB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as image:
                if image.format != MIME_TO_FORMAT[content_type]:
                    raise InvalidImage("File type does not match the image content.")
                if image.width * image.height > MAX_IMAGE_PIXELS:
                    raise InvalidImage("Image dimensions are too large.")
                image.verify()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise InvalidImage("The image could not be read. Try a clearer photo.") from exc
    except Image.DecompressionBombWarning as exc:
        raise InvalidImage("Image dimensions are too large.") from exc
    return FORMAT_TO_SUFFIX[MIME_TO_FORMAT[content_type]]
