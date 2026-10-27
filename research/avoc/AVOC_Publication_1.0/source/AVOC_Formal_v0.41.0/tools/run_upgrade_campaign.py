#!/usr/bin/env python3
"""Execute the verified upgrade gate for a fixed compiled component catalogue.

This is a replayed, read-only campaign evaluator, not a live self-modifying agent.
It never changes the research workflow, replaces source files, or authorizes retries.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORE = "AVOC-upgrade-checker-v1"
OBJECTIVE = "retry-action-NoRevival;visits-horizons-0-1-2-4-8-16-32;v1"
VERSIONS = {"dynamic", "threshold", "always_retry"}


def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def natural(value: Any, name: str, maximum: int) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f"{name} must be an integer between 0 and {maximum}")
    return value


def make_wire(config: Any) -> list[Any]:
    if not isinstance(config, dict) or set(config) != {"credits", "proposals"}:
        raise ValueError("campaign requires exactly credits and proposals; scores and prices are protected")
    credits = natural(config["credits"], "credits", 10000)
    proposals = config["proposals"]
    if not isinstance(proposals, list) or len(proposals) > 128:
        raise ValueError("proposals must be a list of at most 128 entries")
    encoded = []
    for proposal in proposals:
        if not isinstance(proposal, dict):
            raise ValueError("proposal must be an object")
        if not {"parent", "revision", "candidate"} <= set(proposal) or not set(proposal) <= {
            "parent", "revision", "candidate", "core", "objective"
        }:
            raise ValueError("invalid proposal fields; no candidate-provided scores or fees")
        parent, candidate = proposal["parent"], proposal["candidate"]
        if not isinstance(parent, str) or not isinstance(candidate, str) or parent not in VERSIONS or candidate not in VERSIONS:
            raise ValueError("unknown immutable candidate")
        revision = natural(proposal["revision"], "revision", 1000)
        core, objective = proposal.get("core", CORE), proposal.get("objective", OBJECTIVE)
        if not all(isinstance(s, str) and len(s.encode("utf-8")) <= 256 for s in (core, objective)):
            raise ValueError("invalid identity string")
        encoded.append([parent, revision, candidate, core, objective])
    return ["avoc-upgrade-campaign-v1", credits, encoded]


def checked_environment() -> tuple[Path, dict[str, str]]:
    kit = Path(os.environ.get("AVOC_LEAN_KIT", "/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2")).resolve()
    lean = kit / "toolchain/bin/lean"
    if not lean.is_file():
        raise RuntimeError("pinned Lean runtime is missing; set AVOC_LEAN_KIT and follow REPRODUCE.md")
    pins = json.loads((ROOT / "upgrade_source_pins.json").read_text())
    for relative, expected in pins["sources"].items():
        path = ROOT / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError(f"protected source drift: {relative}")
    for relative in pins["compiled_targets"]:
        path = ROOT / relative
        record_path = ROOT / "results/v0.23.0" / f"clean_{path.stem}.json"
        output = ROOT / ".lake/build/lib/lean" / Path(relative).with_suffix(".olean")
        if not record_path.is_file() or not output.is_file():
            raise RuntimeError(f"current checked local build is missing: {relative}")
        record = json.loads(record_path.read_text())
        if (record["returncode"] != 0 or record["timed_out"] or
            record["source_sha256"] != hashlib.sha256(path.read_bytes()).hexdigest() or
            record["output_sha256"] != hashlib.sha256(output.read_bytes()).hexdigest()):
            raise RuntimeError(f"stale or altered local build: {relative}")
    version = subprocess.check_output([str(lean), "--version"], text=True, timeout=10).strip()
    if version != pins["lean_version"]:
        raise RuntimeError("Lean runtime version mismatch")
    if hashlib.sha256(lean.read_bytes()).hexdigest() != pins["lean_binary_sha256"]:
        raise RuntimeError("Lean executable fingerprint mismatch")
    env = os.environ.copy()
    packages = kit / "workspace/.lake/packages"
    env["LEAN_PATH"] = ":".join(map(str, [ROOT / ".lake/build/lib/lean"] + [
        p / ".lake/build/lib/lean" for p in sorted(packages.iterdir()) if p.is_dir()
    ]))
    env["PATH"] = str(kit / "toolchain/bin") + ":" + env.get("PATH", "")
    return lean, env


def run(config: Any, timeout: int = 30) -> dict[str, Any]:
    wire = make_wire(config)
    lean, env = checked_environment()
    with tempfile.TemporaryDirectory(prefix="avoc-upgrade-") as directory:
        request = Path(directory) / "request.json"
        request.write_text(json.dumps(wire, ensure_ascii=False))
        command = [str(lean), "--run", str(ROOT / "tools/UpgradeMain.lean"), str(request)]
        started = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)
        elapsed = time.monotonic() - started
    if result.returncode != 0:
        raise RuntimeError(f"Lean evaluator rejected the request: {result.stderr or result.stdout}")
    output = json.loads(result.stdout)
    # A changed source/build during evaluation also invalidates this local report.
    checked_environment()
    output["execution"] = {
        "evaluator": "actual Lean UpgradeRuntime.execute",
        "seconds_in_evaluator_process": elapsed,
        "writes_to_research_store": False,
        "physical_cost_calibrated": False,
    }
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("configuration", type=Path)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    try:
        if not 1 <= args.timeout <= 120:
            raise ValueError("timeout must be between 1 and 120 seconds")
        if args.configuration.stat().st_size > 262144:
            raise ValueError("configuration size limit")
        config = json.loads(args.configuration.read_text(), object_pairs_hook=unique_object)
        print(json.dumps(run(config, args.timeout), indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
