from typing import cast

from fastapi import Request

from .service import NoticeAnalyzer


def get_analyzer(request: Request) -> NoticeAnalyzer:
    return cast(NoticeAnalyzer, request.app.state.analyzer)
