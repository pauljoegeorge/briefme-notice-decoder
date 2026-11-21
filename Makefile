.PHONY: check

check:
	python3 scripts/check_source_size.py
	cd api && uv run ruff check app tests && uv run ruff format --check app tests && uv run python -m pytest -q
	cd web && npm run check
