#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.ambient_eval import (
    episode_bank_receipts,
    episode_contract,
    make_episode_bank,
)
from komorebi_neuralese.reporting import source_files, tree_digest


PARENT_SOURCE_DIGEST = "cb5d6b1eccb7b9e05cbbe16637dac90cc1334a469fb9add6472238affa61210e"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def load_json(relative: str) -> dict:
    path = ROOT / relative
    if not path.exists():
        raise SystemExit(f"Missing required artifact: {relative}")
    try:
        return json.loads(
            path.read_text(encoding="utf-8"), parse_constant=_reject_json_constant
        )
    except (json.JSONDecodeError, ValueError) as error:
        raise SystemExit(f"Invalid strict JSON: {relative}: {error}") from error


def verify_parent_completion(directory: str, expected_schema: str) -> dict:
    completion = load_json(f"{directory}/RUN_COMPLETE.json")
    if completion.get("schema") != expected_schema:
        raise SystemExit(f"Parent completion schema mismatch: {directory}")
    if completion.get("profile") != "pilot":
        raise SystemExit(f"Parent completion profile mismatch: {directory}")
    if not completion.get("all_gates_passed", False):
        raise SystemExit(f"Parent developmental gates did not pass: {directory}")
    if completion.get("evaluation_source_digest") != PARENT_SOURCE_DIGEST:
        raise SystemExit(f"Parent lineage digest mismatch: {directory}")
    for key, filename in (("results_sha256", "RESULTS.json"), ("report_sha256", "REPORT.md")):
        observed = file_sha256(ROOT / directory / filename)
        if completion.get(key) != observed:
            raise SystemExit(f"Parent completion hash mismatch: {directory}/{filename}")
    return completion


def verify_ambient_completion(current_source_digest: str) -> dict:
    directory = "results/ambient_pilot"
    completion = load_json(f"{directory}/RUN_COMPLETE.json")
    expected = {
        "schema": "komorebi.neuralese.ambient_diagnostics.completion.v1",
        "version": "0.3.0",
        "profile": "pilot",
        "execution_status": "PASS",
        "assay_status": "PASS",
        "full_developmental_claim": "NOT_CLAIMED_POSTHOC",
    }
    for key, value in expected.items():
        if completion.get(key) != value:
            raise SystemExit(f"Ambient completion mismatch for {key}: {completion.get(key)!r}")
    for key in ("mechanism_reference_status", "capability_reference_status"):
        if completion.get(key) not in {"PASS", "FAIL"}:
            raise SystemExit(f"Ambient completion omitted an evaluable {key}")
    for key, filename in (
        ("results_sha256", "RESULTS.json"),
        ("gates_sha256", "GATES.json"),
        ("report_sha256", "REPORT.md"),
        ("environment_sha256", "ENVIRONMENT.json"),
    ):
        observed = file_sha256(ROOT / directory / filename)
        if completion.get(key) != observed:
            raise SystemExit(f"Ambient completion hash mismatch: {directory}/{filename}")
    if completion.get("evaluation_source_digest") != current_source_digest:
        raise SystemExit("Ambient pilot was not evaluated from the packaged source")

    result = load_json(f"{directory}/RESULTS.json")
    gates = load_json(f"{directory}/GATES.json")
    contract = load_json("AMBIENT_PREREGISTRATION.json")
    environment = load_json(f"{directory}/ENVIRONMENT.json")
    if environment.get("schema") != "komorebi.neuralese.ambient_diagnostics.environment.v1":
        raise SystemExit("Ambient environment schema mismatch")
    if environment.get("device") != "cpu" or not environment.get(
        "deterministic_algorithms", False
    ):
        raise SystemExit("Ambient environment did not record deterministic CPU execution")
    if result.get("schema") != "komorebi.neuralese.ambient_diagnostics.result.v1":
        raise SystemExit("Ambient result schema mismatch")
    if result.get("version") != "0.3.0" or result.get("profile") != "pilot":
        raise SystemExit("Ambient result version/profile mismatch")
    expected_study_status = "developmental_posthoc_frozen_checkpoint_diagnostics"
    if result.get("study_status") != expected_study_status:
        raise SystemExit("Ambient result study status mismatch")
    if result.get("source_digest") != current_source_digest:
        raise SystemExit("Ambient result source digest mismatch")
    if result.get("contract_schema") != contract.get("schema"):
        raise SystemExit("Ambient result contract schema mismatch")
    if result.get("contract_version") != contract.get("version"):
        raise SystemExit("Ambient result contract version mismatch")
    if result.get("contract_status") != contract.get("status"):
        raise SystemExit("Ambient result contract status mismatch")
    contract_sha256 = file_sha256(ROOT / "AMBIENT_PREREGISTRATION.json")
    if result.get("contract_sha256") != contract_sha256:
        raise SystemExit("Ambient result contract hash mismatch")
    for key, expected_value in (
        ("contract_schema", contract.get("schema")),
        ("contract_version", contract.get("version")),
        ("contract_status", contract.get("status")),
        ("contract_sha256", contract_sha256),
    ):
        if completion.get(key) != expected_value:
            raise SystemExit(f"Ambient completion contract mismatch for {key}")
    if result.get("implementation_contract") != contract.get("profiles", {}).get("pilot"):
        raise SystemExit("Ambient result does not match the frozen pilot contract")
    if result.get("adjudication") != gates:
        raise SystemExit("Ambient GATES.json disagrees with RESULTS.json")
    if gates.get("study_status") != expected_study_status:
        raise SystemExit("Ambient gates study status mismatch")
    if gates.get("execution_status") != "PASS" or gates.get("assay_status") != "PASS":
        raise SystemExit("Ambient gates do not record a valid completed assay")
    if gates.get("assay_valid") is not True:
        raise SystemExit("Ambient gates omitted assay validity")
    gate_contracts = (
        ("assay_gates", "assay_gates"),
        ("mechanism_reference_gates", "learned_mechanism_reference_gates"),
        ("capability_reference_gates", "capability_reference_gates"),
    )
    for emitted_key, contract_key in gate_contracts:
        criteria = {name: gate["criterion"] for name, gate in gates[emitted_key].items()}
        if criteria != contract.get(contract_key):
            raise SystemExit(f"Ambient gate criteria mismatch for {emitted_key}")
    for key in (
        "execution_status",
        "assay_status",
        "mechanism_reference_status",
        "capability_reference_status",
        "full_developmental_claim",
    ):
        if completion.get(key) != gates.get(key):
            raise SystemExit(f"Ambient completion and gates disagree for {key}")

    parent = load_json("results/projective_pilot/RESULTS.json")
    for seed in contract["profiles"]["pilot"]["model_seeds"]:
        receipt = result.get("checkpoint_receipts", {}).get(str(seed))
        parent_record = parent.get("records", {}).get(str(seed), {}).get("projective", {})
        parent_checkpoint = parent_record.get("checkpoint", {})
        parent_config = parent_record.get("training", {}).get("config")
        if not isinstance(receipt, dict) or not isinstance(parent_config, dict):
            raise SystemExit(f"Missing checkpoint provenance for seed {seed}")
        if receipt.get("sha256") != parent_checkpoint.get("sha256"):
            raise SystemExit(f"Checkpoint receipt hash mismatch for seed {seed}")
        if receipt.get("schema") != parent_checkpoint.get("schema"):
            raise SystemExit(f"Checkpoint receipt schema mismatch for seed {seed}")
        if receipt.get("config") != parent_config:
            raise SystemExit(f"Checkpoint receipt config mismatch for seed {seed}")

    profile = contract["profiles"]["pilot"]
    for family in profile["families"]:
        bank = make_episode_bank(
            contexts=profile["contexts_per_family"],
            length=max(profile["prefixes"]),
            family=family,
            seed=profile["bank_seed"],
        )
        if result.get("bank_receipts", {}).get(family) != episode_bank_receipts(bank):
            raise SystemExit(f"Deterministic bank receipt mismatch: {family}")
        if result.get("bank_contracts", {}).get(family) != episode_contract(bank):
            raise SystemExit(f"Deterministic bank contract mismatch: {family}")
    return completion


def verify_manifest() -> dict:
    manifest = load_json("MANIFEST.json")
    if manifest.get("schema") != "komorebi.neuralese.package_manifest.v3":
        raise SystemExit("Manifest schema mismatch")
    if manifest.get("version") != "0.3.0":
        raise SystemExit("Manifest version mismatch")
    records = manifest.get("files", [])
    if manifest.get("file_count") != len(records):
        raise SystemExit("Manifest file count mismatch")
    paths = [record.get("path") for record in records]
    if any(not isinstance(path, str) for path in paths) or len(paths) != len(set(paths)):
        raise SystemExit("Manifest contains invalid or duplicate paths")
    sum_lines = [
        line
        for line in (ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
        if line
    ]
    expected_sums = {record["path"]: record["sha256"] for record in records}
    parsed_sums: dict[str, str] = {}
    for line in sum_lines:
        expected, relative = line.split("  ", 1)
        if relative in parsed_sums:
            raise SystemExit(f"Duplicate SHA256SUMS path: {relative}")
        parsed_sums[relative] = expected
    if len(sum_lines) != len(records):
        raise SystemExit("SHA256SUMS line count mismatch")
    if parsed_sums != expected_sums:
        raise SystemExit("SHA256SUMS and MANIFEST disagree")
    for record in records:
        path = ROOT / record["path"]
        if not path.exists():
            raise SystemExit(f"Manifest file missing: {record['path']}")
        if path.stat().st_size != record["size"]:
            raise SystemExit(f"Manifest size mismatch: {record['path']}")
        if file_sha256(path) != record["sha256"]:
            raise SystemExit(f"Checksum mismatch: {record['path']}")
    actual_paths: set[str] = set()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.name in {"MANIFEST.json", "SHA256SUMS.txt"}:
            continue
        if "__pycache__" in path.parts or ".pytest_cache" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith("results/local/"):
            continue
        actual_paths.add(relative)
    if set(paths) != actual_paths:
        missing = sorted(actual_paths - set(paths))
        extra = sorted(set(paths) - actual_paths)
        raise SystemExit(f"Manifest path-set mismatch; missing={missing}, extra={extra}")
    return manifest


def main() -> int:
    manifest = verify_manifest()
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(ROOT / "tests")],
        cwd=ROOT,
        check=True,
    )

    legacy = load_json("results/pilot/RUN_COMPLETE.json")
    if (
        legacy.get("schema") != "komorebi.neuralese.run_complete.v1"
        or legacy.get("profile") != "pilot"
        or not legacy.get("all_development_gates_passed", False)
    ):
        raise SystemExit("Legacy parent pilot is incomplete")

    verify_parent_completion(
        "results/stability_pilot", "komorebi.neuralese.stable_quotient.completion.v1"
    )
    verify_parent_completion(
        "results/projective_pilot", "komorebi.neuralese.projective_training.completion.v1"
    )
    current_source_digest = tree_digest(ROOT, source_files(ROOT))
    ambient = verify_ambient_completion(current_source_digest)

    print(
        json.dumps(
            {
                "status": "PACKAGE_VERIFY_PASS",
                "version": "0.3.0",
                "manifest_files": manifest["file_count"],
                "tests": "passed",
                "parent_lineage": "verified",
                "ambient_assay": ambient["assay_status"],
                "ambient_mechanism_reference": ambient["mechanism_reference_status"],
                "ambient_capability_reference": ambient["capability_reference_status"],
                "source_digest": current_source_digest,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
