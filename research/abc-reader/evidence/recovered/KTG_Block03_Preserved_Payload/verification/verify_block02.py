#!/usr/bin/env python3
"""Reproduce the KTG Block 02 Lean verification.

The project is dependency-free apart from Lean's bundled `Std`.  Set LEAN_BIN
and LAKE_BIN when the desired toolchain is not on PATH.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "formalization" / "lean"
OUT = ROOT / "verification" / "block02_final"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def executable(env_name: str, fallback: str) -> str:
    candidate = os.environ.get(env_name)
    if candidate:
        p = Path(candidate)
        if not p.is_file():
            raise SystemExit(f"{env_name} does not name a file: {candidate}")
        return str(p)
    found = shutil.which(fallback)
    if not found:
        raise SystemExit(
            f"Missing {fallback}. Put it on PATH or set {env_name} to the executable."
        )
    return found


def run(argv: list[str], cwd: Path, env: dict[str, str] | None = None) -> dict:
    started = time.monotonic()
    proc = subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "argv": argv,
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "output": proc.stdout,
    }


def strip_lean_comments(text: str) -> str:
    """Remove nested block comments and line comments, preserving strings enough
    for a conservative placeholder scan.  This is not a Lean parser."""
    out: list[str] = []
    i = 0
    depth = 0
    in_string = False
    while i < len(text):
        if depth:
            if text.startswith("/-", i):
                depth += 1
                i += 2
            elif text.startswith("-/", i):
                depth -= 1
                i += 2
            else:
                if text[i] == "\n":
                    out.append("\n")
                i += 1
            continue
        if not in_string and text.startswith("/-", i):
            depth = 1
            i += 2
            continue
        if not in_string and text.startswith("--", i):
            j = text.find("\n", i)
            if j == -1:
                break
            out.append("\n")
            i = j + 1
            continue
        ch = text[i]
        out.append(ch)
        if ch == '"' and (i == 0 or text[i - 1] != "\\"):
            in_string = not in_string
        i += 1
    return "".join(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true", help="remove .lake/build first")
    args = parser.parse_args()

    lean = executable("LEAN_BIN", "lean")
    lake = executable("LAKE_BIN", "lake")
    OUT.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    records.append(run([lean, "--version"], PROJECT))
    records.append(run([lake, "--version"], PROJECT))

    if args.clean:
        shutil.rmtree(PROJECT / ".lake" / "build", ignore_errors=True)

    build = run([lake, "build"], PROJECT)
    (OUT / "lake_build.log").write_text(build["output"], encoding="utf-8")
    records.append({k: v for k, v in build.items() if k != "output"} | {"log": "lake_build.log"})
    if build["returncode"] != 0:
        report = {
            "status": "FAIL_LAKE_BUILD",
            "project": str(PROJECT),
            "records": records,
        }
        (OUT / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
        print(build["output"], end="")
        return build["returncode"] or 1

    lean_files = sorted((PROJECT / "KTG").glob("*.lean")) + [PROJECT / "KTG.lean"]
    source_hashes = {str(p.relative_to(ROOT)): sha256(p) for p in lean_files}

    forbidden: dict[str, list[str]] = {}
    token_re = re.compile(r"\b(?:sorry|admit|unsafe)\b|^\s*axiom\b", re.MULTILINE)
    for path in lean_files:
        stripped = strip_lean_comments(path.read_text(encoding="utf-8"))
        hits = sorted(set(m.group(0).strip() for m in token_re.finditer(stripped)))
        if hits:
            forbidden[str(path.relative_to(ROOT))] = hits

    per_file: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="ktg-block02-") as td:
        tmp = Path(td)
        env = os.environ.copy()
        built_lib = PROJECT / ".lake" / "build" / "lib" / "lean"
        old_path = env.get("LEAN_PATH", "")
        env["LEAN_PATH"] = str(built_lib) + (os.pathsep + old_path if old_path else "")
        log_dir = OUT / "per_file"
        log_dir.mkdir(parents=True, exist_ok=True)
        for index, source in enumerate(lean_files):
            slug = str(source.relative_to(PROJECT)).replace(os.sep, "__").replace(".lean", "")
            output = tmp / f"{index:02d}_{slug}.olean"
            rec = run(
                [lean, "-DwarningAsError=true", "-o", str(output), str(source)],
                PROJECT,
                env,
            )
            log_name = f"per_file/{index:02d}_{slug}.log"
            (OUT / log_name).write_text(rec["output"], encoding="utf-8")
            per_file.append(
                {k: v for k, v in rec.items() if k != "output"}
                | {"source": str(source.relative_to(ROOT)), "log": log_name}
            )

    failed_files = [r["source"] for r in per_file if r["returncode"] != 0]
    status = "PASS"
    if forbidden:
        status = "FAIL_PLACEHOLDER_AUDIT"
    elif failed_files:
        status = "FAIL_PER_FILE_WARNING_AS_ERROR"

    report = {
        "status": status,
        "project": str(PROJECT),
        "declared_toolchain": (PROJECT / "lean-toolchain").read_text().strip(),
        "actual_lean_version": records[0]["output"].strip(),
        "actual_lake_version": records[1]["output"].strip(),
        "clean_build_requested": args.clean,
        "lean_source_count": len(lean_files),
        "source_sha256": source_hashes,
        "forbidden_token_hits": forbidden,
        "failed_per_file_checks": failed_files,
        "records": records,
        "per_file": per_file,
        "claim_boundary": {
            "iut_iii_corollary_3_12": "NOT_PROVED_OR_DISPROVED",
            "verified_claim": "KTG Block 02 sources elaborate and build under the recorded actual Lean compiler",
            "nonclaim": "A successful build does not instantiate the IUT-specific witness-preservation bridge",
        },
    }
    (OUT / "verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "lean_source_count": len(lean_files),
        "failed_per_file_checks": failed_files,
        "forbidden_token_hits": forbidden,
    }, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
