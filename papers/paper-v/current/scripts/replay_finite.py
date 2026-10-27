#!/usr/bin/env python3
"""Replay Paper V's eight bounded finite suites in temporary source copies.

Usage: python3 scripts/replay_finite.py --output /absolute/new/output-directory
The output directory must not exist and must lie outside this release tree.
Requires the installed Python dependencies numpy, pytest, sympy and mpmath.
This command performs no Lean execution and downloads or installs nothing.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "source/complete/original_snapshot"
IGNORED = {"__pycache__", ".pytest_cache", ".lake"}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def eligible(path, relative):
    return path.is_file() and not any(part in IGNORED for part in relative.parts)


def inventory(directory):
    return {
        path.relative_to(directory).as_posix(): digest(path)
        for path in sorted(directory.rglob("*"))
        if eligible(path, path.relative_to(directory))
    }


def clone(directory, destination):
    shutil.copytree(directory, destination, ignore=shutil.ignore_patterns(*sorted(IGNORED)))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_unittest(path, expected):
    report = read_json(path)
    require(report.get("status") == "PASS", f"Nonpassing suite report: {path}")
    require(report.get("tests_run") == expected, f"Unexpected method count: {report}")
    require(report.get("failures") == 0 and report.get("errors") == 0,
            f"Nonzero unittest errors/failures: {report}")
    require(report.get("lean_kernel_checked") is False, "Finite report misstated its Lean scope")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error("--output must be outside the release source tree")
    if output.exists():
        parser.error("--output must be a new directory, so old evidence cannot be reused")
    output.mkdir(parents=True, exist_ok=False)
    summary = {
        "schema": "komorebi.paper_v.finite_replay.v1",
        "status": "STARTED", "started_utc": now(),
        "python": sys.version, "python_executable": sys.executable,
        "platform": platform.platform(), "launcher_optimization": sys.flags.optimize,
        "runner_sha256": digest(Path(__file__)),
        "dependencies": {}, "suites": [], "errors": [],
        "lean_process_ran": False, "new_formal_theorem_claimed": False,
        "scope": "Eight preserved bounded test suites, with their original ranges and tolerances.",
        "counting_policy": "Counts from overlapping suites are not added into independent assertions or results.",
        "optimization_policy": (
            "The acceptance launcher and all eight suite commands use normal Python optimization level 0. "
            "One original verifier test deliberately invokes -O on a corrupted input and requires rejection. "
            "That expected-rejection child is a robustness control, not an optimized acceptance run."
        ),
    }
    write_json(output / "REPLAY_SUMMARY.json", summary)
    try:
        require(sys.flags.optimize == 0, "Run this acceptance launcher without -O or PYTHONOPTIMIZE")
        for package in ("numpy", "pytest", "sympy", "mpmath"):
            summary["dependencies"][package] = importlib.metadata.version(package)
        with tempfile.TemporaryDirectory(prefix="paper-v-finite-replay-") as temporary:
            temp = Path(temporary)
            source_sets = {
                "snapshot": SNAPSHOT,
                "annals": ROOT / "source/annals",
                "visual": ROOT / "editable/visual_guide",
            }
            before = {name: inventory(src) for name, src in source_sets.items()}
            write_json(output / "INPUT_SHA256.json", {
                name: {"root_relative": src.relative_to(ROOT).as_posix(), "files": before[name]}
                for name, src in source_sets.items()
            })
            for name, src in source_sets.items():
                clone(src, temp / name)
                require(inventory(temp / name) == before[name], f"Clone bytes differ for {name}")
            snapshot, annals, visual = (temp / name for name in ("snapshot", "annals", "visual"))
            env = os.environ.copy()
            env.pop("PYTHONOPTIMIZE", None)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
            env["MPLBACKEND"] = "Agg"

            def invoke(name, command, cwd, validator, timeout=600):
                suite_out = output / name
                suite_out.mkdir()
                record = {"name": name, "status": "STARTED", "command": command,
                          "cwd": str(cwd), "started_utc": now(), "timeout_seconds": timeout}
                summary["suites"].append(record)
                write_json(suite_out / "COMMAND.json", record)
                started = time.monotonic()
                # Explicit clone-local import path also supports nested companion packages.
                local_env = env.copy()
                inherited_paths = [path for path in env.get("PYTHONPATH", "").split(os.pathsep) if path]
                local_env["PYTHONPATH"] = os.pathsep.join([str(cwd), str(snapshot / "tests"), *inherited_paths])
                record["pythonpath"] = local_env["PYTHONPATH"]
                try:
                    result = subprocess.run(command, cwd=cwd, env=local_env, stdin=subprocess.DEVNULL,
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
                    (suite_out / "stdout.log").write_bytes(result.stdout)
                    (suite_out / "stderr.log").write_bytes(result.stderr)
                    record["returncode"] = result.returncode
                    require(result.returncode == 0, f"{name} exited {result.returncode}")
                    record["validated_result"] = validator(suite_out, result.stdout.decode("utf-8", "replace"))
                    record["status"] = "PASS"
                except subprocess.TimeoutExpired as error:
                    (suite_out / "stdout.log").write_bytes(error.stdout or b"")
                    (suite_out / "stderr.log").write_bytes(error.stderr or b"")
                    record.update(status="FAIL", error=f"Timeout after {timeout} seconds")
                    summary["errors"].append({"suite": name, "error": record["error"]})
                except Exception as error:
                    record.update(status="FAIL", error=f"{type(error).__name__}: {error}")
                    (suite_out / "validation_error.log").write_text(traceback.format_exc(), encoding="utf-8")
                    summary["errors"].append({"suite": name, "error": record["error"]})
                record.update(elapsed_seconds=time.monotonic() - started, finished_utc=now())
                write_json(suite_out / "RESULT.json", record)
                write_json(output / "REPLAY_SUMMARY.json", summary)
                print(f"{name}: {record['status']} ({record['elapsed_seconds']:.3f}s)", flush=True)

            python = [sys.executable, "-B"]
            for name, script, count in (
                ("readiness", "test_readiness.py", 10),
                ("verifier", "test_verifier.py", 16),
                ("exact_models", "test_exact_models.py", 12),
                ("second_block", "test_second_block.py", 8),
            ):
                report_path = output / name / "suite_report.json"
                invoke(name, python + ["tests/" + script, "--report", str(report_path)], snapshot,
                       lambda directory, stdout, count=count: check_unittest(directory / "suite_report.json", count))

            def pytest_result(directory, stdout):
                document = ET.parse(directory / "junit.xml").getroot()
                rows = list(document.iter("testsuite"))
                totals = {key: sum(int(row.get(key, 0)) for row in rows)
                          for key in ("tests", "failures", "errors", "skipped")}
                require(totals == {"tests": 33, "failures": 0, "errors": 0, "skipped": 0},
                        f"Companion pytest totals differ: {totals}")
                return {**totals, "arithmetic": "NumPy IEEE float/complex with the preserved test tolerances"}

            invoke("numeric_pytest", python + ["-m", "pytest", "-q", "-p", "no:cacheprovider",
                   "--junitxml=" + str(output / "numeric_pytest/junit.xml"), "tests"],
                   snapshot / "companion", pytest_result)

            def annals_result(directory, stdout):
                found = re.search(r"Paper V revised verification: (\d+)/(\d+) checks passed in (\d+) groups", stdout)
                require(found is not None and tuple(map(int, found.groups())) == (11052, 11052, 13),
                        "Annals result marker/counts differ")
                return {"checks_passed": 11052, "groups": 13,
                        "arithmetic": "Preserved mixed exact/source and NumPy numerical checks",
                        "scope": "Includes 10001 sampled half-shift positions, not a universal proof"}

            invoke("annals", python + ["verification/verify_paper_v.py"], annals, annals_result)

            for name, script, report_name, checks, controls in (
                ("visual_symbolic", "verify_examples.py", "EXACT_CHECKS.json", 181, 7),
                ("visual_extension", "verify_extension_examples.py", "EXTENSION_EXACT_CHECKS.json", 38, 4),
            ):
                def visual_result(directory, stdout, report_name=report_name, checks=checks, controls=controls):
                    generated = visual / "checks" / report_name
                    data = read_json(generated)
                    require(data.get("status") == "PASS" and data.get("checks_passed") == checks,
                            f"Symbolic check count differs: {data}")
                    require(len(data.get("invalid_controls_rejected", [])) == controls,
                            "Rejected-control count differs")
                    shutil.copy2(generated, directory / report_name)
                    return {"checks_passed": checks, "invalid_controls_rejected": controls,
                            "arithmetic": "Exact integers, rational and SymPy symbolic/algebraic examples"}
                # Delete only the temporary clone's historical output, so a stale report cannot pass.
                (visual / "checks" / report_name).unlink(missing_ok=True)
                invoke(name, python + ["checks/" + script], visual, visual_result)

            preservation = {}
            for name, src in source_sets.items():
                current = inventory(src)
                changed = sorted(path for path in before[name].keys() & current.keys()
                                 if before[name][path] != current[path])
                missing = sorted(before[name].keys() - current.keys())
                added = sorted(current.keys() - before[name].keys())
                preservation[name] = {"status": "PASS" if not (changed or missing or added) else "FAIL",
                                      "files_checked": len(before[name]), "changed": changed,
                                      "missing": missing, "added": added}
            write_json(output / "SOURCE_PRESERVATION.json", preservation)
            summary["source_preservation"] = preservation
            require(all(record["status"] == "PASS" for record in preservation.values()), "Input source bytes changed")
            require(len(summary["suites"]) == 8, "All eight suites must run")
            require(not summary["errors"] and all(record["status"] == "PASS" for record in summary["suites"]),
                    "At least one finite suite did not pass; inspect its logs")
        summary["status"] = "PASS"
    except Exception as error:
        summary["status"] = "FAIL"
        summary["errors"].append({"phase": "launcher", "error": f"{type(error).__name__}: {error}"})
        (output / "LAUNCHER_ERROR.log").write_text(traceback.format_exc(), encoding="utf-8")
    summary["finished_utc"] = now()
    write_json(output / "REPLAY_SUMMARY.json", summary)
    artifacts = {path.relative_to(output).as_posix(): digest(path)
                 for path in sorted(output.rglob("*")) if path.is_file() and path.name != "ARTIFACT_SHA256.json"}
    write_json(output / "ARTIFACT_SHA256.json", artifacts)
    print(json.dumps({"status": summary["status"], "output": str(output), "errors": summary["errors"]}, indent=2))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
