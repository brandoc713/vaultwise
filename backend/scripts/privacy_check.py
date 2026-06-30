from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


BLOCKED_SUFFIXES = {".pdf"}
BLOCKED_EXACT = {".env"}
BLOCKED_PARTS = {"local_data"}
ACCOUNT_LIKE_RE = re.compile(r"\b\d{12,19}\b")


def staged_files() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    failures: list[str] = []
    for path in staged_files():
        if path.name in BLOCKED_EXACT:
            failures.append(f"{path}: environment files must not be committed")
        if any(part in BLOCKED_PARTS for part in path.parts):
            failures.append(f"{path}: local private data must not be committed")
        if path.suffix.lower() in BLOCKED_SUFFIXES:
            failures.append(f"{path}: PDFs must not be committed")
        if path.exists() and path.is_file() and path.suffix.lower() in {".txt", ".csv", ".json", ".py", ".ts", ".tsx", ".md"}:
            content = path.read_text(encoding="utf-8", errors="ignore")
            if ACCOUNT_LIKE_RE.search(content):
                failures.append(f"{path}: contains a long account-like number")

    if failures:
        print("Privacy check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Privacy check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
