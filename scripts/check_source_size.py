"""Enforce source-file size limits in the project rules."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIMITS = {".py": 180, ".ts": 180, ".tsx": 180, ".css": 200}
SKIP = {".venv", "node_modules", "dist", "__pycache__", "work"}


def main() -> int:
    violations: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in LIMITS:
            continue
        if any(part in SKIP for part in path.relative_to(ROOT).parts):
            continue
        limit = 250 if "tests" in path.parts else LIMITS[path.suffix]
        lines = len(path.read_text(encoding="utf-8").splitlines())
        if lines > limit:
            violations.append(f"{path.relative_to(ROOT)}: {lines} lines (limit {limit})")
    if violations:
        print("Source size violations:\n" + "\n".join(violations))
        return 1
    print("Source size check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
