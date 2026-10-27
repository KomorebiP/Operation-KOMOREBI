from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import verify_flat_connection as verifier
from verify_flat_connection import (
    AUTHOR,
    CONTRACT_SCHEMA,
    MANIFEST_SCHEMA,
    REGISTERED_DESIGN_FIELDS,
    VERSION,
    VerificationError,
    canonical_json_bytes,
    file_sha256,
    source_digest,
    verify_package,
    write_v5_manifest,
)


@pytest.fixture(autouse=True)
def _stub_expensive_runtime_replay(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests exercise the static layer; production CLI always deep-replays."""

    monkeypatch.setattr(
        verifier,
        "_verify_runtime_evidence",
        lambda *args, **kwargs: {
            "checkpoint_payloads_verified": 30,
            "evaluation_bank_reconstructed": True,
            "controls_reconstructed": True,
            "aggregate_recomputed": True,
            "adjudication_recomputed": True,
            "report_regenerated": True,
            "chart_regenerated": True,
            "anc4_self_check": "PASS",
        },
    )


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _registered_design(contract: dict[str, object]) -> dict[str, object]:
    return {key: contract[key] for key in REGISTERED_DESIGN_FIELDS}


def _seal_registered_design(contract: dict[str, object]) -> None:
    contract["registered_design_sha256"] = hashlib.sha256(
        canonical_json_bytes(_registered_design(contract))
    ).hexdigest()


def _seal_object(value: dict[str, object], key: str) -> None:
    unsigned = dict(value)
    unsigned.pop(key, None)
    value[key] = hashlib.sha256(canonical_json_bytes(unsigned)).hexdigest()


def _reseal_completion(directory: Path) -> None:
    result = _read_json(directory / "RESULTS.json")
    completion = _read_json(directory / "RUN_COMPLETE.json")
    completion["results_sha256"] = file_sha256(directory / "RESULTS.json")
    completion["report_sha256"] = file_sha256(directory / "REPORT.md")
    completion["chart_sha256"] = result["chart"]["sha256"]  # type: ignore[index]
    _write_json(directory / "RUN_COMPLETE.json", completion)


def _make_scientific_fail_package(root: Path) -> Path:
    root.mkdir()
    arms = [
        "polar_supervised",
        "polar_cr_v04",
        "polar_exact_flat",
        "polar_packet_flat",
        "polar_hybrid_flat",
        "polar_shuffled_packet",
    ]
    seeds = [401, 503, 607, 709, 811]
    pilot_profile = {
        "seeds": seeds,
        "steps": 2,
        "batch_size": 4,
        "diamonds_per_length": 2,
        "loops_per_stratum": 2,
        "diamond_lengths": [8, 9],
        "diamond_suffix_lengths": [4, 8],
        "loop_repeats": [1, 8, 32],
        "loop_suffix_lengths": [0, 8, 32],
        "deep_depths": [128],
        "deep_examples": 4,
        "causal_examples": 4,
    }
    preregistration = {
        "schema": "komorebi.flat_packet_connection.preregistration.v2",
        "version": VERSION,
        "author": AUTHOR,
        "arms": arms,
        "primary_arm": "polar_packet_flat",
        "pilot": {
            "seeds": seeds,
            "steps": 2,
            "batch_size": 4,
            "causal_examples_per_seed": 4,
            "deep_examples_per_depth_per_seed": 4,
            "diamond_examples_per_length": 2,
            "loop_examples_per_repeat_suffix_stratum": 2,
        },
        "thresholds": {"deep_128_pooled": 0.99},
        "numerical_contract": {
            "behavior_dtype": "float32",
            "threshold_equality": "fails",
        },
    }
    _write_json(root / "FLAT_CONNECTION_PREREGISTRATION.json", preregistration)
    (root / "run_flat_connection.py").write_text("VERSION = '0.5.0'\n", encoding="utf-8")
    current_source_digest, current_source_files = source_digest(root)
    preregistration_sha = file_sha256(root / "FLAT_CONNECTION_PREREGISTRATION.json")
    contract: dict[str, object] = {
        "schema": CONTRACT_SCHEMA,
        "version": VERSION,
        "author": AUTHOR,
        "source_digest": current_source_digest,
        "profile_name": "pilot",
        "arms": preregistration["arms"],
        "pilot_profile": pilot_profile,
        "thresholds": preregistration["thresholds"],
        "numerical_contract": preregistration["numerical_contract"],
        "preregistration_sha256": preregistration_sha,
    }
    _seal_registered_design(contract)
    _write_json(root / "FLAT_CONNECTION_CONTRACT.json", contract)

    directory = root / "results" / "flat_connection_pilot"
    checkpoint_dir = directory / "checkpoints"
    checkpoint_dir.mkdir(parents=True)
    checkpoint_rows: list[dict[str, object]] = []
    training: dict[str, object] = {}
    for seed in seeds:
        training[str(seed)] = {}
        for arm in arms:
            path = checkpoint_dir / f"{arm}_seed{seed}.pt"
            prefix = path.stem
            with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
                archive.writestr(f"{prefix}/data.pkl", b"fixture-only")
                archive.writestr(f"{prefix}/version", b"3\n")
                archive.writestr(f"{prefix}/byteorder", b"little")
            state_digest = hashlib.sha256(f"state:{seed}:{arm}".encode()).hexdigest()
            checkpoint_rows.append(
                {
                    "path": f"checkpoints/{arm}_seed{seed}.pt",
                    "sha256": file_sha256(path),
                    "arm": arm,
                    "seed": seed,
                    "state_digest": state_digest,
                }
            )
            final_loss = 0.5
            training[str(seed)][arm] = {  # type: ignore[index]
                "config": {"seed": seed},
                "trajectory": [{"step": 2, "loss": final_loss}],
                "elapsed_seconds": 0.01,
                "final_loss": final_loss,
                "parameter_count": 12,
                "initial_state_digest": hashlib.sha256(
                    f"initial:{seed}".encode()
                ).hexdigest(),
                "final_state_digest": state_digest,
                "episode_stream_digest": hashlib.sha256(
                    f"episode:{seed}".encode()
                ).hexdigest(),
                "terminal_proposal_stream_digest": hashlib.sha256(
                    f"proposal:{seed}".encode()
                ).hexdigest(),
                "relation_schedule_digest": hashlib.sha256(
                    f"relation:{seed}:{arm}".encode()
                ).hexdigest(),
                "terminal_proposal_count": 8,
                "terminal_candidates_accepted": 5,
                "terminal_candidates_rejected": 3,
            }
    checkpoint_rows.sort(key=lambda row: (row["seed"], row["arm"]))
    checkpoint_seal: dict[str, object] = {
        "schema": "komorebi.flat_packet_connection.checkpoint_seal.v1",
        "version": VERSION,
        "source_digest": current_source_digest,
        "count": len(checkpoint_rows),
        "checkpoints": checkpoint_rows,
    }
    _seal_object(checkpoint_seal, "seal_sha256")
    _write_json(directory / "CHECKPOINT_SEAL.json", checkpoint_seal)

    bank: dict[str, object] = {
        "schema": "komorebi.flat_packet_connection.eval_bank.v1",
        "audit_bank": {"cases": [1, 2, 3]},
        "causal_banks": {"401": {"seed": 88}},
        "deep_banks": {"401": {"d4": {"128": 99}}},
    }
    _seal_object(bank, "fingerprint")
    _write_json(directory / "EVAL_BANK.json", bank)

    gates = {
        "execution_integrity": "PASS",
        "assay_validity": "PASS",
        "scientific_flatness": "FAIL",
        "scientific_connection": "NOT_EVALUATED",
        "ambient_necessity": "SEPARATE_CALIBRATION_ONLY",
        "control_gates": {"exact_behavior": True, "collapse_rejected": True},
        "integrity_checks": {
            "record_grid_exact": True,
            "aggregate_recomputed_exact": True,
        },
        "scientific_checks": {
            "deep_128": {
                "observed": {"pooled": 0.75},
                "threshold": {"pooled_min": 0.99},
                "pass": False,
            },
            "exact_arm_full_flatness_secondary": {
                "observed": 0.0,
                "threshold": 0.1,
                "pass": True,
            },
            "complete_registered_evaluation": {
                "observed": {"record_grid_exact": True},
                "threshold": "all integrity checks true",
                "pass": True,
            },
        },
        "all_primary_checks_pass": False,
    }
    _write_json(directory / "GATES.json", gates)
    _write_json(
        directory / "RUN_STARTED.json",
        {
            "schema": "komorebi.flat_packet_connection.run_started.v1",
            "version": VERSION,
            "profile": "pilot",
            "run_mode": "fresh_pilot",
            "source_digest": current_source_digest,
            "preregistration_sha256": preregistration_sha,
            "contract_sha256": file_sha256(root / "FLAT_CONNECTION_CONTRACT.json"),
            "runtime": {"device": "cpu"},
        },
    )
    chart = directory / "flat_connection_summary.png"
    chart.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
    (directory / "REPORT.md").write_text("# Retained scientific failure\n", encoding="utf-8")
    result = {
        "schema": "komorebi.flat_packet_connection.result.v1",
        "version": VERSION,
        "profile": "pilot",
        "run_mode": "fresh_pilot",
        "config": contract["pilot_profile"],
        "thresholds": contract["thresholds"],
        "source_digest": current_source_digest,
        "source_files": current_source_files,
        "preregistration_sha256": preregistration_sha,
        "contract_sha256": file_sha256(root / "FLAT_CONNECTION_CONTRACT.json"),
        "checkpoint_seal": checkpoint_seal,
        "evaluation_bank_fingerprint": bank["fingerprint"],
        "training": training,
        "controls": {},
        "records": {},
        "aggregate": {},
        "status": gates,
        "runtime": {"device": "cpu"},
        "phase_seconds": {"training": 0.1, "evaluation": 0.1, "total": 0.2},
        "chart": {
            "path": chart.name,
            "sha256": file_sha256(chart),
        },
    }
    _write_json(directory / "RESULTS.json", result)
    _write_json(
        directory / "RUN_COMPLETE.json",
        {
            "schema": "komorebi.flat_packet_connection.run_complete.v1",
            "version": VERSION,
            "profile": "pilot",
            "run_mode": "fresh_pilot",
            "execution_integrity": "PASS",
            "assay_validity": "PASS",
            "scientific_flatness": "FAIL",
            "contract_sha256": file_sha256(root / "FLAT_CONNECTION_CONTRACT.json"),
            "results_sha256": file_sha256(directory / "RESULTS.json"),
            "report_sha256": file_sha256(directory / "REPORT.md"),
            "chart_sha256": file_sha256(chart),
        },
    )
    write_v5_manifest(root)
    return directory


@pytest.fixture
def valid_package(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "package"
    return root, _make_scientific_fail_package(root)


def test_valid_scientific_fail_package_verifies(
    valid_package: tuple[Path, Path],
) -> None:
    root, _ = valid_package
    receipt = verify_package(root)
    assert receipt["status"] == "PASS"
    assert receipt["scientific_failures_retained"] == 1
    assert receipt["runs"][0]["scientific_flatness"] == "FAIL"
    assert receipt["runs"][0]["execution_integrity"] == "PASS"


@pytest.mark.parametrize(
    "relative",
    (
        "__pycache__/poison.pyc",
        "src/pkg/__pycache__/poison.pyc",
        ".pytest_cache/state",
    ),
)
def test_cache_and_bytecode_are_rejected(
    valid_package: tuple[Path, Path],
    relative: str,
) -> None:
    root, _ = valid_package
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"cache")
    with pytest.raises(VerificationError, match="cache/bytecode"):
        verify_package(root)


def test_manifest_rejects_uncovered_and_tampered_files(
    valid_package: tuple[Path, Path],
) -> None:
    root, _ = valid_package
    (root / "uncovered.bin").write_bytes(b"not in manifest")
    with pytest.raises(VerificationError, match="coverage mismatch"):
        verify_package(root)
    (root / "uncovered.bin").unlink()
    (root / "run_flat_connection.py").write_text("tampered\n", encoding="utf-8")
    with pytest.raises(VerificationError, match="manifest (size|hash) mismatch"):
        verify_package(root)


def test_manifest_schema_and_checksum_rendering_are_strict(
    valid_package: tuple[Path, Path],
) -> None:
    root, _ = valid_package
    manifest = _read_json(root / "MANIFEST.json")
    manifest["schema"] = "komorebi.neuralese.package_manifest.v4"
    _write_json(root / "MANIFEST.json", manifest)
    with pytest.raises(VerificationError, match="manifest schema mismatch"):
        verify_package(root)

    manifest["schema"] = MANIFEST_SCHEMA
    _write_json(root / "MANIFEST.json", manifest)
    (root / "SHA256SUMS.txt").write_text(
        (root / "SHA256SUMS.txt").read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )
    with pytest.raises(VerificationError, match="not canonical"):
        verify_package(root)


def test_contract_source_preregistration_and_design_seals_are_enforced(
    valid_package: tuple[Path, Path],
) -> None:
    root, _ = valid_package
    contract_path = root / "FLAT_CONNECTION_CONTRACT.json"
    contract = _read_json(contract_path)
    contract["source_digest"] = "0" * 64
    _write_json(contract_path, contract)
    write_v5_manifest(root)
    with pytest.raises(VerificationError, match="source_digest"):
        verify_package(root)

    contract = _read_json(contract_path)
    current_source, _ = source_digest(root)
    contract["source_digest"] = current_source
    contract["preregistration_sha256"] = "1" * 64
    _seal_registered_design(contract)
    _write_json(contract_path, contract)
    write_v5_manifest(root)
    with pytest.raises(VerificationError, match="preregistration digest"):
        verify_package(root)

    contract["preregistration_sha256"] = file_sha256(
        root / "FLAT_CONNECTION_PREREGISTRATION.json"
    )
    contract["thresholds"] = {"deep_128_pooled": 0.5}
    # Deliberately retain the old registered-design digest.
    _write_json(contract_path, contract)
    write_v5_manifest(root)
    with pytest.raises(VerificationError, match="threshold mismatch|registered-design"):
        verify_package(root)


def test_pilot_requires_contract(valid_package: tuple[Path, Path]) -> None:
    root, _ = valid_package
    (root / "FLAT_CONNECTION_CONTRACT.json").unlink()
    write_v5_manifest(root)
    with pytest.raises(VerificationError, match="canonical package requires"):
        verify_package(root)


def test_evaluation_bank_fingerprint_is_enforced(
    valid_package: tuple[Path, Path],
) -> None:
    root, directory = valid_package
    bank_path = directory / "EVAL_BANK.json"
    bank = _read_json(bank_path)
    bank["audit_bank"] = {"cases": [999]}
    _write_json(bank_path, bank)
    write_v5_manifest(root)
    with pytest.raises(VerificationError, match="evaluation bank self-seal"):
        verify_package(root)


def test_checkpoint_file_hash_and_seal_are_enforced(
    valid_package: tuple[Path, Path],
) -> None:
    root, directory = valid_package
    checkpoint = directory / "checkpoints" / "polar_packet_flat_seed401.pt"
    checkpoint.write_bytes(b"different checkpoint")
    # Re-seal every outer receipt so rejection depends on checkpoint-content
    # validation rather than merely noticing a stale enclosing hash.
    seal_path = directory / "CHECKPOINT_SEAL.json"
    seal = _read_json(seal_path)
    for row in seal["checkpoints"]:  # type: ignore[index]
        if row["path"] == "checkpoints/polar_packet_flat_seed401.pt":
            row["sha256"] = file_sha256(checkpoint)
    _seal_object(seal, "seal_sha256")
    _write_json(seal_path, seal)
    result = _read_json(directory / "RESULTS.json")
    result["checkpoint_seal"] = seal
    _write_json(directory / "RESULTS.json", result)
    _reseal_completion(directory)
    write_v5_manifest(root)
    with pytest.raises(
        VerificationError,
        match="torch ZIP checkpoint",
    ):
        verify_package(root)

    # Restore the package, then attack the seal itself while keeping the
    # package-level manifest internally consistent.
    root2 = root.parent / "package2"
    directory2 = _make_scientific_fail_package(root2)
    seal_path = directory2 / "CHECKPOINT_SEAL.json"
    seal = _read_json(seal_path)
    seal["count"] = 2
    _write_json(seal_path, seal)
    result = _read_json(directory2 / "RESULTS.json")
    result["checkpoint_seal"] = seal
    _write_json(directory2 / "RESULTS.json", result)
    _reseal_completion(directory2)
    write_v5_manifest(root2)
    with pytest.raises(VerificationError, match="checkpoint seal self-seal|count mismatch"):
        verify_package(root2)


def test_result_schema_and_cross_artifact_status_must_match(
    valid_package: tuple[Path, Path],
) -> None:
    root, directory = valid_package
    result = _read_json(directory / "RESULTS.json")
    result["schema"] = "wrong.result.schema"
    _write_json(directory / "RESULTS.json", result)
    _reseal_completion(directory)
    write_v5_manifest(root)
    with pytest.raises(VerificationError, match="RESULTS schema mismatch"):
        verify_package(root)

    root2 = root.parent / "package2"
    directory2 = _make_scientific_fail_package(root2)
    gates = _read_json(directory2 / "GATES.json")
    gates["scientific_flatness"] = "PASS"
    _write_json(directory2 / "GATES.json", gates)
    result = _read_json(directory2 / "RESULTS.json")
    result["status"] = copy.deepcopy(gates)
    _write_json(directory2 / "RESULTS.json", result)
    completion = _read_json(directory2 / "RUN_COMPLETE.json")
    completion["scientific_flatness"] = "PASS"
    _write_json(directory2 / "RUN_COMPLETE.json", completion)
    _reseal_completion(directory2)
    write_v5_manifest(root2)
    with pytest.raises(VerificationError, match="scientific-flatness status"):
        verify_package(root2)


def test_duplicate_json_keys_are_rejected(
    valid_package: tuple[Path, Path],
) -> None:
    root, _ = valid_package
    prereg = root / "FLAT_CONNECTION_PREREGISTRATION.json"
    prereg.write_text('{"schema":"x","schema":"y"}\n', encoding="utf-8")
    write_v5_manifest(root)
    with pytest.raises(VerificationError, match="duplicate JSON object key"):
        verify_package(root)


def test_zero_official_runs_are_rejected(
    valid_package: tuple[Path, Path],
) -> None:
    root, directory = valid_package
    directory.rename(root / "results" / "flat_connection_pilot_developmental")
    write_v5_manifest(root)
    with pytest.raises(VerificationError, match="canonical pilot directory is missing"):
        verify_package(root)


@pytest.mark.parametrize(
    ("status_key", "gate_key", "expected_message"),
    (
        ("execution_integrity", "integrity_checks", "execution integrity did not pass"),
        ("assay_validity", "control_gates", "assay validity did not pass"),
    ),
)
def test_failed_execution_or_assay_is_not_a_valid_scientific_package(
    valid_package: tuple[Path, Path],
    status_key: str,
    gate_key: str,
    expected_message: str,
) -> None:
    root, directory = valid_package
    gates = _read_json(directory / "GATES.json")
    gates[status_key] = "FAIL"
    gates["scientific_flatness"] = "NOT_EVALUATED"
    for key in gates[gate_key]:  # type: ignore[index]
        gates[gate_key][key] = False  # type: ignore[index]
    _write_json(directory / "GATES.json", gates)
    result = _read_json(directory / "RESULTS.json")
    result["status"] = copy.deepcopy(gates)
    _write_json(directory / "RESULTS.json", result)
    completion = _read_json(directory / "RUN_COMPLETE.json")
    completion[status_key] = "FAIL"
    completion["scientific_flatness"] = "NOT_EVALUATED"
    _write_json(directory / "RUN_COMPLETE.json", completion)
    _reseal_completion(directory)
    write_v5_manifest(root)
    with pytest.raises(VerificationError, match=expected_message):
        verify_package(root)
