#!/usr/bin/env python3
"""
Export all Python (.py, .pyi), TOML (.toml), and Markdown (.md) files
from a directory tree into a single text file named mapper.txt.

Usage:
  python export_mapper.py [ROOT] [OUTPUT]

Defaults:
  ROOT   = current working directory
  OUTPUT = mapper.txt
"""
from __future__ import annotations
import sys
from pathlib import Path

# Extensions to include
ALLOW_EXT = {".py", ".pyi", ".toml", ".md"}

# Common directories to skip
EXCLUDE_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__",
    "dist", "build", ".mypy_cache", ".pytest_cache", ".tox", ".idea",
    ".eggs", ".ruff_cache", ".pytype", ".coverage"
}

def is_excluded(path: Path) -> bool:
    parts = path.parts
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
        if part.endswith(".egg-info"):
            return True
    return False

def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("mapper.txt")

    if not root.exists():
        print(f"Root path does not exist: {root}")
        sys.exit(1)

    # Collect candidate files
    candidates = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if is_excluded(p):
            continue
        if p.suffix.lower() in ALLOW_EXT:
            candidates.append(p)

    # Sort for stable, readable output (by relative POSIX path)
    candidates.sort(key=lambda p: p.relative_to(root).as_posix())

    # Write output with file headers
    with out_path.open("w", encoding="utf-8", newline="\n") as out:
        for p in candidates:
            rel = p.relative_to(root).as_posix()
            out.write(f"\n\n===== FILE: {rel} =====\n")
            try:
                out.write(p.read_text(encoding="utf-8", errors="ignore"))
            except Exception as e:
                out.write(f"<<Skipped unreadable file: {e}>>")

    print(f"Wrote {len(candidates)} files to {out_path}")

if __name__ == "__main__":
    main()
