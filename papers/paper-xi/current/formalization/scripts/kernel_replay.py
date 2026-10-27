#!/usr/bin/env python3
"""Replay each freshly built module's declarations through Lean's kernel.

This uses the official leanchecker shipped with the pinned Lean release. It
checks module declarations over their imported environments. It is not an
independent implementation of Lean's kernel and does not rebuild mathlib.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import time

from replay import ROOT, locate_bin, runtime_environment, sha, stamp, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", default="evidence/replay")
    parser.add_argument("--out", default="evidence/kernel_replay")
    parser.add_argument("--lean-bin")
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--scope", choices=["all", "selected", "terminal", "new_interface"], default="all")
    args = parser.parse_args()
    if not 1 <= args.jobs <= 8:
        parser.error("--jobs must be between 1 and 8")
    replay = (ROOT / args.replay).resolve()
    out = (ROOT / args.out).resolve()
    if not out.is_relative_to(ROOT) or out.exists():
        parser.error("--out must be a new directory inside this project")
    build = json.loads((replay / "RESULT.json").read_text())
    if build.get("selected_status") != "PASS":
        parser.error("The complete selected-source replay must pass first")
    rows = [x for x in build["modules"] if x["status"] == "PASS"
            and (args.scope == "all" or x["group"] == args.scope)]
    out.mkdir(parents=True)
    logs = out / "logs"
    logs.mkdir()
    bin_dir = locate_bin(args.lean_bin)
    env = runtime_environment(bin_dir, replay / "objects")
    inputs = {path: digest for x in rows for path, digest in x["artifacts"].items()}
    for path, digest in inputs.items():
        if sha(ROOT / path) != digest:
            raise RuntimeError(f"Fresh object changed before kernel replay: {path}")
    report = {
        "status": "RUNNING", "started_at": stamp(), "scope": args.scope,
        "module_count": len(rows), "jobs": args.jobs,
        "per_module_timeout_seconds": args.timeout,
        "tool": str(bin_dir / "leanchecker"), "tool_sha256": sha(bin_dir / "leanchecker"),
        "lean_version": build["lean_version"], "mathlib_commit": build["mathlib_commit"],
        "object_hashes_before": inputs, "modules": [],
        "method": "Official leanchecker replays each target module's own declarations into its imported kernel environment.",
        "non_claims": ["This is not an independent kernel implementation.",
                       "Imported mathlib declarations are not rebuilt by this check."]
    }
    write_json(out / "RESULT.json", report)
    start = time.monotonic()

    def run(row: dict) -> dict:
        name = row["module"]
        command = [str(bin_dir / "leanchecker"), "--verbose", name]
        log = logs / (name + ".log")
        began = stamp()
        t = time.monotonic()
        with log.open("w") as f:
            try:
                p = subprocess.run(command, cwd=ROOT, env=env, stdout=f,
                                   stderr=subprocess.STDOUT, timeout=args.timeout)
                code = p.returncode
                replayed = [s[len("replaying "):] for s in log.read_text().splitlines()
                            if s.startswith("replaying ")]
                status = "PASS" if code == 0 and replayed == [name] else "FAIL"
            except subprocess.TimeoutExpired:
                code = None; replayed = []; status = "TIMEOUT"
        return {"module": name, "group": row["group"], "status": status,
                "exit_code": code, "started_at": began, "seconds": time.monotonic() - t,
                "command": command, "reported_replayed_modules": replayed,
                "log_path": str(log.relative_to(ROOT)), "log_sha256": sha(log)}

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(run, row) for row in rows]
        for future in as_completed(futures):
            row = future.result()
            report["modules"].append(row)
            report["elapsed_seconds"] = time.monotonic() - start
            write_json(out / "RESULT.json", report)
            print(f'{len(report["modules"]):03d}/{len(rows)} {row["module"]}: '
                  f'{row["status"]} ({row["seconds"]:.2f}s)', flush=True)
    after = {path: sha(ROOT / path) for path in inputs}
    report.update(object_hashes_after=after, objects_unchanged=inputs == after,
                  completed_at=stamp(), elapsed_seconds=time.monotonic() - start)
    report["status"] = "PASS" if inputs == after and all(x["status"] == "PASS"
        for x in report["modules"]) and len(report["modules"]) == len(rows) else "FAIL"
    write_json(out / "RESULT.json", report)
    print(json.dumps({k: report[k] for k in ["status", "module_count", "objects_unchanged", "elapsed_seconds"]}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
