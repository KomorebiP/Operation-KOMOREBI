#!/usr/bin/env python3
"""Replay Block 66 exact certificates, corruption controls, and optional predecessors.

Requires only Python's standard library. The report must be outside this immutable
package. A timeout is inconclusive, never a successful finite exclusion.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent
OUTPUTS = (
    "count66.json", "independent_count66.json", "semilinear66.json",
    "independent_semilinear66.json", "filter66.json", "independent_filter66.json",
)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safe_extract(source: Path, destination: Path) -> None:
    with zipfile.ZipFile(source) as archive:
        need(archive.testzip() is None, "ZIP CRC failure")
        names = archive.namelist()
        need(len(names) == len(set(names)), "Duplicate ZIP member")
        for info in archive.infolist():
            target = (destination / info.filename).resolve()
            need(target.is_relative_to(destination.resolve()), "Unsafe ZIP path")
            need(not stat.S_ISLNK(info.external_attr >> 16), "ZIP symlink is not allowed")
        archive.extractall(destination)


def integrity(root: Path) -> dict[str, Any]:
    manifest = load(root / "MANIFEST.json")
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.relative_to(root).as_posix() != "MANIFEST.json"
    }
    need(actual == set(manifest["sha256"]), "Payload member set mismatch")
    for name, expected in manifest["sha256"].items():
        need(sha256(root / name) == expected, "Payload SHA256 mismatch: " + name)
    records = load(root / "work66/source_records/INHERITED_INPUTS.json")
    predecessors = list((root / "predecessor").glob("*.zip"))
    need(len(predecessors) == 1, "Expected exactly one frozen predecessor")
    predecessor = predecessors[0]
    need(sha256(predecessor) == records["predecessor_sha256"], "Predecessor bytes changed")
    cache: dict[tuple[str, ...], bytes] = {(): predecessor.read_bytes()}
    for entry in records["files"]:
        chain: tuple[str, ...] = ()
        for member in entry["archive_chain"]:
            extended = chain + (member,)
            if extended not in cache:
                with zipfile.ZipFile(io.BytesIO(cache[chain])) as archive:
                    cache[extended] = archive.read(member)
            chain = extended
        with zipfile.ZipFile(io.BytesIO(cache[chain])) as archive:
            content = archive.read(entry["member"])
        need(hashlib.sha256(content).hexdigest() == entry["sha256"],
             "Inherited source mismatch: " + entry["member"])
    copied = records["copied_input"]
    with zipfile.ZipFile(predecessor) as archive:
        need((root / copied["path"]).read_bytes() == archive.read(copied["member"]),
             "Copied inherited candidate list changed")
    return {
        "payload_files": len(actual),
        "named_inherited_source_files": len(records["files"]),
        "nested_archives_accessed": len(cache),
        "predecessor_sha256": sha256(predecessor),
        "copied_conductor_certificate": "BYTE_IDENTICAL",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--integrity-only", action="store_true")
    parser.add_argument("--replay-predecessors", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--job-timeout", type=int, default=600)
    args = parser.parse_args()
    need(args.job_timeout > 0, "Job timeout must be positive")
    if args.report:
        need(not args.report.resolve().is_relative_to(ROOT),
             "Write verification reports outside the immutable package")
    start = time.monotonic()
    jobs: list[dict[str, Any]] = []
    result: dict[str, Any] = {
        "schema": "beal.block66.verification.v1",
        "status": "RUNNING", "started_unix": time.time(),
        "python": sys.version, "platform": platform.platform(),
        "cpu_count_visible": os.cpu_count(),
        "job_timeout_seconds": args.job_timeout,
        "replay_predecessors": args.replay_predecessors,
        "limits": "Per-job wall cap; exact standard-library arithmetic; no randomness or network. Timeout is inconclusive.",
        "proof_boundary": "Finite certificate replay, not independent mathematical review or Lean verification.",
    }
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONOPTIMIZE="0")

    def run(arguments: list[Any], cwd: Path, negative: bool = False,
            diagnostic: str | None = None) -> subprocess.CompletedProcess[str]:
        argv = [sys.executable, "-B", *map(str, arguments)]
        before = time.monotonic()
        try:
            proc = subprocess.run(argv, cwd=cwd, env=env, text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  timeout=args.job_timeout, check=False)
        except subprocess.TimeoutExpired as exc:
            captured = exc.stdout or ""
            if isinstance(captured, bytes):
                captured = captured.decode("utf-8", errors="replace")
            jobs.append({"argv": argv, "cwd": str(cwd), "status": "INCONCLUSIVE_TIMEOUT",
                         "elapsed_seconds": time.monotonic() - before, "output": captured,
                         "expected_rejection": negative})
            raise
        jobs.append({"argv": argv, "cwd": str(cwd), "returncode": proc.returncode,
                     "elapsed_seconds": time.monotonic() - before,
                     "expected_rejection": negative, "output": proc.stdout})
        print("NEGATIVE" if negative else "REPLAY", Path(argv[2]).name,
              proc.returncode, flush=True)
        if negative:
            need(proc.returncode != 0, "Malformed input accepted")
            need(diagnostic is not None and diagnostic in proc.stdout,
                 "Wrong rejection reason: " + str(diagnostic))
        else:
            need(proc.returncode == 0, "Scientific job failed: " + str(arguments[0]))
        return proc

    try:
        result["integrity"] = integrity(ROOT)
        if not args.integrity_only:
            with tempfile.TemporaryDirectory(prefix="beal66_replay_") as directory:
                temporary = Path(directory)
                scratch = temporary / "package"
                shutil.copytree(ROOT, scratch)
                work = scratch / "work66"
                code = work / "computations"
                output = work / "verification"
                inherited = work / "source_records/conductor65.json"
                # Cached outputs must not mask interrupted or incomplete regeneration.
                for name in OUTPUTS:
                    (output / name).unlink()
                run([code / "count66.py", "--output", output / "count66.json"], work)
                run([code / "independent_count66.py", "--counts", output / "count66.json",
                     "--output", output / "independent_count66.json"], work)
                run([code / "semilinear66.py", "--output", output / "semilinear66.json"], work)
                run([code / "independent_semilinear66.py", "--certificate", output / "semilinear66.json",
                     "--output", output / "independent_semilinear66.json"], work)
                run([code / "filter66.py", "--inherited", inherited, "--counts", output / "count66.json",
                     "--output", output / "filter66.json"], work)
                run([code / "independent_filter66.py", "--inherited", inherited,
                     "--counts", output / "count66.json", "--certificate", output / "filter66.json",
                     "--output", output / "independent_filter66.json"], work)
                for name in OUTPUTS:
                    need(load(output / name) == load(ROOT / "work66/verification" / name),
                         "Complete JSON replay mismatch: " + name)
                result["complete_json_replays"] = list(OUTPUTS)
                bad = temporary / "negative"
                bad.mkdir()
                broken = load(output / "count66.json")
                broken["primes"][0]["rows"][0]["N1"] += 1
                write(bad / "counts.json", broken)
                run([code / "independent_count66.py", "--counts", bad / "counts.json",
                     "--output", bad / "out.json"], work, True, "Point-count row mismatch")

                def corrupt_filter(name: str, mutate: Callable[[Any], None], diagnostic: str) -> None:
                    data = load(output / "filter66.json")
                    mutate(data)
                    write(bad / name, data)
                    run([code / "independent_filter66.py", "--inherited", inherited,
                         "--counts", output / "count66.json", "--certificate", bad / name,
                         "--output", bad / "out.json"], work, True, diagnostic)

                def changed_column(data: Any) -> None:
                    row = data["columns"][0]["rows"]
                    row["421"] = (row["421"] + 1) % 7

                corrupt_filter("column.json", changed_column, "Changed twisted column")
                corrupt_filter("pair.json",
                               lambda data: data["tests"][0]["paired_trace_sets"].append([1]),
                               "Changed common polynomial or Kummer data")
                corrupt_filter("survivors.json", lambda data: data.__setitem__("count", 0),
                               "Changed final survivors")
                broken = load(output / "semilinear66.json")
                broken["accepted_quadruples"].append([7, 1, 7, 7])
                write(bad / "semilinear.json", broken)
                run([code / "independent_semilinear66.py", "--certificate", bad / "semilinear.json",
                     "--output", bad / "out.json"], work, True, "Changed semilinear classification")
                with (scratch / "README.md").open("a", encoding="utf-8") as stream:
                    stream.write("\nDELIBERATELY ALTERED PAYLOAD\n")
                run([scratch / "verify.py", "--integrity-only", "--report", bad / "payload.json"],
                    scratch, True, "Payload SHA256 mismatch")
                result["negative_controls"] = [
                    "changed_point_count", "changed_twisted_column", "invented_common_polynomial_pair",
                    "false_zero_survivor_count", "invalid_semilinear_quadruple", "altered_payload",
                ]
                if args.replay_predecessors:
                    destination = temporary / "predecessor"
                    destination.mkdir()
                    safe_extract(next((ROOT / "predecessor").glob("*.zip")), destination)
                    old = destination / "Komorebi_Beal_Block65"
                    report = temporary / "Block65_Replay.json"
                    run([old / "verify.py", "--replay-predecessors", "--report", report], old)
                    predecessor_result = load(report)
                    need(predecessor_result.get("status") == "PASS", "Unexpected predecessor status")
                    result["predecessor_replay"] = predecessor_result
        result["status"] = "PASS"
    except subprocess.TimeoutExpired as exc:
        result["status"] = "INCONCLUSIVE_TIMEOUT"
        result["error"] = str(exc)
        print(str(exc), file=sys.stderr)
    except Exception as exc:
        result["status"] = "FAIL"
        result["error"] = str(exc)
        print(str(exc), file=sys.stderr)
    result["jobs"] = jobs
    result["elapsed_seconds"] = time.monotonic() - start
    result["finished_unix"] = time.time()
    if args.report:
        write(args.report, result)
    print(result["status"], flush=True)
    return 0 if result["status"] == "PASS" else (3 if result["status"] == "INCONCLUSIVE_TIMEOUT" else 2)


if __name__ == "__main__":
    sys.exit(main())
