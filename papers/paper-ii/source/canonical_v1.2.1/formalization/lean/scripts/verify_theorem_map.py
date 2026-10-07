#!/usr/bin/env python3
"""Fail closed if the Paper II theorem map and compiled Lean API diverge."""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path


LEAN_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    map_files = sorted(LEAN_ROOT.glob("LEAN_THEOREM_MAP_v*.md"))
    if len(map_files) != 1:
        raise SystemExit(
            f"expected exactly one versioned theorem map, found {len(map_files)}"
        )

    text = map_files[0].read_text(encoding="utf-8")
    prefixes: dict[str, str] = {}
    for line in text.splitlines():
        match = re.fullmatch(r"\| `([A-Z]+)` \| `([^`]+)` \|", line.strip())
        if match:
            prefixes[match.group(1)] = match.group(2)

    rows: dict[int, list[str]] = {}
    for line in text.splitlines():
        if not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        columns = [column.strip() for column in line.split("|")[1:-1]]
        row_id = int(columns[0])
        declarations = re.findall(r"`([A-Z]+)\.([^`]+)`", columns[3])
        if not declarations:
            raise SystemExit(f"contract row {row_id} has no compiled declaration")
        expanded: list[str] = []
        for prefix, suffix in declarations:
            if prefix not in prefixes:
                raise SystemExit(f"contract row {row_id} uses unknown prefix {prefix}")
            expanded.append(f"{prefixes[prefix]}.{suffix}")
        if row_id in rows:
            raise SystemExit(f"duplicate contract row {row_id}")
        rows[row_id] = expanded

    expected_rows = list(range(1, 26))
    if sorted(rows) != expected_rows:
        raise SystemExit(
            f"contract rows must be exactly 1..25, found {sorted(rows)}"
        )

    declarations = sorted({name for names in rows.values() for name in names})
    lean_source = [
        "import KomorebiVerification.PaperII",
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
        f"map={map_files[0].name}"
    )


if __name__ == "__main__":
    main()
