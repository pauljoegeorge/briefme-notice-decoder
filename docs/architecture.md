# Architecture and boundaries

The app is a local-first modular monolith. `api/app/` is the FastAPI package; the web client calls it through `/api`. See the [implementation plan](plan.md) for milestones and [FastAPI conventions](fastapi-conventions.md) for package rules.

```text
main.py creates NoticeAnalyzer(RapidOcrReader) and registers the router
web → notices/router.py → notices/service/analysis.py → ocr/client.py
                              ↓
                 service/{triage,extract,compose}.py
```

`ocr/client.py` defines the OCR contract and RapidOCR implementation. The contract is a type; it is not called as a separate step.

## Reading the folders

Start at `main.py` to see how the API is assembled. In a feature package, open `router.py` for endpoints, then `service/` for the use case. Its `__init__.py` exposes the public service; `analysis.py` shows the current notice flow. `schemas.py` holds Pydantic shapes, `dependencies.py` supplies route dependencies, and `constants.py` holds named patterns. In `ocr/`, open `client.py` for the reader contract and implementation.

## Stable package layout

```text
api/
  app/
    main.py                application setup and router registration
    image_uploads.py       shared image safety validation
    ocr/
      client.py            OCR contract and implementation
      preprocess.py        EXIF orientation, page rectification, and text deskew
      schemas.py           OCR output shape
    notices/
      router.py            notice analysis endpoint
      schemas.py           notice result shapes
      dependencies.py      analyzer injection
      constants.py         notice patterns and risk categories
      service/
        analysis.py        coordinates notice analysis
        triage.py          classifies notice type and risk
        extract.py         extracts linked facts
        compose.py         builds the result
    auth/                  later: identity and sessions
    guides/                later: curated guidance and retrieval
    reminders/             later: confirmed reminders
    config.py              later: shared configuration
    database.py            later: connection and session factory
  tests/                   mirrors the app packages as they grow
  migrations/              later: reversible Alembic migrations
```

The future entries show ownership, not folders to create now. Add another top-level package for a distinct domain or reusable capability. Use the same conventional filenames inside packages and create only those needed. Cross-package imports must be explicit.

`app/ocr/` is reusable, like a focused Rails `lib/ocr`. `OcrLine` and the `OcrReader` contract live there, so another feature can use OCR without importing notices. `app/notices/service/` owns classification, extraction, evidence, and response behavior. Generic image safety validation lives in `app/image_uploads.py`; a feature can apply a stricter policy at its router.

## Planned flows

- LangGraph belongs to notice analysis and will orchestrate OCR → risk → extraction → validation → response inside `app/notices/`.
- Jev and LLM clients are reusable provider packages when introduced; notice-specific decisions remain in `app/notices/`.
- Curated-guide RAG belongs to `app/guides/`. Private notice-history retrieval stays separate, even if both use one PostgreSQL instance with pgvector.
- Auth, storage, and reminders are added after the reading flow is evaluated. A route can require auth through a package dependency without moving its business logic into auth.

The current OCR endpoint uses a synchronous route because the library blocks. Before public deployment, measure OCR memory, latency, and concurrency, then move heavy analysis to a bounded worker process with reliable job state. Image files stay outside PostgreSQL; save them only after explicit confirmation.

## Web structure

```text
web/src/
  main.tsx                         mounts BrowserRouter and the app
  app/App.tsx                      registers pages
  app/AppShell.tsx                 shared header and page layout
  pages/NoticeAnalysisPage/       page mounted at `/`
    NoticeAnalysisPage.tsx         notice page composition
    hooks/useNoticeAnalysis.ts     upload, request, preview, and selection state
    api/analyzeNotice.ts           HTTP call
    utils/parseAnalysis.ts         response validation
    types/analysis.ts              feature contracts
    components/                   notice-only UI components
    styles/                       notice-only styles
  styles/                          global tokens and base styles
```

To add a page, create a matching folder under `pages/` and register its URL path in `app/App.tsx`. Keep request state in a page hook and HTTP code in that page's API module. `app/` must stay independent of page behavior.
