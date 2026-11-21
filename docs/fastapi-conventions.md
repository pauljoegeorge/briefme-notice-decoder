# FastAPI conventions for this repository

Source: the community-maintained [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices), especially [Project Structure](https://github.com/zhanymkanov/fastapi-best-practices#project-structure) and its [agent rules](https://github.com/zhanymkanov/fastapi-best-practices/blob/master/AGENTS.md). This local file records how we apply that guide to Notice Decoder. Recheck the source when changing an API area.

## Package ownership

`api/app/` plays the guide's `src/` role. Put each domain or reusable capability in a top-level package: `notices/`, `ocr/`, later `auth/`, `guides/`, and `reminders/`. Shared modules such as `image_uploads.py`, future `config.py`, and future `database.py` live at the app root. Add a package or file when its responsibility exists; do not create placeholders.

Within a package, use `router.py` for endpoints, `schemas.py` for Pydantic contracts, `models.py` for database models, `dependencies.py` for FastAPI dependencies, `constants.py` for patterns/error codes, `config.py` for package settings, `exceptions.py` for typed failures, and `utils.py` only for non-business helpers. Provider packages use `client.py`. Keep cross-package imports explicit; never use wildcard imports.

Product features use a `service/` package for business logic, with a small `__init__.py` exposing the feature's public service. This is our project-specific extension of the guide's `service.py` example, chosen so the feature root stays predictable while workflows grow. Never have a peer `service.py`. In this project, `notices/service/analysis.py` coordinates OCR and the other service modules; `triage.py`, `extract.py`, and `compose.py` own separate steps inside that package. Their regex tables live in `notices/constants.py`. Do not create empty placeholders.

## Request and provider rules

- Use `Annotated[T, Depends(...)]` for dependencies. Keep route handlers focused on HTTP validation and error translation; use typed exceptions for expected failures.
- Use `async def` for nonblocking I/O and `def` for blocking libraries. Never call blocking I/O directly in an async route. Heavy OCR needs measured concurrency limits and a worker process before public deployment.
- Use Pydantic validation at API boundaries. Avoid specifying the same Pydantic model both as return type and `response_model`.
- Keep OCR, model, Jev, retrieval, and calendar provider code outside notice-specific rules. `app/ocr/` owns the OCR contract and implementations; `app/notices/` owns how OCR evidence affects a notice.
- Use reliable workers for heavy or retried jobs; FastAPI `BackgroundTasks` is only for small, disposable work. Do not add a queue until a workflow needs one.
- When auth is introduced, use router dependencies for access control and PyJWT if JWT is chosen. Keep secrets in environment-backed settings. Expose OpenAPI docs only in chosen environments.

## Persistence and tests

- When PostgreSQL is introduced, use SQLAlchemy 2 async sessions and reversible Alembic migrations. Keep database models separate from Pydantic schemas. Use consistent singular `snake_case` tables, `_at`/`_date` column suffixes, foreign-key names, and explicit index naming; push joins and aggregation into SQL.
- Test routes with `httpx.AsyncClient` and `ASGITransport`; override FastAPI dependencies for external providers. Use a real test database for persistence integration tests when database code exists.
- Run Ruff and `make check`. Do not introduce auth, database, or cloud dependencies before those features are implemented.
