#!/usr/bin/env python3
"""Static source and predecessor-preservation audit for Block 09."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

DECL = re.compile(r"^(?:protected\s+)?(theorem|lemma|def|structure)\s+([A-Za-z0-9_'.]+)", re.MULTILINE)
THEOREM_START = re.compile(r"^(?:protected\s+)?(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)\b")
BAD = {
    "sorry": re.compile(r"\bsorry\b"),
    "admit": re.compile(r"\badmit\b"),
    "axiom": re.compile(r"^\s*axiom\s+", re.MULTILINE),
}
LOCAL_IMPORT = re.compile(r"^import\s+(KomorebiPadic(?:\.[A-Za-z0-9_']+)?)\s*$", re.MULTILINE)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def theorem_headers(lean_root: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for path in sorted((lean_root / "KomorebiPadic").glob("*.lean")):
        lines = path.read_text(encoding="utf-8").splitlines()
        i = 0
        while i < len(lines):
            m = THEOREM_START.match(lines[i])
            if not m:
                i += 1
                continue
            name = m.group(1)
            acc = [lines[i]]
            while ":=" not in acc[-1]:
                i += 1
                if i >= len(lines):
                    raise RuntimeError(f"unterminated theorem header {name} in {path}")
                acc.append(lines[i])
            joined = "\n".join(acc).split(":=", 1)[0]
            normalized = " ".join(joined.split())
            out[name] = {
                "header": normalized,
                "file": str(path.relative_to(lean_root.parent)),
            }
            i += 1
    return out


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    predecessor = root.parent / "Block08"
    predecessor_snapshot = root / "predecessor" / "BLOCK08_THEOREM_HEADERS.json"
    lean_root = root / "lean"
    files = sorted(lean_root.rglob("*.lean"))
    modules: dict[str, Path] = {}
    for path in files:
        rel = path.relative_to(lean_root).with_suffix("")
        modules[".".join(rel.parts)] = path

    declarations: list[dict[str, str]] = []
    violations: list[dict[str, str]] = []
    missing_imports: list[dict[str, str]] = []
    imports: dict[str, list[str]] = {}
    for module, path in modules.items():
        text = path.read_text(encoding="utf-8")
        for kind, name in DECL.findall(text):
            declarations.append({"module": module, "kind": kind, "name": name})
        for label, pattern in BAD.items():
            if pattern.search(text):
                violations.append({"module": module, "kind": label})
        local = LOCAL_IMPORT.findall(text)
        imports[module] = local
        for imported in local:
            if imported not in modules:
                missing_imports.append({"module": module, "missing": imported})

    cycles: list[list[str]] = []
    visiting: list[str] = []
    visited: set[str] = set()

    def dfs(module: str) -> None:
        if module in visiting:
            i = visiting.index(module)
            cycles.append(visiting[i:] + [module])
            return
        if module in visited:
            return
        visiting.append(module)
        for dep in imports.get(module, []):
            if dep in modules:
                dfs(dep)
        visiting.pop()
        visited.add(module)

    for module in modules:
        dfs(module)

    root_imports = set(imports.get("KomorebiPadic", []))
    production_modules = {m for m in modules if m != "KomorebiPadic"}
    missing_from_root = sorted(production_modules - root_imports)
    by_kind: dict[str, int] = {}
    for decl in declarations:
        by_kind[decl["kind"]] = by_kind.get(decl["kind"], 0) + 1
    names = [d["name"] for d in declarations]
    duplicate_decls = sorted({n for n in names if names.count(n) > 1})

    if predecessor_snapshot.is_file():
        snapshot = json.loads(predecessor_snapshot.read_text(encoding="utf-8"))
        old_headers = snapshot["headers"]
        predecessor_snapshot_sha256 = sha256(predecessor_snapshot)
    elif (predecessor / "lean").is_dir():
        old_headers = theorem_headers(predecessor / "lean")
        predecessor_snapshot_sha256 = None
    else:
        raise RuntimeError("missing Block 07 theorem-header snapshot and predecessor source")
    new_headers = theorem_headers(lean_root)
    missing_predecessor_theorems = sorted(set(old_headers) - set(new_headers))
    changed_predecessor_theorems = [
        {
            "name": name,
            "predecessor": old_headers[name],
            "block09": new_headers.get(name),
        }
        for name in sorted(set(old_headers) & set(new_headers))
        if old_headers[name]["header"] != new_headers[name]["header"]
    ]
    added_theorems = sorted(set(new_headers) - set(old_headers))

    passed = not (
        violations or missing_imports or cycles or missing_from_root or duplicate_decls
        or missing_predecessor_theorems or changed_predecessor_theorems
    )
    report = {
        "schema": "komorebi-padic-block09-static-source-audit-v1",
        "status": "PASS" if passed else "FAIL",
        "lean_file_count": len(files),
        "module_count": len(modules),
        "declaration_counts": by_kind,
        "declaration_total": len(declarations),
        "placeholder_or_axiom_violations": violations,
        "missing_local_imports": missing_imports,
        "local_import_cycles": cycles,
        "missing_root_imports": missing_from_root,
        "duplicate_declarations": duplicate_decls,
        "predecessor_theorem_count": len(old_headers),
        "predecessor_snapshot_sha256": predecessor_snapshot_sha256,
        "block09_theorem_count": len(new_headers),
        "missing_predecessor_theorems": missing_predecessor_theorems,
        "changed_predecessor_theorem_statements": changed_predecessor_theorems,
        "added_theorems": added_theorems,
        "files": [
            {
                "path": str(path.relative_to(root)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in files
        ],
    }
    out = root / "results" / "static_source_audit_block09.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "files"}, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
