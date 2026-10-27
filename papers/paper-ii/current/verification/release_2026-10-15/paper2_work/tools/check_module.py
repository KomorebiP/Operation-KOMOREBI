#!/usr/bin/env python3
"""Serial, bounded Paper II development check against authenticated fresh objects.

This compiles one exact source snapshot. It does not assert manuscript coverage
or perform a complete release audit. Dependency caches remain trusted inputs.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import time


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def main() -> int:
    work = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--module", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, default=work / "baseline_compile")
    parser.add_argument("--extra-objects", type=Path, action="append", default=[])
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--memory-mib", type=int, default=0,
                        help="Optional virtual-address cap; default 0 uses the existing container bound. Lean maps large cache files.")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*", args.module):
        parser.error("Module must be a dotted Lean identifier")
    if not 0 < args.timeout < 86400 or not (args.memory_mib == 0 or 8192 <= args.memory_mib <= 65536):
        parser.error("Invalid resource bounds")
    source_root = args.source_root.resolve()
    rel = Path(*args.module.split(".")).with_suffix(".lean")
    source = source_root / rel
    if not source.is_file() or source.is_symlink():
        parser.error("Source must be an existing regular file")
    out = args.output.resolve()
    if out == source_root or source_root in out.parents:
        parser.error("Output must be outside source root")
    out.mkdir(parents=True, exist_ok=False)
    record = {"status": "WAITING", "module": args.module,
              "source_path": str(source), "source_sha256": sha(source),
              "timeout_seconds": args.timeout, "address_space_limit_mib": args.memory_mib or None,
              "container_memory_max_bytes": Path('/sys/fs/cgroup/memory.max').read_text().strip(),
              "interpretation": "One source module compiled with strict flags. Not a full release or semantic coverage audit."}
    write(out / "CHECK.json", record)
    with (work / "lean_serial.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            baseline = args.baseline.resolve()
            prior = json.loads((baseline / "REPLAY.json").read_text())
            if prior["status"] != "PASS" or not prior["sources_unchanged"]:
                raise RuntimeError("Baseline is not an accepted unchanged-source compilation")
            for row in prior["modules"]:
                if row["status"] != "PASS":
                    raise RuntimeError("Failed baseline module")
                for obj, digest in row["objects"].items():
                    if sha(baseline / "objects" / obj) != digest:
                        raise RuntimeError("Baseline object changed: " + obj)
            record["baseline_receipt_sha256"] = sha(baseline / "REPLAY.json")
            driver_path = Path(__file__).with_name("replay_current.py")
            spec = importlib.util.spec_from_file_location("paper2_replay_driver", driver_path)
            driver = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(driver)
            runtime, env = driver.validate_runtime(args.runtime.resolve())
            record["runtime"] = runtime
            record["runtime_driver_sha256"] = sha(driver_path)
            snapshots = out / "source_snapshots"
            snapshot = snapshots / rel
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, snapshot)
            if sha(snapshot) != record["source_sha256"]:
                raise RuntimeError("Source changed before snapshot")
            objects = out / "objects"
            obj = objects / rel.with_suffix(".olean")
            info = objects / rel.with_suffix(".ilean")
            extra = [p.resolve() for p in args.extra_objects]
            if any(not p.is_dir() for p in extra):
                raise RuntimeError("Extra object root is missing")
            record["extra_objects"] = {
                str(p): {str(f.relative_to(p)): sha(f) for f in sorted(p.rglob("*.olean"))}
                for p in extra}
            # Lean chooses the first existing root namespace directory. Merely
            # prepending a partly populated namespace would hide later roots.
            # Merge authenticated inputs into one scratch tree using hardlinks.
            dependency_objects = {}
            for dependency in [baseline / "objects", *reversed(extra)]:
                for file in sorted(dependency.rglob("*")):
                    if not file.is_file() or file.suffix not in {".olean", ".ilean"}:
                        continue
                    target = objects / file.relative_to(dependency)
                    if target in {obj, info}:
                        continue
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if target.exists():
                        target.unlink()
                    os.link(file, target)
                    dependency_objects[str(target.relative_to(objects))] = {
                        "source": str(file), "sha256": sha(file)}
            record["dependency_objects"] = dependency_objects
            obj.parent.mkdir(parents=True, exist_ok=True)
            env["LEAN_PATH"] = os.pathsep.join(
                [str(objects), env["LEAN_PATH"]])
            record["lean_path"] = env["LEAN_PATH"]
            cmd = [str(args.runtime.resolve() / "toolchain/bin/lean"), *driver.FLAGS,
                   "-o", str(obj), "-i", str(info), str(rel)]
            record.update(status="RUNNING", command=cmd)
            write(out / "CHECK.json", record)
            def limits() -> None:
                if args.memory_mib:
                    cap = args.memory_mib * 1024 * 1024
                    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
            started = time.monotonic()
            with (out / "compile.log").open("w") as log:
                try:
                    result = subprocess.run(cmd, cwd=snapshots, env=env, stdout=log,
                                            stderr=subprocess.STDOUT, timeout=args.timeout,
                                            preexec_fn=limits)
                    code = result.returncode
                except subprocess.TimeoutExpired:
                    code = 124
            record.update(elapsed_seconds=time.monotonic() - started, returncode=code,
                          max_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                          source_unchanged=sha(source) == record["source_sha256"],
                          log_sha256=sha(out / "compile.log"))
            logs = (out / "compile.log").read_text(errors="replace")
            accepted = code == 0 and obj.is_file() and not re.search(r"\berror(?:\(|:)", logs)
            accepted = accepted and record["source_unchanged"]
            record["dependency_objects_unchanged"] = all(
                sha(objects / name) == item["sha256"] and sha(Path(item["source"])) == item["sha256"]
                for name, item in dependency_objects.items())
            accepted = accepted and record["dependency_objects_unchanged"]
            record["status"] = "PASS" if accepted else "TIMEOUT" if code == 124 else "FAIL"
            record["objects"] = {str(p.relative_to(objects)): sha(p) for p in [obj, info] if p.is_file()}
        except Exception as error:
            record.update(status="FAIL", failure=type(error).__name__ + ": " + str(error))
        write(out / "CHECK.json", record)
        print(json.dumps({k: record[k] for k in ["status", "module", "returncode", "failure", "elapsed_seconds", "max_rss_kib"] if k in record}, indent=2))
        return 0 if record["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
