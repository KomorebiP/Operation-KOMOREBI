#!/usr/bin/env python3
"""Generate #print axioms commands for every Block 10 project theorem/lemma.

Unlike the older generator, this parser accepts declaration attributes such as
`@[simp] theorem ...` on the same line.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

DECL = re.compile(
    r"^\s*(?:@\[[^\n\]]+\]\s*)*(?:protected\s+)?(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)",
    re.MULTILINE,
)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source_files = sorted((root / "lean" / "KomorebiPadic").glob("*.lean"))
    names: list[str] = []
    records: list[dict[str, str]] = []
    for path in source_files:
        text = path.read_text(encoding="utf-8")
        for match in DECL.finditer(text):
            name = match.group(1)
            line = text.count("\n", 0, match.start()) + 1
            names.append(name)
            records.append({"name": name, "file": str(path.relative_to(root)), "line": str(line)})
    duplicates = sorted({n for n in names if names.count(n) > 1})
    if duplicates:
        raise SystemExit(f"duplicate theorem names: {duplicates}")
    if not names:
        raise SystemExit("no theorem declarations found")

    out = root / "verification" / "AxiomAuditBlock10.lean"
    lines = ["import KomorebiPadic", "", "namespace KomorebiPadic", ""]
    lines.extend(f"#print axioms {name}" for name in names)
    lines.extend(["", "end KomorebiPadic", ""])
    out.write_text("\n".join(lines), encoding="utf-8")

    results = root / "results"
    results.mkdir(exist_ok=True)
    (results / "theorem_names_block10.txt").write_text("\n".join(names) + "\n", encoding="utf-8")
    (results / "theorem_locations_block10.json").write_text(
        json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"theorems={len(names)}")
    print(f"wrote={out}")


if __name__ == "__main__":
    main()
