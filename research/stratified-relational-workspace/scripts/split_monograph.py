#!/usr/bin/env python3
"""Verify or regenerate the modular source from the frozen monolithic snapshot."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "metadata" / "source_map.json"
ARCHIVE = ROOT / "archive" / "v1.0.0" / "Stratified_Relational_Workspace_Theory_monolithic.tex"
MONOGRAPH = ROOT / "monograph"


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def strip_header(path: Path, lines: int = 2) -> str:
    data = path.read_text(encoding="utf-8").splitlines(keepends=True)
    return "".join(data[lines:])


def segments() -> tuple[str, str, list[tuple[str, str]], str]:
    text = ARCHIVE.read_text(encoding="utf-8")
    begin = text.index(r"\begin{document}")
    part_matches = list(re.finditer(r"^\\theorypart\{([^}]+)\}\{([^}]+)\}", text, re.MULTILINE))
    first = part_matches[0].start()
    bib = text.index(r"\begin{thebibliography}{99}")
    end = text.rindex(r"\end{document}")
    preamble = text[:begin]
    front = text[begin + len(r"\begin{document}"):first].lstrip("\n").rstrip() + "\n"
    parts: list[tuple[str, str]] = []
    meta = json.loads(MAP.read_text(encoding="utf-8"))
    for index, match in enumerate(part_matches):
        stop = part_matches[index + 1].start() if index + 1 < len(part_matches) else bib
        content = text[match.start():stop].rstrip() + "\n"
        filename = Path(meta["parts"][index]["file"]).name
        parts.append((filename, content))
    refs = text[bib:end].rstrip() + "\n"
    return preamble, front, parts, refs


def check() -> None:
    meta = json.loads(MAP.read_text(encoding="utf-8"))
    if hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() != meta["source_snapshot_sha256"]:
        raise SystemExit("Frozen monolithic source hash does not match metadata/source_map.json")
    _, front, parts, refs = segments()
    errors: list[str] = []
    if strip_header(MONOGRAPH / "frontmatter.tex") != front:
        errors.append("monograph/frontmatter.tex")
    if strip_header(MONOGRAPH / "references.tex") != refs:
        errors.append("monograph/references.tex")
    for filename, expected in parts:
        if strip_header(MONOGRAPH / "parts" / filename) != expected:
            errors.append(f"monograph/parts/{filename}")
    if errors:
        raise SystemExit("Modular source differs from frozen snapshot: " + ", ".join(errors))
    print(f"source_split_check=PASS files={len(parts) + 2}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify the current modular source")
    args = parser.parse_args()
    if not args.check:
        parser.error("Regeneration is intentionally not automatic in the release repository; use --check")
    check()


if __name__ == "__main__":
    main()
