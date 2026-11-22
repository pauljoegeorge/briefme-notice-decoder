# Notice Decoder — local prototype

A local web app for getting a preliminary English reading of a Japanese notice while keeping the original photo in view.

## Current capabilities

- Upload or take a JPEG, PNG, or WebP photo up to 15 MB.
- Read Japanese text locally with RapidOCR. The OCR pipeline applies camera orientation, attempts perspective correction or text-angle deskew, and keeps the original reading when correction does not improve its score.
- Show a preliminary English explanation of what the notice appears to be, whether action may be needed, and its key details.
- Extract dates, amounts, and phone numbers with OCR confidence and a link to the source line highlighted on the original photo.
- Flag notices that match money, legal, immigration, medical, or threatening patterns. High-risk matches receive a referral instead of an interpretation.
- Keep processing local. Uploaded images are removed after analysis; the app does not save notices or create reminders.

## Requirements

- Python 3.11+ and `uv`
- Node.js 20+

## Run

```sh
cd api
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

In another terminal:

```sh
cd web
npm install
npm run dev
```

Open the URL printed by Vite. The browser sends images to the local API on port 8000.

Run `make check` from the project root before finishing a code change. Rules for future agents are in `AGENTS.md`, with API and web-specific rules in their directories.

## Project docs

[Implementation plan](docs/plan.md) · [Architecture](docs/architecture.md) · [FastAPI conventions](docs/fastapi-conventions.md) · [Engineering standards](docs/engineering-standards.md) · [Design system](docs/design-system.md) · [Product boundaries](docs/product-boundaries.md)

## PostgreSQL

The planned application database is PostgreSQL with pgvector. It is not required for the current reading flow because nothing is saved. `compose.yaml` provides the local database for future features.

## Current limits

- OCR quality depends on image quality. Vertical text and handwriting need dedicated evaluation.
- The summary and risk route are simple rules, not model judgments. They should not be treated as authoritative.
- Only JPEG, PNG, and WebP images up to 15 MB are accepted.
- RAG, Jev, Claude, and LangGraph are not implemented yet.
