#!/usr/bin/env python3
"""Fail closed if the Paper I theorem map and compiled Lean API diverge."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path


LEAN_ROOT = Path(__file__).resolve().parents[1]
RELEASE_ROOT = LEAN_ROOT.parents[1]
KERNEL_AUDIT = LEAN_ROOT / "KomorebiVerification" / "KernelAudit.lean"
EXPECTED_ROWS = list(range(1, 36))


def _contract_rows(text: str) -> dict[int, list[str]]:
    rows: dict[int, list[str]] = {}
    for line in text.splitlines():
        if not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        columns = [column.strip() for column in line.split("|")[1:-1]]
        if len(columns) != 6:
            raise SystemExit(f"malformed theorem-map row: {line}")
        row_id = int(columns[0])
        if row_id in rows:
            raise SystemExit(f"duplicate contract row {row_id}")
        if columns[2] not in {"Exact", "Stronger"}:
            raise SystemExit(
                f"contract row {row_id} has unaccepted classification {columns[2]!r}"
            )
        declarations = re.findall(
            r"`((?:Komorebi|KomorebiVerification)\.[^`]+)`", columns[3]
        )
        if not declarations:
            raise SystemExit(f"contract row {row_id} has no compiled declaration")
        rows[row_id] = declarations
    return rows


def main() -> None:
    map_files = sorted(LEAN_ROOT.glob("LEAN_THEOREM_MAP_v*.md"))
    if len(map_files) != 1:
        raise SystemExit(
            f"expected exactly one versioned theorem map, found {len(map_files)}"
        )

    release = json.loads((RELEASE_ROOT / "RELEASE.json").read_text(encoding="utf-8"))
    manuscript_version = release["components"]["manuscript"]
    lean_version = release["components"]["lean_verification"]
    expected_map_name = f"LEAN_THEOREM_MAP_v{lean_version}.md"
    if map_files[0].name != expected_map_name:
        raise SystemExit(
            f"theorem-map filename {map_files[0].name!r} does not match "
            f"Lean component {lean_version!r}"
        )

    text = map_files[0].read_text(encoding="utf-8")
    required_headers = (
        f"# Lean Theorem Map v{lean_version}",
        f"Manuscript release: *Projector-Resolved Seed Calculus I*, v{manuscript_version}",
        f"Lean component: v{lean_version}",
    )
    for header in required_headers:
        if header not in text:
            raise SystemExit(f"missing or stale theorem-map header: {header}")

    rows = _contract_rows(text)
    if sorted(rows) != EXPECTED_ROWS:
        raise SystemExit(
            f"contract rows must be exactly 1..35, found {sorted(rows)}"
        )

    mapped = [name for names in rows.values() for name in names]
    duplicate_mapped = sorted(name for name, count in Counter(mapped).items() if count > 1)
    if duplicate_mapped:
        raise SystemExit(
            "mapped declarations must be unique across rows: "
            + ", ".join(duplicate_mapped)
        )
    declarations = sorted(mapped)

    audit_text = KERNEL_AUDIT.read_text(encoding="utf-8")
    audited = re.findall(r"^#print axioms\s+(\S+)\s*$", audit_text, re.MULTILINE)
    duplicate_audited = sorted(
        name for name, count in Counter(audited).items() if count > 1
    )
    if duplicate_audited:
        raise SystemExit(
            "duplicate #print axioms entries: " + ", ".join(duplicate_audited)
        )
    missing_from_audit = sorted(set(declarations) - set(audited))
    extra_in_audit = sorted(set(audited) - set(declarations))
    if missing_from_audit or extra_in_audit:
        raise SystemExit(
            "kernel audit and theorem map differ; "
            f"missing={missing_from_audit}; extra={extra_in_audit}"
        )

    lean_source = [
        "import KomorebiVerification",
        "",
        "open Lean Elab Command",
        "",
        "run_cmd do",
        "  let env ← getEnv",
        "  let contract : Array Name := #[",
    ]
    lean_source.extend(f"    `{name}," for name in declarations)
    lean_source.extend(
        [
            "  ]",
            "  for name in contract do",
            "    unless env.contains name do",
            '      throwError "missing mapped declaration: {name}"',
            '  logInfo m!"THEOREM MAP LEAN CHECK PASS: {contract.size} unique declarations"',
            "",
        ]
    )

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix="TheoremMapAudit_",
            suffix=".lean",
            dir=LEAN_ROOT,
            delete=False,
        ) as temporary:
            temporary.write("\n".join(lean_source))
            temporary_path = Path(temporary.name)

        subprocess.run(
            ["lake", "env", "lean", "-E", "warning", temporary_path.name],
            cwd=LEAN_ROOT,
            check=True,
        )
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    print(
        "THEOREM_MAP_AUDIT_PASS "
        f"rows={len(rows)} unique_compiled_declarations={len(declarations)} "
        f"direct_axiom_reports={len(audited)} map={map_files[0].name}"
    )


if __name__ == "__main__":
    main()
