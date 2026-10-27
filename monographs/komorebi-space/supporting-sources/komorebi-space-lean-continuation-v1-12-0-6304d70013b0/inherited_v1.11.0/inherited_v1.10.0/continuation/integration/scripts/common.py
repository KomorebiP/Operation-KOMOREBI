"""Small, dependency-free source inventory helpers. These do not check proofs."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT_MODULE = "KomorebiSpaceCombined"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
EXPECTED_ARCHIVE = "914bb768686bc186d4baefd53c1e13690346b0f506560ede916d1fb87d7e6794"
FORBIDDEN = re.compile(r"\b(?:sorry|admit|axiom|native_decide|unsafe)\b")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def strip_comments(text: str) -> str:
    """Replace nested Lean comments with spaces while preserving strings/lines."""
    out, i, depth, in_string = [], 0, 0, False
    while i < len(text):
        pair = text[i:i + 2]
        if depth:
            if pair == "/-":
                depth += 1
                out.extend("  ")
                i += 2
            elif pair == "-/":
                depth -= 1
                out.extend("  ")
                i += 2
            else:
                out.append("\n" if text[i] == "\n" else " ")
                i += 1
        elif in_string:
            out.append(text[i])
            if text[i] == "\\" and i + 1 < len(text):
                i += 1
                out.append(text[i])
            elif text[i] == '"':
                in_string = False
            i += 1
        elif pair == "/-":
            depth = 1
            out.extend("  ")
            i += 2
        elif pair == "--":
            end = text.find("\n", i)
            if end == -1:
                end = len(text)
            out.extend(" " * (end - i))
            i = end
        else:
            in_string = text[i] == '"'
            out.append(text[i])
            i += 1
    if depth or in_string:
        raise ValueError("Unterminated comment or string in source")
    return "".join(out)


def graph(project: Path) -> dict:
    files = sorted((project / "KomorebiSpace").rglob("*.lean"))
    files += sorted(project.glob("KomorebiSpace*.lean"))
    mods = {".".join(p.relative_to(project).with_suffix("").parts): p for p in files}
    if ROOT_MODULE not in mods:
        raise ValueError("Missing combined root")
    imports, scans = {}, []
    for mod, path in sorted(mods.items()):
        text = strip_comments(path.read_text())
        bad = FORBIDDEN.findall(text)
        if bad:
            raise ValueError(f"Forbidden production tokens in {mod}: {bad}")
        local, external = [], []
        for line in text.splitlines():
            if re.match(r"^\s*import\s+", line):
                for dep in line.strip().split()[1:]:
                    (local if dep.startswith("KomorebiSpace") else external).append(dep)
        local = sorted(set(local))
        if set(local) - mods.keys():
            raise ValueError(f"Missing local imports in {mod}: {set(local) - mods.keys()}")
        imports[mod] = local
        scans.append({"module": mod, "sha256": sha(path), "local_imports": local,
                      "external_imports": sorted(set(external)), "forbidden_tokens": bad,
                      "explicit_theorem_lemma_count": len(re.findall(r"\b(?:theorem|lemma)\s+[\w'.]+", text))})
    order, active, done = [], set(), set()

    def visit(mod: str) -> None:
        if mod in done:
            return
        if mod in active:
            raise ValueError(f"Local import cycle at {mod}")
        active.add(mod)
        for dep in imports[mod]:
            visit(dep)
        active.remove(mod)
        done.add(mod)
        order.append(mod)

    visit(ROOT_MODULE)
    if done != mods.keys():
        raise ValueError(f"Combined root omits {mods.keys() - done}")
    return {"compile_order": order, "compile_targets": len(mods),
            "production_modules": sum(mod.startswith("KomorebiSpace.") for mod in mods),
            "entrypoints": sorted(mod for mod in mods if "." not in mod),
            "source_scan": scans, "local_imports": imports,
            "source_sha256": {str(p.relative_to(project)): sha(p) for p in files},
            "explicit_theorem_lemma_count": sum(s["explicit_theorem_lemma_count"] for s in scans)}
