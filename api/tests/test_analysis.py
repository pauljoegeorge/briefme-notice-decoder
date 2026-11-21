from io import BytesIO
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient, Response
from PIL import Image

from app.main import create_app
from app.notices.dependencies import get_analyzer
from app.notices.service import NoticeAnalyzer
from app.notices.service.compose import compose_result
from app.ocr.schemas import OcrLine


class FakeOcr:
    def __init__(self, text: str) -> None:
        self.text = text

    def read(self, image_path: Path) -> list[OcrLine]:
        assert image_path.exists()
        return [OcrLine(text=self.text, confidence=0.95, x=0.1, y=0.2, width=0.7, height=0.1)]


def image_bytes() -> bytes:
    output = BytesIO()
    Image.new("RGB", (100, 100), "white").save(output, format="PNG")
    return output.getvalue()


async def analyze_with(text: str, content_type: str = "image/png") -> Response:
    app = create_app()
    app.dependency_overrides[get_analyzer] = lambda: NoticeAnalyzer(FakeOcr(text))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        return await client.post(
            "/api/notice-analyses",
            files={"file": ("notice.png", image_bytes(), content_type)},
        )


@pytest.mark.asyncio
async def test_extracted_fields_link_to_ocr_evidence() -> None:
    response = await analyze_with("お届け 2026/11/22 電話 03-1234-5678")
    assert response.status_code == 200
    body = response.json()
    assert body["risk"] == "routine"
    assert body["fields"]
    assert all(field["source_line"] == 0 for field in body["fields"])
    assert all(field["source_quote"] == body["lines"][0]["text"] for field in body["fields"])


@pytest.mark.asyncio
async def test_high_risk_notice_uses_referral() -> None:
    response = await analyze_with("裁判所からの通知")
    assert response.status_code == 200
    body = response.json()
    assert body["risk"] == "legal"
    assert "contact" in body["action_needed"].lower()
    assert "cannot interpret" in body["warning"].lower()


@pytest.mark.asyncio
async def test_rejects_mismatched_mime_type() -> None:
    response = await analyze_with("notice", "image/jpeg")
    assert response.status_code == 422
    assert "does not match" in response.json()["detail"]


def test_low_confidence_keeps_high_risk_warning() -> None:
    line = OcrLine(text="裁判所", confidence=0.3, x=0.1, y=0.2, width=0.3, height=0.1)
    result = compose_result(lines=[line], fields=[], risk="legal", kind="notice")
    assert "cannot interpret" in result.warning
    assert "confidence is low" in result.warning
