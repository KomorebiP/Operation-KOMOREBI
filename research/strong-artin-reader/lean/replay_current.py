#!/usr/bin/env python3
"""Replay the original v0.38 verifier in a new isolated extraction.

This wrapper changes no mathematical source. It checks the exact archive hash,
extracts it to a new work directory and invokes its pinned verifier. The kit is
an external dependency, not included in the paper handoff.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ARCHIVE_SHA = "d5f065bcb05ee02465082804dfb14800f82b86f43a8838eded2e3d3519abcb9a"
ROOT_NAME = "Strong_Artin_v0.38_Effective_Matrix_Hensel"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive", type=Path, required=True)
    ap.add_argument("--kit", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    args = ap.parse_args()
    start = time.monotonic()
    work = args.work.resolve()
    if work.exists(): raise FileExistsError("Use a new replay work directory")
    work.mkdir(parents=True)
    rec = {"started_utc": datetime.now(timezone.utc).isoformat(),
           "scope": "Seven new v0.38 modules plus all-named-constant axiom audit; pinned Mathlib cache reused",
           "parent_freshly_replayed": False,
           "archive": str(args.archive.resolve()), "kit": str(args.kit.resolve()),
           "status": "IN_PROGRESS"}
    try:
        blob = args.archive.read_bytes()
        rec["archive_sha256"] = hashlib.sha256(blob).hexdigest()
        if rec["archive_sha256"] != ARCHIVE_SHA:
            raise ValueError("Archive identity does not match the authenticated v0.38 checkpoint")
        kit = args.kit.resolve()
        if not (kit/"toolchain/bin/lean").is_file():
            rec.update(status="BLOCKED", failure="Matching Lean binary is absent", fresh_lean_replay=False)
            return 2
        with zipfile.ZipFile(args.archive) as z:
            if z.testzip() is not None: raise ValueError("Archive CRC failure")
            for n in z.namelist():
                p = Path(n)
                if p.is_absolute() or ".." in p.parts: raise ValueError("Unsafe archive path")
            z.extractall(work/"extract")
        root = work/"extract"/ROOT_NAME
        cmd = [sys.executable, str(root/"verify.py"), "--kit", str(kit), "--label", "current_replay"]
        rec["command"] = cmd
        # Each original compiler invocation has its own 120-second timeout.
        # This outer timeout bounds the eight-invocation verifier as a whole.
        run = subprocess.run(cmd, capture_output=True, text=True, timeout=1100)
        (work/"stdout.txt").write_text(run.stdout)
        (work/"stderr.txt").write_text(run.stderr)
        rec["returncode"] = run.returncode
        evidence = root/"verification/current_replay/RESULT.json"
        rec["verifier_result"] = str(evidence)
        if evidence.exists():
            result = json.loads(evidence.read_text())
            rec["verifier_status"] = result["status"]
            rec["verifier_result_sha256"] = hashlib.sha256(evidence.read_bytes()).hexdigest()
        rec["status"] = "PASS" if run.returncode == 0 and rec.get("verifier_status") == "PASS" else "FAIL"
        rec["fresh_lean_replay"] = rec["status"] == "PASS"
        return 0 if rec["status"] == "PASS" else 1
    except Exception as exc:
        rec.update(status="FAIL", failure=type(exc).__name__+": "+str(exc), fresh_lean_replay=False)
        return 1
    finally:
        rec["finished_utc"] = datetime.now(timezone.utc).isoformat()
        rec["runtime_seconds"] = time.monotonic()-start
        (work/"WRAPPER_RESULT.json").write_text(json.dumps(rec, indent=2)+"\n")
        print(json.dumps(rec))


if __name__ == "__main__":
    raise SystemExit(main())
