# Notice Decoder agent rules

Read [architecture](docs/architecture.md), [engineering standards](docs/engineering-standards.md), [design system](docs/design-system.md), and [product boundaries](docs/product-boundaries.md) before changing their areas.

- Preserve the local-first FastAPI/Python and React/TypeScript architecture. Group API code by feature; keep HTTP handlers and UI components thin, with decisions in testable functions.
- Treat the notice image and OCR quotes as the only source for notice facts. Guide RAG adds context; it never overrides the notice. Keep evidence links and uncertainty visible.
- Redirect legal, immigration, medical, and threatening notices. Do not give action advice for them. Saving and reminders require explicit user confirmation.
- Validate untrusted input at the boundary. Keep errors safe for users and useful for operators. Never log notice text, images, secrets, or personal details.
- Use strict types, small files, descriptive names, and explicit dependencies. No silent exception handling, hidden I/O, or speculative abstractions.
- Run `make check` before finishing a code change. Add focused tests when behavior, safety routing, or data boundaries change.

More specific rules in `api/AGENTS.md` and `web/AGENTS.md` apply inside those directories.
