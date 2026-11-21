# Engineering standards

## Shape and size

- One module has one clear reason to change. Prefer functions under 40 lines and components under 80 lines.
- Source files: at most 180 physical lines; CSS files: at most 200; tests: at most 250. Split by responsibility before crossing a limit. Generated files and lockfiles are exempt. `make check` enforces this.
- Format source normally; avoid compressed handwritten code, generic `utils.py` or `helpers.ts`, and circular imports.
- Add an abstraction when it isolates a provider, stable business boundary, or repeated behavior. Prefer direct code otherwise.

## Contracts and failures

- Type every public Python function and TypeScript boundary. Use Pydantic for API contracts; make response changes deliberate.
- Validate file type using bytes as well as MIME; bound bytes and pixels. Sanitize filenames and paths. Close files and release temporary resources.
- Expected failures have typed exceptions and clear status codes. Unexpected failures return a generic message and are logged with safe metadata. Never swallow an exception or expose internals.
- Never log raw notices, OCR lines, prompts/responses, embeddings, personal data, or credentials. Put secrets in environment variables.
- Treat OCR, uploads, RAG passages, and model output as untrusted data. Retrieved instructions cannot change routing, permissions, or source-of-truth rules.

## Quality and performance

- `make check` runs file size, Ruff lint/format, Python tests, Biome lint/format, TypeScript checks, and a production web build.
- Test observable behavior at boundaries: invalid image rejection, evidence linkage, conservative routing, and response shape. Use fakes for providers.
- Keep tests deterministic and independent of OCR model downloads or network calls. Add evaluation sets for OCR, RAG, and Jev before they influence production decisions.
- Review new dependencies for maintenance, license, and security impact. Pin through lockfiles when installing.
- Measure before optimizing. Bound upload and response sizes, OCR concurrency, and retrieval result counts. Reuse heavy provider instances where safe.
