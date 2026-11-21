from fastapi import FastAPI

from app.notices.router import router as notices_router
from app.notices.service import NoticeAnalyzer
from app.ocr.client import RapidOcrReader


def create_app() -> FastAPI:
    app = FastAPI(title="Notice Decoder API", version="0.1.0")
    app.state.analyzer = NoticeAnalyzer(RapidOcrReader())
    app.include_router(notices_router)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
