#!/usr/bin/env python3
"""Generate a complete #print axioms file for every project theorem/lemma."""
from __future__ import annotations

import re
from pathlib import Path

DECL = re.compile(r"^(?:protected\s+)?(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)", re.MULTILINE)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    names: list[str] = []
    for path in sorted((root / "lean" / "KomorebiPadic").glob("*.lean")):
        text = path.read_text(encoding="utf-8")
        names.extend(DECL.findall(text))
    if len(names) != len(set(names)):
        dupes = sorted({n for n in names if names.count(n) > 1})
        raise SystemExit(f"duplicate theorem names: {dupes}")
    out = root / "verification" / "AxiomAudit.lean"
    lines = ["import KomorebiPadic", "", "namespace KomorebiPadic", ""]
    lines.extend(f"#print axioms {name}" for name in names)
    lines.extend(["", "end KomorebiPadic", ""])
    out.write_text("\n".join(lines), encoding="utf-8")
    (root / "results" / "theorem_names.txt").write_text("\n".join(names) + "\n", encoding="utf-8")
    print(f"theorems={len(names)}")
    print(f"wrote={out}")


if __name__ == "__main__":
    main()
