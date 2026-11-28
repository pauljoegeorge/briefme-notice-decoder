from io import BytesIO
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient, Response
from langsmith import get_tracing_context
from PIL import Image

from app.main import create_app
from app.notices.dependencies import get_analyzer
from app.notices.schemas import ExtractedField
from app.notices.service import NoticeAnalyzer
from app.notices.service.compose import compose_result
from app.ocr.schemas import OcrLine


class FakeOcr:
    def __init__(self, text: str) -> None:
        self.text = text

    def read(self, image_path: Path) -> list[OcrLine]:
        assert image_path.exists()
        if not self.text:
            return []
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
async def test_high_risk_notice_uses_referral(monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected_extract(_lines: list[OcrLine]) -> list[ExtractedField]:
        pytest.fail("High-risk notices must skip extraction")

    monkeypatch.setattr("app.notices.service.graph.extract_fields", unexpected_extract)
    response = await analyze_with("裁判所からの通知 2026/11/27 電話 03-1234-5678")
    assert response.status_code == 200
    body = response.json()
    assert body["risk"] == "legal"
    assert "contact" in body["action_needed"].lower()
    assert "cannot interpret" in body["warning"].lower()
    assert body["fields"] == []


@pytest.mark.asyncio
async def test_unreadable_notice_skips_triage(monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected_triage(_text: str) -> str:
        pytest.fail("Unreadable notices must skip triage")

    monkeypatch.setattr("app.notices.service.graph.classify_kind", unexpected_triage)
    response = await analyze_with("")
    assert response.status_code == 200
    body = response.json()
    assert body["risk"] == "unreadable"
    assert body["fields"] == []
    assert "retake" in body["action_needed"].lower()


@pytest.mark.asyncio
async def test_invalid_evidence_is_omitted_with_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    invalid = ExtractedField(
        label="Date",
        value="2026/11/27",
        source_line=0,
        source_quote="a different notice",
        confidence=0.9,
    )
    monkeypatch.setattr("app.notices.service.graph.extract_fields", lambda _lines: [invalid])
    response = await analyze_with("お届け 2026/11/27")

    assert response.status_code == 200
    body = response.json()
    assert body["fields"] == []
    assert "lacked matching OCR evidence" in body["warning"]


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


def test_graph_disables_notice_tracing(tmp_path: Path) -> None:
    image_path = tmp_path / "notice.png"
    image_path.write_bytes(image_bytes())

    class TracingCheckOcr:
        def read(self, _image_path: Path) -> list[OcrLine]:
            assert get_tracing_context()["enabled"] is False
            return []

    result = NoticeAnalyzer(TracingCheckOcr()).analyze(image_path)
    assert result.risk == "unreadable"


def test_graph_rejects_invalid_image_before_ocr(tmp_path: Path) -> None:
    image_path = tmp_path / "notice.png"
    image_path.write_bytes(b"not an image")

    class UnexpectedOcr:
        def read(self, _image_path: Path) -> list[OcrLine]:
            pytest.fail("OCR must not run on an invalid image")

    with pytest.raises(ValueError, match="could not be decoded"):
        NoticeAnalyzer(UnexpectedOcr()).analyze(image_path)
