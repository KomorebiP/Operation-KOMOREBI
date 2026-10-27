#!/usr/bin/env python3
"""Conservative, source-only checks of the actual monograph input closure.

This is not a TeX interpreter or a proof checker. It recognizes this project's
literal inputs and plate/source macros; the LaTeX build remains authoritative.
Historical guide documents are deliberately outside the monograph ref graph.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re


COMMAND = re.compile(r"\\([A-Za-z@]+|.)", re.S)
REFS = {"ref", "eqref", "pageref", "autoref", "cref", "Cref", "nameref"}


def uncomment(s):
    # Tokenize control sequences: escaped percent and escaped backslash differ.
    out, i = [], 0
    while i < len(s):
        if s[i] == "\\":
            m = COMMAND.match(s, i)
            out.append(m.group()); i = m.end()
        elif s[i] == "%":
            j = s.find("\n", i)
            if j < 0:
                out.append(" " * (len(s) - i)); break
            out.append(" " * (j - i)); i = j
        else:
            out.append(s[i]); i += 1
    return "".join(out)


def arg(s, start, opening="{", closing="}"):
    i = start
    while i < len(s) and s[i].isspace(): i += 1
    if i >= len(s) or s[i] != opening: return None, start
    depth, j = 1, i + 1
    while j < len(s):
        if s[j] == "\\":
            j = COMMAND.match(s, j).end(); continue
        if s[j] == opening: depth += 1
        elif s[j] == closing:
            depth -= 1
            if depth == 0: return s[i + 1:j], j + 1
        j += 1
    return None, start


def args(s, start, count=1, optional=False):
    i = start
    if optional:
        while True:
            v, j = arg(s, i, "[", "]")
            if v is None: break
            i = j
    values = []
    for _ in range(count):
        v, i = arg(s, i)
        if v is None: return None
        values.append(v)
    return values


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1] / "source")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "reviews/STRUCTURAL_CHECK.json")
    opt = parser.parse_args()
    root = opt.source.resolve()
    issues, graph, plates, assets = [], [], [], {}
    visited, occurrences, texts, checked_hashes = set(), [], {}, {}
    labels, targets, bibs = defaultdict(list), defaultdict(list), defaultdict(list)
    refs, links, cites = [], [], []

    def loc(p, s, pos): return {"file": str(p.relative_to(root)), "line": s.count("\n", 0, pos) + 1}
    def issue(kind, where, **details): issues.append({"kind": kind, **where, **details})
    def resolve(name, suffix=".tex"):
        p = root / name
        return p if p.suffix else p.with_suffix(suffix)
    def add(table, key, where):
        if "#" not in key: table[key].append(where)

    def structural(p, s):
        braces, envs, math = [], [], None
        i = 0
        while i < len(s):
            where = loc(p, s, i)
            if s[i] == "\\":
                m = COMMAND.match(s, i); cmd = m.group(1); i = m.end()
                if cmd in {"begin", "end"}:
                    a = args(s, i)
                    if a:
                        name = a[0]
                        if cmd == "begin": envs.append((name, where))
                        elif not envs or envs[-1][0] != name:
                            issue("environment_mismatch", where, closing=name, open_environment=envs[-1][0] if envs else None)
                        else: envs.pop()
                elif cmd in {"(", "["}:
                    if math is not None: issue("nested_math_delimiter", where, delimiter=cmd)
                    else: math = (cmd, where)
                elif cmd in {")", "]"}:
                    if math is None or math[0] != {")": "(", "]": "["}[cmd]:
                        issue("math_delimiter_mismatch", where, delimiter=cmd)
                    else: math = None
                continue
            if s[i] == "{": braces.append(where)
            elif s[i] == "}":
                if braces: braces.pop()
                else: issue("unmatched_closing_brace", where)
            elif s[i] == "$":
                token = "$$" if s[i:i + 2] == "$$" else "$"
                if math is None: math = (token, where)
                elif math[0] == token: math = None
                else: issue("math_delimiter_mismatch", where, delimiter=token)
                i += len(token); continue
            i += 1
        for where in braces: issue("unclosed_brace", where)
        for name, where in envs: issue("unclosed_environment", where, environment=name)
        if math: issue("unclosed_math_delimiter", math[1], delimiter=math[0])

    def walk(p, stack=()):
        if p in stack:
            issue("input_cycle", {"file": str(p.relative_to(root))}); return
        if not p.is_file():
            issue("missing_input", {"file": str(p.relative_to(root))}); return
        # All actual occurrences are checked for duplicate labels; each file is
        # structurally checked and hashed once. Repeated input is not hidden.
        occurrences.append(str(p.relative_to(root)))
        raw = p.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if p in checked_hashes and checked_hashes[p] != digest:
            issue("source_changed_during_check", {"file": str(p.relative_to(root))})
        checked_hashes[p] = digest
        s = uncomment(raw.decode())
        if p not in visited:
            visited.add(p); texts[p] = s; structural(p, s)
        for m in COMMAND.finditer(s):
            cmd, where = m.group(1), loc(p, s, m.start())
            if cmd in {"input", "include"}:
                a = args(s, m.end())
                if a and "#" not in a[0]:
                    q = resolve(a[0]); graph.append({**where, "kind": cmd, "target": str(q.relative_to(root))}); walk(q, (*stack, p))
            elif cmd in {"usepackage", "RequirePackage"}:
                a = args(s, m.end(), optional=True)
                if a:
                    for name in a[0].split(","):
                        q = resolve(name.strip(), ".sty")
                        if q.is_file():
                            graph.append({**where, "kind": "local_package", "target": str(q.relative_to(root))}); walk(q, (*stack, p))
            elif cmd in {"plate", "fixedplate"}:
                a = args(s, m.end(), 3)
                if a and not any("#" in v for v in a):
                    q = resolve("figures/" + a[0])
                    plates.append({**where, "figure": str(q.relative_to(root)), "caption": a[1], "label": a[2]})
                    add(labels, a[2], where)
                    graph.append({**where, "kind": cmd, "target": str(q.relative_to(root))}); walk(q, (*stack, p))
            elif cmd == "source":
                a = args(s, m.end())
                if a and "#" not in a[0]:
                    add(labels, "src:" + a[0], where); links.append(("claim:" + a[0], where))
            elif cmd in {"label", "hypertarget", "bibitem"}:
                a = args(s, m.end(), optional=(cmd == "bibitem"))
                if a: add({"label": labels, "hypertarget": targets, "bibitem": bibs}[cmd], a[0], where)
            elif cmd in REFS or cmd in {"hyperlink", "cite", "citep", "citet", "nocite"}:
                a = args(s, m.end(), optional=True)
                if a and "#" not in a[0]:
                    dest = refs if cmd in REFS else links if cmd == "hyperlink" else cites
                    for key in a[0].split(","):
                        if key.strip() != "*": dest.append((key.strip(), where))
            elif cmd == "hyperref":
                key, _ = arg(s, m.end(), "[", "]")
                if key and "#" not in key: refs.append((key, where))
            elif cmd == "includegraphics":
                a = args(s, m.end(), optional=True)
                if a and "#" not in a[0]:
                    q = resolve(a[0], ".pdf")
                    if not q.is_file(): issue("missing_graphic", where, target=a[0])
                    else: assets[str(q.relative_to(root))] = sha(q)

    walk(root / "Komorebi_Space_Monograph.tex")
    for kind, items, definitions in [("unresolved_reference", refs, labels), ("unresolved_hyperlink", links, targets), ("unresolved_citation", cites, bibs)]:
        for key, where in items:
            if key not in definitions: issue(kind, where, key=key)
    for kind, table in [("duplicate_label", labels), ("duplicate_hypertarget", targets), ("duplicate_bibitem", bibs)]:
        for key, locations in table.items():
            if len(locations) > 1: issues.append({"kind": kind, "key": key, "locations": locations})

    # Check the complete figure source inventory without polluting the monograph
    # reference namespace with the separate, inherited guide documents.
    all_figures = sorted((root / "figures").glob("*.tex"))
    extra_figures = [p for p in all_figures if p not in visited]
    for p in extra_figures:
        raw = p.read_bytes()
        checked_hashes[p] = hashlib.sha256(raw).hexdigest()
        structural(p, uncomment(raw.decode()))
    for p, digest in checked_hashes.items():
        if sha(p) != digest:
            issue("source_changed_during_check", {"file": str(p.relative_to(root))})
    for name, digest in assets.items():
        if sha(root / name) != digest:
            issue("graphic_changed_during_check", {"file": name})
    result = {
        "schema": "komorebi-manuscript-structure-v1", "status": "PASS" if not issues else "FAIL",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "entrypoint": "Komorebi_Space_Monograph.tex",
        "scope": "Recursive literal input/local-package closure, with project plate and source macro recognition; historical guides excluded from reference graph.",
        "limitations": ["Static lexical checking is not a TeX interpreter, mathematical proof audit, numerical rerun, or PDF visual inspection.", "Per-file braces, explicit math delimiters, and environment nesting are checked; general macro expansion and TeX conditional execution are not modeled.", "Figure-only guide sources are structurally checked separately; their guide captions receive manual review."],
        "counts": {"closure_files": len(visited), "input_occurrences": len(occurrences), "monograph_plates": len(plates), "all_figure_sources": len(all_figures), "labels": len(labels), "reference_occurrences": len(refs), "hypertargets": len(targets), "hyperlink_occurrences": len(links), "bibliography_keys": len(bibs), "citation_occurrences": len(cites), "graphic_assets": len(assets), "issues": len(issues)},
        "input_graph": graph, "input_occurrences": occurrences,
        "source_sha256": {str(p.relative_to(root)): checked_hashes[p] for p in sorted(visited)},
        "all_figure_source_sha256": {str(p.relative_to(root)): checked_hashes[p] for p in all_figures},
        "figure_sources_outside_monograph": [str(p.relative_to(root)) for p in extra_figures],
        "graphic_sha256": assets, "plates": plates, "issues": issues,
        "checker_sha256": sha(Path(__file__)),
    }
    opt.output.parent.mkdir(parents=True, exist_ok=True)
    opt.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": result["status"], "counts": result["counts"], "issues": issues, "output": str(opt.output)}, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
