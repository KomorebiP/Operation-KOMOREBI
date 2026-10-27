#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.reporting import code_files, tree_digest
from komorebi_neuralese.version import VERSION

IGNORED_PARTS = {"__pycache__", ".pytest_cache", ".git"}


def fail(message: str) -> None:
    raise SystemExit(f"PACKAGE_VERIFY_FAIL: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def included_files(include_manifest: bool) -> set[str]:
    output: set[str] = set()
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative == "SHA256SUMS.txt" or (relative == "MANIFEST.json" and not include_manifest):
            continue
        output.add(relative)
    return output


def verify_checksums() -> None:
    path = ROOT / "SHA256SUMS.txt"
    if not path.is_file():
        fail("SHA256SUMS.txt is missing")
    records: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, relative_text = line.split("  ", 1)
        except ValueError:
            fail("malformed checksum line")
        relative = Path(relative_text)
        if relative.is_absolute() or ".." in relative.parts or relative_text in records:
            fail(f"unsafe or duplicate checksum path: {relative_text}")
        target = ROOT / relative
        if not target.is_file() or sha256(target) != expected:
            fail(f"checksum mismatch: {relative_text}")
        records[relative_text] = expected
    expected_paths = included_files(include_manifest=True)
    if set(records) != expected_paths:
        fail(f"checksum set mismatch: missing={sorted(expected_paths-set(records))}, extra={sorted(set(records)-expected_paths)}")


def verify_manifest(code_digest: str, protocol_digest: str) -> dict:
    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != "komorebi.neuralese.package_manifest.v2" or manifest.get("version") != VERSION:
        fail("manifest schema or version mismatch")
    if manifest.get("scientific_code_digest") != code_digest or manifest.get("primary_protocol_digest") != protocol_digest:
        fail("manifest scientific digest mismatch")
    records = manifest.get("files")
    if not isinstance(records, list) or manifest.get("file_count") != len(records):
        fail("manifest file count mismatch")
    observed: set[str] = set()
    for record in records:
        relative = str(record.get("path", ""))
        if not relative or relative in observed:
            fail("manifest contains an empty or duplicate path")
        target = ROOT / relative
        if not target.is_file() or target.stat().st_size != record.get("size") or sha256(target) != record.get("sha256"):
            fail(f"manifest record mismatch: {relative}")
        observed.add(relative)
    if observed != included_files(include_manifest=False):
        fail("manifest payload set mismatch")
    return manifest


def verify_primary(code_digest: str, protocol_digest: str) -> dict:
    primary = ROOT / "results" / "v0.2.0" / "preregistered_primary"
    if (primary / "RUNNING.json").exists() or (primary / "FAILED.json").exists():
        fail("primary directory contains an incomplete-run marker")
    protocol_path = ROOT / "protocols" / "V0_2_PRIMARY.json"
    if protocol_path.read_bytes() != (primary / "PROTOCOL.json").read_bytes():
        fail("result protocol differs from the frozen protocol")
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    receipt = json.loads((primary / "RECEIPT.json").read_text(encoding="utf-8"))
    if receipt.get("status") != "complete" or not receipt.get("grid_complete"):
        fail("primary receipt is incomplete")
    if (receipt.get("package_version"), receipt.get("code_digest"), receipt.get("protocol_digest")) != (VERSION, code_digest, protocol_digest):
        fail("primary receipt digest mismatch")

    cells = {(arm, int(seed)) for arm in protocol["arms"] for seed in protocol["seeds"]}
    expected_records: set[str] = set()
    expected_checkpoints: set[str] = set()
    for arm, seed in sorted(cells):
        record_path = primary / "arms" / arm / f"seed_{seed}.json"
        checkpoint_path = primary / "checkpoints" / arm / f"seed_{seed}.pt"
        if not record_path.is_file() or not checkpoint_path.is_file():
            fail(f"missing primary cell: {arm}/{seed}")
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if (record.get("arm"), record.get("seed"), record.get("package_version"), record.get("code_digest"), record.get("protocol_digest")) != (arm, seed, VERSION, code_digest, protocol_digest):
            fail(f"primary cell identity or digest mismatch: {arm}/{seed}")
        expected_records.add(record_path.relative_to(primary).as_posix())
        expected_checkpoints.add(checkpoint_path.relative_to(primary).as_posix())
    actual_records = {path.relative_to(primary).as_posix() for path in (primary / "arms").glob("*/seed_*.json")}
    actual_checkpoints = {path.relative_to(primary).as_posix() for path in (primary / "checkpoints").glob("*/seed_*.pt")}
    if actual_records != expected_records or actual_checkpoints != expected_checkpoints:
        fail("primary arm-seed grid contains missing or unexpected cells")

    gates = json.loads((primary / "GATES.json").read_text(encoding="utf-8"))
    gate_ids = {gate["id"] for gate in protocol["gates"]}
    if set(gates.get("gates", {})) != gate_ids:
        fail("primary gate set mismatch")
    passed = sum(bool(value.get("passed")) for value in gates["gates"].values())
    failed = len(gates["gates"]) - passed
    if (passed, failed, gates.get("all_gates_passed"), receipt.get("scientific_gate_status"), receipt.get("all_gates_passed")) != (20, 6, False, "fail", False):
        fail("primary scientific outcome mismatch")

    split = json.loads((primary / "COORDINATE_SPLIT_AUDIT.json").read_text(encoding="utf-8"))
    if not split.get("passed") or any(split.get("pairwise_intersections", {}).values()) or split.get("digest") != receipt.get("coordinate_split_digest"):
        fail("coordinate split audit mismatch")
    expected_pairs = {tuple(pair) for pair in protocol["transport"]["seed_pairs"]}
    actual_pairs: set[tuple[int, int]] = set()
    for path in (primary / "transport").glob("*.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        actual_pairs.add((int(record["source_seed"]), int(record["target_seed"])))
        if record.get("arm") != "metric_composition" or record.get("code_digest") != code_digest or record.get("protocol_digest") != protocol_digest:
            fail(f"transport receipt mismatch: {path.name}")
    if actual_pairs != expected_pairs or receipt.get("transport_records") != len(expected_pairs):
        fail("transport pair set mismatch")
    replay = json.loads((primary / "REPRODUCIBILITY.json").read_text(encoding="utf-8"))
    if not replay.get("metrics_exactly_equal") or replay.get("max_parameter_absolute_difference") != 0.0:
        fail("reproducibility receipt failed")
    return {"cells": len(cells), "passed_gates": passed, "failed_gates": failed, "transport_pairs": len(expected_pairs)}


def main() -> int:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", str(ROOT / "tests")], cwd=ROOT, env=environment, check=True)
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    if project["project"]["version"] != VERSION:
        fail("pyproject and package version disagree")
    code_digest = tree_digest(ROOT, code_files(ROOT))
    protocol_path = ROOT / "protocols" / "V0_2_PRIMARY.json"
    protocol_digest = sha256(protocol_path)
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if protocol.get("expected_code_digest") != code_digest:
        fail("frozen protocol code digest mismatch")
    primary = verify_primary(code_digest, protocol_digest)
    releases = json.loads((ROOT / "PRIOR_RELEASES.json").read_text(encoding="utf-8"))
    prior = releases["releases"][0]
    if sha256(ROOT / prior["archive"]) != prior["sha256"] or prior["sha256"] != "2c215d33b0b3f4788da838337272c29cd3c662fbf4cfcd23bdb915432f2c91ba":
        fail("prior v0.1.1 archive hash mismatch")
    ledger = json.loads((ROOT / "EVIDENCE_LEDGER.json").read_text(encoding="utf-8"))
    if (ledger["primary"]["scientific_gate_status"], ledger["primary"]["passed_gate_count"], ledger["primary"]["failed_gate_count"]) != ("fail", 20, 6):
        fail("evidence ledger outcome mismatch")
    verify_checksums()
    manifest = verify_manifest(code_digest, protocol_digest)
    if manifest["primary_outcome"]["scientific_gate_status"] != "fail":
        fail("manifest does not preserve failed outcome")
    print(json.dumps({"status": "PACKAGE_VERIFY_PASS", "version": VERSION, "code_digest": code_digest, **primary}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
