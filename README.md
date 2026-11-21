# Notice Decoder — local prototype

This prototype covers the first three milestones: local app setup, upload-to-result flow, and OCR evidence on the original image. It uses local RapidOCR with Japanese recognition and rule-based triage. RAG, Jev, Claude, and LangGraph are the next phase.

Project decisions and next steps: [implementation plan](docs/plan.md) · [architecture](docs/architecture.md) · [FastAPI conventions](docs/fastapi-conventions.md) · [engineering standards](docs/engineering-standards.md) · [design system](docs/design-system.md) · [product boundaries](docs/product-boundaries.md).

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

Open the URL printed by Vite. The browser sends images to the local API. Uploaded files are deleted after OCR; the prototype does not save notices or create reminders. The Japanese OCR model downloads on the first use, then runs locally.

Run `make check` from the project root before finishing a code change. Rules for future agents are in `AGENTS.md`, with API and web-specific rules in their directories.

## PostgreSQL

The planned application database is PostgreSQL with pgvector. It is not required for these first three milestones because nothing is saved before confirmation. `compose.yaml` provides the local database for the next phase.

## Current limits

- OCR quality depends on image quality. Vertical text and handwriting need dedicated evaluation.
- The summary and risk route are simple rules, not model judgments. They should not be treated as authoritative.
- Only JPEG, PNG, and WebP images up to 15 MB are accepted.
