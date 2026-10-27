#!/usr/bin/env python3
"""Parse Block 10 Lean `#print axioms` output conservatively."""
from __future__ import annotations

import json
import re
from pathlib import Path

ALLOWED = {"propext", "Quot.sound", "Classical.choice"}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    names = (root / "results" / "theorem_names_block10.txt").read_text(encoding="utf-8").splitlines()
    text = (root / "logs" / "axiom_audit_block10.log").read_text(encoding="utf-8")
    records: list[dict[str, object]] = []
    seen: set[str] = set()

    dep = re.compile(
        r"'KomorebiPadic\.([^']+)' depends on axioms: \[([^\]]*)\]",
        re.MULTILINE | re.DOTALL,
    )
    none = re.compile(
        r"'KomorebiPadic\.([^']+)' does not depend on any axioms",
        re.MULTILINE,
    )
    for match in dep.finditer(text):
        name = match.group(1)
        axioms = [x.strip() for x in match.group(2).replace("\n", " ").split(",") if x.strip()]
        records.append({"name": name, "axioms": axioms})
        seen.add(name)
    for match in none.finditer(text):
        name = match.group(1)
        records.append({"name": name, "axioms": []})
        seen.add(name)

    index = {name: i for i, name in enumerate(names)}
    records.sort(key=lambda r: index.get(str(r["name"]), len(names)))
    observed = {a for record in records for a in record["axioms"]}
    unexpected = sorted(observed - ALLOWED)
    missing = sorted(set(names) - seen)
    extra = sorted(seen - set(names))
    counts: dict[str, int] = {}
    for record in records:
        key = str(record["name"])
        counts[key] = counts.get(key, 0) + 1
    duplicates = sorted(name for name, count in counts.items() if count > 1)
    passed = (
        not unexpected
        and not missing
        and not extra
        and not duplicates
        and len(records) == len(names)
    )
    report = {
        "schema": "komorebi-padic-block10-axiom-audit-v1",
        "status": "PASS" if passed else "FAIL",
        "theorem_count": len(names),
        "record_count": len(records),
        "allowed_axioms": sorted(ALLOWED),
        "observed_axioms": sorted(observed),
        "unexpected_axioms": unexpected,
        "missing_theorems": missing,
        "extra_theorems": extra,
        "duplicate_records": duplicates,
        "records": records,
    }
    output = root / "results" / "axiom_audit_block10.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "records"}, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
