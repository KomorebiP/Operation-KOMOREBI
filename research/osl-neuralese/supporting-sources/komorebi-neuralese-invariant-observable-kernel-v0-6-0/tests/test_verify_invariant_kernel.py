from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest
import torch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import verify_invariant_kernel as verifier
from verify_invariant_kernel import (
    AUTHOR,
    CHECKPOINT_SCHEMA,
    CHECKPOINT_SEAL_SCHEMA,
    COMPLETION_SCHEMA,
    EVAL_BANK_SCHEMA,
    GATES_SCHEMA,
    PRIMARY_ARMS,
    PREREGISTRATION_SCHEMA,
    PLAN_VERSION,
    RECORD_SCHEMA,
    RESULT_SCHEMA,
    STARTED_SCHEMA,
    VERSION,
    VerificationError,
    canonical_json_bytes,
    canonical_object_sha256,
    file_sha256,
    source_digest,
    verify_package,
)


class UnsafeCheckpointValue:
    """Pickle-global sentinel that a weights-only load must reject."""

    pass


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _seal(value: dict[str, object], key: str) -> None:
    unsigned = dict(value)
    unsigned.pop(key, None)
    value[key] = canonical_object_sha256(unsigned)


def _identity(schema: str, source: str, preregistration: str) -> dict[str, object]:
    return {
        "schema": schema,
        "version": VERSION,
        "source_digest": source,
        "preregistration_sha256": preregistration,
    }


def _relation_exposure() -> dict[str, object]:
    return {
        "selection": "first_n_accepted_rows_without_replacement",
        "contexts_per_step": 8,
        "cells_per_context": 9,
        "cells_per_step_total": 72,
        "aggregation": "mean_over_contexts_and_cells_not_sum",
        "shared_across_arms": True,
    }


def _metadata(arm: str, seed: int, state_digest: str) -> dict[str, object]:
    paired_names = {"episode", "proposal", "relation", "firewall", "construction"}
    digest = lambda name: hashlib.sha256(
        f"{name}:{seed}".encode()
        if name in paired_names
        else f"{name}:{arm}:{seed}".encode()
    ).hexdigest()
    hard = arm.startswith("hard_kernel")
    model_class = verifier.EXPECTED_MODEL_CLASSES[arm]
    ambient_digest = digest("ambient") if hard else None
    return {
        "plan_version": PLAN_VERSION,
        "arm": copy.deepcopy(verifier.ARM_METADATA[arm]),
        "config": {
            "seed": seed,
            "steps": 2,
            "batch_size": 4,
            "train_max_length": 4,
            "hidden_dim": 12,
            "learning_rate": 2e-3,
            "weight_decay": 1e-6,
            "grad_clip": 5.0,
            "warmup_steps": 200,
            "auxiliary_delay_steps": 0,
            "auxiliary_ramp_end_step": 2,
            "auxiliary_contexts": 8,
            "construction_words_per_step": 4,
            "relation_cells_per_step": 9,
            "episode_seed_base": 50_000,
            "gauge_seed_base": 60_700,
            "ambient_seed_base": 61_700,
            "checkpoints": 9,
            "device": "cpu",
            "base_weights": {
                "construction_ce": 0.25,
                "anchor": 0.01,
                "composition": 0.10,
                "margin": 0.10,
                "conformal": 0.05,
                "switched_gain": 0.02,
                "delayed_return": 0.05,
            },
            "weights": {
                "exact_flatness": 0.3,
                "observer_anchor_geometry": 0.1,
                "observer_centered_readout": 1.0,
                "observer_intertwining": 10.0,
                "observer_semantic_relation": 0.3,
                "hard_semantic_flatness": 0.3,
            },
        },
        "model_class": model_class,
        "parameter_count": 2,
        "trainable_parameter_count": 2,
        "initial_state_digest": digest("initial"),
        "core_initial_state_digest": digest("core"),
        "final_state_digest": state_digest,
        "episode_stream_digest": digest("episode"),
        "terminal_proposal_stream_digest": digest("proposal"),
        "relation_schedule_digest": digest("relation"),
        "terminal_firewall_policy_digest": digest("firewall"),
        "terminal_counts": {
            "proposals": 9,
            "accepted": 5,
            "rejected": 4,
            "identity_rejections": 2,
            "r2_rejections": 2,
        },
        "construction": {"digest": digest("construction"), "words": [[0], [1]]},
        "ambient_encoder": {
            "frozen_random_dormant": hard,
            "initial_digest": ambient_digest,
            "final_digest": ambient_digest,
        },
        "hard_anchor_contract": (
            "orthogonal_anchor_completion_via_common_logit_gauge" if hard else None
        ),
        "auxiliary_schedule": {
            "delay_steps": 0,
            "ramp_end_step": 2,
            "base_warmup_steps": 200,
            "base_warmup_is_independent": True,
        },
        "relation_exposure": _relation_exposure(),
        "claim_boundary": {
            "explicit_pressure_only": True,
            "spontaneous_emergence": False,
            "anchor_geometry_is_supervised": arm == "learned_intertwiner",
            "observer_constructs_recurrence": False,
            "learned_intertwiner_projective_normalization": False,
            "ambient_fiber_is_useful_memory": False,
        },
    }


def _make_run(root: Path, profile: str = "screen") -> Path:
    root.mkdir()
    profiles = {
        "smoke": {"seeds": [73], "steps": 2, "batch_size": 4, "auxiliary_delay_steps": 0, "auxiliary_ramp_end_step": 2, "auxiliary_contexts": 8},
        "screen": {"seeds": [947], "steps": 2, "batch_size": 4, "auxiliary_delay_steps": 0, "auxiliary_ramp_end_step": 2, "auxiliary_contexts": 8},
        "pilot": {"seeds": [1009, 1217], "steps": 2, "batch_size": 4, "auxiliary_delay_steps": 0, "auxiliary_ramp_end_step": 2, "auxiliary_contexts": 8},
    }
    preregistration = {
        "schema": PREREGISTRATION_SCHEMA,
        "version": VERSION,
        "author": AUTHOR,
        "training_plan_version": PLAN_VERSION,
        "arms": [{"name": arm} for arm in PRIMARY_ARMS],
        "profiles": profiles,
        "decomposition_contract": {"hidden_dimension": 12},
        "loss_contract": {
            "warmup_steps": 200,
            "full_space_relation_weight": 0.3,
            "hard_semantic_relation_weight": 0.3,
            "relation_exposure": _relation_exposure(),
            "learned_intertwiner": {
                "simplex_gram_weight": 0.1,
                "centered_readout_weight": 1.0,
                "intertwining_weight": 10.0,
                "semantic_relation_weight": 0.3,
            },
        },
    }
    _write_json(root / "INVARIANT_KERNEL_PREREGISTRATION.json", preregistration)
    (root / "run_invariant_kernel.py").write_text("VERSION = '0.6.0'\n", encoding="utf-8")
    (root / "src.py").write_text("VALUE = 6\n", encoding="utf-8")
    source_sha, source_files = source_digest(root)
    prereg_sha = file_sha256(root / "INVARIANT_KERNEL_PREREGISTRATION.json")
    seeds = profiles[profile]["seeds"]
    run_mode = "developmental" if profile in {"smoke", "screen"} else "fresh_pilot"
    directory = root / "results" / f"invariant_kernel_{profile}"
    checkpoint_dir = directory / "checkpoints"
    record_dir = directory / "records"
    checkpoint_dir.mkdir(parents=True)
    record_dir.mkdir()

    started = _identity(STARTED_SCHEMA, source_sha, prereg_sha)
    started.update({"profile": profile, "run_mode": run_mode, "runtime": {"device": "cpu"}})
    _write_json(directory / "RUN_STARTED.json", started)

    checkpoint_rows: list[dict[str, object]] = []
    record_rows: list[dict[str, object]] = []
    record_tree: dict[str, dict[str, object]] = {str(seed): {} for seed in seeds}
    training_tree: dict[str, dict[str, object]] = {str(seed): {} for seed in seeds}
    for seed in seeds:
        for arm_index, arm in enumerate(PRIMARY_ARMS):
            state = {
                "bias": torch.tensor([seed / 1000.0], dtype=torch.float32),
                "weight": torch.tensor([[float(arm_index), 1.0]], dtype=torch.float32),
            }
            state_digest = verifier._state_dict_digest(state, torch)
            metadata = _metadata(arm, seed, state_digest)
            payload = {
                "schema": CHECKPOINT_SCHEMA,
                "version": VERSION,
                "arm": arm,
                "seed": seed,
                "config": metadata["config"],
                "model_class": metadata["model_class"],
                "state_dict": state,
                "initial_state_digest": metadata["initial_state_digest"],
                "final_state_digest": metadata["final_state_digest"],
                "training_metadata": metadata,
                "source_digest": source_sha,
                "preregistration_sha256": prereg_sha,
            }
            checkpoint_path = checkpoint_dir / f"{arm}_seed{seed}.pt"
            torch.save(payload, checkpoint_path)
            checkpoint_rows.append(
                {
                    "path": f"checkpoints/{arm}_seed{seed}.pt",
                    "sha256": file_sha256(checkpoint_path),
                    "arm": arm,
                    "seed": seed,
                    "state_digest": state_digest,
                }
            )
            counts = metadata["terminal_counts"]
            training_tree[str(seed)][arm] = {
                "config": metadata["config"],
                "trajectory": [
                    {
                        "step": 1,
                        "length": 1,
                        "loss": 0.6,
                        "terminal_loss": 0.4,
                        "construction_ce_loss": 0.2,
                        "legacy_composition_loss": 0.0,
                        "legacy_delayed_return_loss": 0.0,
                        "exact_flatness_loss": 0.0,
                        "observer_anchor_geometry_loss": 0.0,
                        "observer_centered_readout_loss": 0.0,
                        "observer_intertwining_loss": 0.0,
                        "observer_semantic_relation_loss": 0.0,
                        "observer_orthogonality_residual": 0.0,
                        "hard_semantic_flatness_loss": 0.0,
                        "terminal_accuracy": 0.5,
                        "construction_accuracy": 0.5,
                        "gradient_norm_before_clip": 1.0,
                        "base_warmup": 0.005,
                        "auxiliary_multiplier": 0.5,
                        "auxiliary_delay_steps": 0,
                        "auxiliary_ramp_end_step": 2,
                        "relation_context_indices": list(range(8)),
                        "relation_cell_indices": list(range(9)),
                        "relation_cells_per_context": 9,
                        "relation_cells_total": 72,
                    },
                    {
                        "step": 2,
                        "length": 2,
                        "loss": 0.5,
                        "terminal_loss": 0.3,
                        "construction_ce_loss": 0.2,
                        "legacy_composition_loss": 0.0,
                        "legacy_delayed_return_loss": 0.0,
                        "exact_flatness_loss": 0.0,
                        "observer_anchor_geometry_loss": 0.0,
                        "observer_centered_readout_loss": 0.0,
                        "observer_intertwining_loss": 0.0,
                        "observer_semantic_relation_loss": 0.0,
                        "observer_orthogonality_residual": 0.0,
                        "hard_semantic_flatness_loss": 0.0,
                        "terminal_accuracy": 0.5,
                        "construction_accuracy": 0.5,
                        "gradient_norm_before_clip": 1.0,
                        "base_warmup": 0.01,
                        "auxiliary_multiplier": 1.0,
                        "auxiliary_delay_steps": 0,
                        "auxiliary_ramp_end_step": 2,
                        "relation_context_indices": list(range(8)),
                        "relation_cell_indices": list(range(9)),
                        "relation_cells_per_context": 9,
                        "relation_cells_total": 72,
                    },
                ],
                "elapsed_seconds": 0.01,
                "final_loss": 0.5,
                "parameter_count": metadata["parameter_count"],
                "trainable_parameter_count": metadata["trainable_parameter_count"],
                "initial_state_digest": metadata["initial_state_digest"],
                "core_initial_state_digest": metadata["core_initial_state_digest"],
                "final_state_digest": metadata["final_state_digest"],
                "episode_stream_digest": metadata["episode_stream_digest"],
                "terminal_proposal_stream_digest": metadata["terminal_proposal_stream_digest"],
                "relation_schedule_digest": metadata["relation_schedule_digest"],
                "terminal_firewall_policy_digest": metadata["terminal_firewall_policy_digest"],
                "terminal_proposal_count": counts["proposals"],
                "terminal_candidates_accepted": counts["accepted"],
                "terminal_candidates_rejected": counts["rejected"],
                "terminal_identity_rejections": counts["identity_rejections"],
                "terminal_r2_rejections": counts["r2_rejections"],
                "construction_digest": metadata["construction"]["digest"],
                "ambient_initial_digest": metadata["ambient_encoder"]["initial_digest"],
                "ambient_final_digest": metadata["ambient_encoder"]["final_digest"],
            }
            record = _identity(RECORD_SCHEMA, source_sha, prereg_sha)
            record.update(
                {
                    "arm": arm,
                    "seed": seed,
                    "checkpoint_sha256": file_sha256(checkpoint_path),
                    "checkpoint_state_digest": state_digest,
                    "behavior": {"score": 0.25 + arm_index / 100.0},
                    "geometry": {"finite": True},
                    "null_perturbation": {"retention": 1.0},
                }
            )
            record_path = record_dir / f"{arm}_seed{seed}.json"
            _write_json(record_path, record)
            record_tree[str(seed)][arm] = record
            record_rows.append(
                {
                    "path": f"records/{arm}_seed{seed}.json",
                    "sha256": file_sha256(record_path),
                    "arm": arm,
                    "seed": seed,
                }
            )
    checkpoint_rows.sort(key=lambda row: (row["seed"], row["arm"]))
    record_rows.sort(key=lambda row: (row["seed"], row["arm"]))
    seal = _identity(CHECKPOINT_SEAL_SCHEMA, source_sha, prereg_sha)
    seal.update({"count": len(checkpoint_rows), "checkpoints": checkpoint_rows})
    _seal(seal, "seal_sha256")
    _write_json(directory / "CHECKPOINT_SEAL.json", seal)

    bank = _identity(EVAL_BANK_SCHEMA, source_sha, prereg_sha)
    bank.update({"profile": profile, "cases": {"geometry": [1, 2, 3]}})
    _seal(bank, "fingerprint")
    _write_json(directory / "EVAL_BANK.json", bank)

    aggregate = {arm: {"mean": 0.25} for arm in PRIMARY_ARMS}
    gates = _identity(GATES_SCHEMA, source_sha, prereg_sha)
    gates.update(
        {
            "profile": profile,
            "run_mode": run_mode,
            "status": {
                "execution_integrity": "PASS",
                "assay_validity": "PASS",
                "scientific_status": "COMPILED_KERNEL_ONLY",
                "pilot_promotion": "DO_NOT_PROMOTE" if profile == "screen" else "NOT_APPLICABLE",
            },
        }
    )
    _write_json(directory / "GATES.json", gates)
    controls = {
        "schema": "komorebi.neuralese.invariant_kernel.controls.v1",
        "kernel": {"assay_valid": True},
        "behavioral": {"assay_valid": True},
        "assay_valid": True,
    }
    _write_json(directory / "CONTROLS.json", controls)
    chart = directory / "invariant_kernel_summary.png"
    chart.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
    (directory / "REPORT.md").write_text("# Developmental result\n\nScientific status: negative.\n", encoding="utf-8")
    result = _identity(RESULT_SCHEMA, source_sha, prereg_sha)
    result.update(
        {
            "profile": profile,
            "run_mode": run_mode,
            "config": profiles[profile],
            "source_files": source_files,
            "checkpoint_seal": seal,
            "evaluation_bank_fingerprint": bank["fingerprint"],
            "training_contract": {
                "plan_version": PLAN_VERSION,
                "arms": [copy.deepcopy(verifier.ARM_METADATA[arm]) for arm in PRIMARY_ARMS],
                "config": copy.deepcopy(training_tree[str(seeds[0])][PRIMARY_ARMS[0]]["config"]),
                "stream_lineage": {},
                "auxiliary_schedule": {
                    "delay_steps": 0,
                    "ramp_end_step": 2,
                    "rule": (
                        "zero through completed delay_steps; linear ramp thereafter; "
                        "one at completed ramp_end_step"
                    ),
                    "base_warmup_steps": 200,
                    "base_warmup_is_independent": True,
                },
                "relation_exposure": _relation_exposure(),
                "learned_intertwiner": {},
                "hard_kernel": {},
                "claim_boundary": "explicit-pressure developmental comparison only",
            },
            "record_index": record_rows,
            "records": record_tree,
            "training": training_tree,
            "controls": controls,
            "aggregate": aggregate,
            "aggregate_sha256": canonical_object_sha256(aggregate),
            "gates": gates,
            "runtime": {"device": "cpu"},
            "phase_seconds": {"total": 0.1},
            "chart": {"path": chart.name, "sha256": file_sha256(chart)},
        }
    )
    _write_json(directory / "RESULTS.json", result)
    completion = _identity(COMPLETION_SCHEMA, source_sha, prereg_sha)
    completion.update(
        {
            "profile": profile,
            "run_mode": run_mode,
            "execution_integrity": "PASS",
            "assay_validity": "PASS",
            "scientific_status": gates["status"]["scientific_status"],
            "pilot_promotion": gates["status"]["pilot_promotion"],
            "results_sha256": file_sha256(directory / "RESULTS.json"),
            "gates_sha256": file_sha256(directory / "GATES.json"),
            "report_sha256": file_sha256(directory / "REPORT.md"),
            "chart_sha256": file_sha256(chart),
            "checkpoint_seal_sha256": file_sha256(directory / "CHECKPOINT_SEAL.json"),
            "evaluation_bank_fingerprint": bank["fingerprint"],
            "record_hashes": record_rows,
            "aggregate_sha256": canonical_object_sha256(aggregate),
            "controls_sha256": file_sha256(directory / "CONTROLS.json"),
        }
    )
    _write_json(directory / "RUN_COMPLETE.json", completion)
    return directory


@pytest.fixture
def valid_screen(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "package"
    return root, _make_run(root, "screen")


def _reseal_checkpoint_outer(directory: Path) -> None:
    seal_path = directory / "CHECKPOINT_SEAL.json"
    seal = _read_json(seal_path)
    for row in seal["checkpoints"]:  # type: ignore[index]
        path = directory / str(row["path"])
        row["sha256"] = file_sha256(path)
    _seal(seal, "seal_sha256")
    _write_json(seal_path, seal)
    result = _read_json(directory / "RESULTS.json")
    result["checkpoint_seal"] = copy.deepcopy(seal)
    _write_json(directory / "RESULTS.json", result)
    completion = _read_json(directory / "RUN_COMPLETE.json")
    completion["checkpoint_seal_sha256"] = file_sha256(seal_path)
    completion["results_sha256"] = file_sha256(directory / "RESULTS.json")
    _write_json(directory / "RUN_COMPLETE.json", completion)


def test_developmental_screen_verifies_without_pilot(
    valid_screen: tuple[Path, Path],
) -> None:
    root, _ = valid_screen
    receipt = verify_package(root)
    assert receipt["status"] == "PASS"
    assert receipt["developmental_runs"] == 1
    assert receipt["fresh_pilots"] == 0
    assert receipt["runs"][0]["scientific_status"] == "COMPILED_KERNEL_ONLY"
    assert receipt["runs"][0]["checkpoint_payloads_verified"] == 6


def test_smoke_and_scientific_failure_are_valid_structural_results(tmp_path: Path) -> None:
    root = tmp_path / "package"
    directory = _make_run(root, "smoke")
    gates = _read_json(directory / "GATES.json")
    gates["status"]["scientific_status"] = "NOT_EVALUATED"
    _write_json(directory / "GATES.json", gates)
    result = _read_json(directory / "RESULTS.json")
    result["gates"] = gates
    _write_json(directory / "RESULTS.json", result)
    completion = _read_json(directory / "RUN_COMPLETE.json")
    completion["scientific_status"] = "NOT_EVALUATED"
    completion["gates_sha256"] = file_sha256(directory / "GATES.json")
    completion["results_sha256"] = file_sha256(directory / "RESULTS.json")
    _write_json(directory / "RUN_COMPLETE.json", completion)
    assert verify_package(root)["runs"][0]["profile"] == "smoke"


@pytest.mark.parametrize(
    "payload",
    [
        '{"x":NaN}\n',
        '{"x":Infinity}\n',
        '{"x":1e999}\n',
        '{"x":1,"x":2}\n',
    ],
)
def test_nonfinite_and_duplicate_json_are_rejected(
    valid_screen: tuple[Path, Path], payload: str
) -> None:
    root, directory = valid_screen
    (directory / "GATES.json").write_text(payload, encoding="utf-8")
    with pytest.raises(VerificationError, match="non-finite JSON|duplicate JSON object key"):
        verify_package(root)


def test_source_and_preregistration_identity_are_bound(
    valid_screen: tuple[Path, Path],
) -> None:
    root, _ = valid_screen
    (root / "src.py").write_text("VALUE = 7\n", encoding="utf-8")
    with pytest.raises(VerificationError, match="source digest mismatch"):
        verify_package(root)


def test_missing_run_complete_is_rejected(valid_screen: tuple[Path, Path]) -> None:
    root, directory = valid_screen
    (directory / "RUN_COMPLETE.json").unlink()
    with pytest.raises(VerificationError, match="run is incomplete"):
        verify_package(root)


def test_checkpoint_grid_rejects_extra_file(valid_screen: tuple[Path, Path]) -> None:
    root, directory = valid_screen
    torch.save({"rogue": torch.ones(1)}, directory / "checkpoints" / "rogue.pt")
    with pytest.raises(VerificationError, match="missing or extra artifacts"):
        verify_package(root)


def test_checkpoint_outside_sealed_directory_is_rejected(
    valid_screen: tuple[Path, Path],
) -> None:
    root, directory = valid_screen
    torch.save({"rogue": torch.ones(1)}, directory / "concealed.pt")
    with pytest.raises(VerificationError, match="unsealed checkpoint"):
        verify_package(root)


@pytest.mark.parametrize("suffix", (".pth", ".ckpt", ".bin", ".safetensors"))
def test_checkpoint_like_artifact_with_alternate_suffix_is_rejected(
    valid_screen: tuple[Path, Path], suffix: str
) -> None:
    root, directory = valid_screen
    (directory / f"concealed{suffix}").write_bytes(b"unsealed checkpoint")
    with pytest.raises(VerificationError, match="unsealed checkpoint"):
        verify_package(root)


def test_checkpoint_payload_schema_is_exact(valid_screen: tuple[Path, Path]) -> None:
    root, directory = valid_screen
    path = directory / "checkpoints" / "learned_intertwiner_seed947.pt"
    payload = torch.load(path, map_location="cpu", weights_only=True)
    payload["posthoc_claim"] = "spontaneous neuralese"
    torch.save(payload, path)
    _reseal_checkpoint_outer(directory)
    with pytest.raises(VerificationError, match="checkpoint payload.*schema mismatch"):
        verify_package(root)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("auxiliary_delay_steps", 1, "auxiliary_delay_steps"),
        ("weights", {
            "exact_flatness": 0.9,
            "observer_anchor_geometry": 0.1,
            "observer_centered_readout": 1.0,
            "observer_intertwining": 10.0,
            "observer_semantic_relation": 0.3,
            "hard_semantic_flatness": 0.3,
        }, "loss weights"),
    ),
)
def test_checkpoint_schedule_and_weights_are_bound_to_preregistration(
    valid_screen: tuple[Path, Path],
    field: str,
    value: object,
    message: str,
) -> None:
    root, directory = valid_screen
    path = directory / "checkpoints" / "learned_intertwiner_seed947.pt"
    payload = torch.load(path, map_location="cpu", weights_only=True)
    payload["config"][field] = value
    payload["training_metadata"]["config"][field] = copy.deepcopy(value)
    torch.save(payload, path)
    _reseal_checkpoint_outer(directory)
    with pytest.raises(VerificationError, match=message):
        verify_package(root)


def test_checkpoint_metadata_schedule_is_bound_to_config(
    valid_screen: tuple[Path, Path],
) -> None:
    root, directory = valid_screen
    path = directory / "checkpoints" / "learned_intertwiner_seed947.pt"
    payload = torch.load(path, map_location="cpu", weights_only=True)
    payload["training_metadata"]["auxiliary_schedule"]["delay_steps"] = 1
    torch.save(payload, path)
    _reseal_checkpoint_outer(directory)
    with pytest.raises(VerificationError, match="auxiliary schedule/config mismatch"):
        verify_package(root)


def test_checkpoint_config_surface_is_exact(valid_screen: tuple[Path, Path]) -> None:
    root, directory = valid_screen
    path = directory / "checkpoints" / "learned_intertwiner_seed947.pt"
    payload = torch.load(path, map_location="cpu", weights_only=True)
    payload["config"]["posthoc_schedule"] = 17
    payload["training_metadata"]["config"]["posthoc_schedule"] = 17
    torch.save(payload, path)
    _reseal_checkpoint_outer(directory)
    with pytest.raises(VerificationError, match="checkpoint config.*schema mismatch"):
        verify_package(root)


def test_checkpoint_cannot_silently_omit_auxiliary_context_count(
    valid_screen: tuple[Path, Path],
) -> None:
    root, directory = valid_screen
    path = directory / "checkpoints" / "learned_intertwiner_seed947.pt"
    payload = torch.load(path, map_location="cpu", weights_only=True)
    payload["config"].pop("auxiliary_contexts", None)
    payload["training_metadata"]["config"].pop("auxiliary_contexts", None)
    torch.save(payload, path)
    _reseal_checkpoint_outer(directory)
    with pytest.raises(VerificationError, match="checkpoint config.*schema mismatch"):
        verify_package(root)


def test_checkpoint_auxiliary_context_count_is_bound_to_profile(
    valid_screen: tuple[Path, Path],
) -> None:
    root, directory = valid_screen
    path = directory / "checkpoints" / "learned_intertwiner_seed947.pt"
    payload = torch.load(path, map_location="cpu", weights_only=True)
    payload["config"]["auxiliary_contexts"] = 7
    payload["training_metadata"]["config"]["auxiliary_contexts"] = 7
    torch.save(payload, path)
    _reseal_checkpoint_outer(directory)
    with pytest.raises(VerificationError, match="preregistered auxiliary_contexts"):
        verify_package(root)


def test_checkpoint_cannot_silently_omit_relation_exposure(
    valid_screen: tuple[Path, Path],
) -> None:
    root, directory = valid_screen
    path = directory / "checkpoints" / "learned_intertwiner_seed947.pt"
    payload = torch.load(path, map_location="cpu", weights_only=True)
    payload["training_metadata"].pop("relation_exposure")
    torch.save(payload, path)
    _reseal_checkpoint_outer(directory)
    with pytest.raises(VerificationError, match="training metadata.*schema mismatch"):
        verify_package(root)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("selection", "random_rows_with_replacement"),
        ("contexts_per_step", 7),
        ("contexts_per_step", 8.0),
        ("cells_per_context", 8),
        ("cells_per_step_total", 71),
        ("aggregation", "sum_over_contexts_and_cells"),
        ("shared_across_arms", False),
    ),
)
def test_checkpoint_relation_exposure_policy_is_exact(
    valid_screen: tuple[Path, Path], field: str, value: object
) -> None:
    root, directory = valid_screen
    path = directory / "checkpoints" / "learned_intertwiner_seed947.pt"
    payload = torch.load(path, map_location="cpu", weights_only=True)
    payload["training_metadata"]["relation_exposure"][field] = value
    torch.save(payload, path)
    _reseal_checkpoint_outer(directory)
    with pytest.raises(VerificationError, match="frozen eight-context policy"):
        verify_package(root)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("relation_context_indices", list(range(7))),
        ("relation_context_indices", [1, 0, 2, 3, 4, 5, 6, 7]),
        ("relation_cell_indices", list(range(8))),
        ("relation_cells_per_context", 8),
        ("relation_cells_total", 71),
        ("relation_cells_total", 72.0),
    ),
)
def test_training_trajectory_relation_receipt_is_exact(
    valid_screen: tuple[Path, Path], field: str, value: object
) -> None:
    root, directory = valid_screen
    result = _read_json(directory / "RESULTS.json")
    row = result["training"]["947"]["learned_intertwiner"]["trajectory"][0]
    row[field] = value
    _write_json(directory / "RESULTS.json", result)
    completion = _read_json(directory / "RUN_COMPLETE.json")
    completion["results_sha256"] = file_sha256(directory / "RESULTS.json")
    _write_json(directory / "RUN_COMPLETE.json", completion)
    with pytest.raises(VerificationError, match="relation-cell schedule mismatch"):
        verify_package(root)


def test_training_contract_relation_policy_is_bound_to_checkpoints(
    valid_screen: tuple[Path, Path],
) -> None:
    root, directory = valid_screen
    result = _read_json(directory / "RESULTS.json")
    result["training_contract"]["relation_exposure"]["aggregation"] = (
        "sum_over_contexts_and_cells"
    )
    _write_json(directory / "RESULTS.json", result)
    completion = _read_json(directory / "RUN_COMPLETE.json")
    completion["results_sha256"] = file_sha256(directory / "RESULTS.json")
    _write_json(directory / "RUN_COMPLETE.json", completion)
    with pytest.raises(VerificationError, match="frozen eight-context policy"):
        verify_package(root)


def test_training_trajectory_schedule_is_verified_independently(
    valid_screen: tuple[Path, Path],
) -> None:
    root, directory = valid_screen
    result = _read_json(directory / "RESULTS.json")
    row = result["training"]["947"]["learned_intertwiner"]["trajectory"][0]
    row["auxiliary_multiplier"] = 0.75
    _write_json(directory / "RESULTS.json", result)
    completion = _read_json(directory / "RUN_COMPLETE.json")
    completion["results_sha256"] = file_sha256(directory / "RESULTS.json")
    _write_json(directory / "RUN_COMPLETE.json", completion)
    with pytest.raises(VerificationError, match="staged multiplier mismatch"):
        verify_package(root)


def test_training_contract_schedule_is_bound_to_checkpoints(
    valid_screen: tuple[Path, Path],
) -> None:
    root, directory = valid_screen
    result = _read_json(directory / "RESULTS.json")
    result["training_contract"]["auxiliary_schedule"]["ramp_end_step"] = 3
    _write_json(directory / "RESULTS.json", result)
    completion = _read_json(directory / "RUN_COMPLETE.json")
    completion["results_sha256"] = file_sha256(directory / "RESULTS.json")
    _write_json(directory / "RUN_COMPLETE.json", completion)
    with pytest.raises(VerificationError, match="training-contract schedule mismatch"):
        verify_package(root)


def test_checkpoint_is_always_loaded_weights_only(
    valid_screen: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _ = valid_screen
    observed: list[object] = []
    original = torch.load

    def wrapped(*args: object, **kwargs: object) -> object:
        observed.append(kwargs.get("weights_only"))
        return original(*args, **kwargs)

    monkeypatch.setattr(torch, "load", wrapped)
    verify_package(root)
    assert observed == [True] * len(PRIMARY_ARMS)


def test_unsafe_checkpoint_pickle_global_is_rejected(
    valid_screen: tuple[Path, Path],
) -> None:
    root, directory = valid_screen
    path = directory / "checkpoints" / "polar_supervised_seed947.pt"
    payload = torch.load(path, map_location="cpu", weights_only=True)
    payload["config"] = UnsafeCheckpointValue()
    torch.save(payload, path)
    _reseal_checkpoint_outer(directory)
    with pytest.raises(VerificationError, match="safe weights-only load failed"):
        verify_package(root)


def test_nonfinite_checkpoint_tensor_fails_closed(valid_screen: tuple[Path, Path]) -> None:
    root, directory = valid_screen
    path = directory / "checkpoints" / "polar_cr_seed947.pt"
    payload = torch.load(path, map_location="cpu", weights_only=True)
    payload["state_dict"]["weight"][0, 0] = float("nan")
    torch.save(payload, path)
    _reseal_checkpoint_outer(directory)
    with pytest.raises(VerificationError, match="non-finite"):
        verify_package(root)


def test_record_grid_and_hash_are_enforced(valid_screen: tuple[Path, Path]) -> None:
    root, directory = valid_screen
    record = directory / "records" / "polar_exact_seed947.json"
    record.write_text(record.read_text(encoding="utf-8") + " ", encoding="utf-8")
    with pytest.raises(VerificationError, match="record file hash mismatch"):
        verify_package(root)


@pytest.mark.parametrize(
    ("artifact", "message"),
    (("RESULTS.json", "RESULTS.json"), ("GATES.json", "GATES.json"), ("REPORT.md", "REPORT.md")),
)
def test_completion_hashes_bind_result_gate_and_report(
    valid_screen: tuple[Path, Path], artifact: str, message: str
) -> None:
    root, directory = valid_screen
    path = directory / artifact
    path.write_bytes(path.read_bytes() + b" \n")
    with pytest.raises(VerificationError, match=message):
        verify_package(root)


def test_aggregate_and_record_index_hashes_are_enforced(
    valid_screen: tuple[Path, Path],
) -> None:
    root, directory = valid_screen
    completion = _read_json(directory / "RUN_COMPLETE.json")
    completion["aggregate_sha256"] = "0" * 64
    _write_json(directory / "RUN_COMPLETE.json", completion)
    with pytest.raises(VerificationError, match="aggregate"):
        verify_package(root)


@pytest.mark.parametrize("relative", ("__pycache__/poison.pyc", ".pytest_cache/state"))
def test_run_cache_and_bytecode_are_rejected(
    valid_screen: tuple[Path, Path], relative: str
) -> None:
    root, directory = valid_screen
    path = directory / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"poison")
    with pytest.raises(VerificationError, match="cache/bytecode"):
        verify_package(root)


def test_run_symlink_is_rejected(valid_screen: tuple[Path, Path]) -> None:
    root, directory = valid_screen
    target = directory / "REPORT.md"
    link = directory / "report_alias.md"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlink creation is unavailable")
    with pytest.raises(VerificationError, match="symbolic links"):
        verify_package(root)


def test_package_level_cache_is_rejected(valid_screen: tuple[Path, Path]) -> None:
    root, _ = valid_screen
    path = root / "src" / "__pycache__" / "poison.pyc"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"poison")
    with pytest.raises(VerificationError, match="cache/bytecode"):
        verify_package(root)


def test_failed_integrity_or_assay_is_not_a_valid_run(
    valid_screen: tuple[Path, Path],
) -> None:
    root, directory = valid_screen
    gates = _read_json(directory / "GATES.json")
    gates["status"]["execution_integrity"] = "FAIL"
    gates["status"]["scientific_status"] = "NOT_EVALUATED"
    _write_json(directory / "GATES.json", gates)
    result = _read_json(directory / "RESULTS.json")
    result["gates"] = gates
    _write_json(directory / "RESULTS.json", result)
    completion = _read_json(directory / "RUN_COMPLETE.json")
    completion["execution_integrity"] = "FAIL"
    completion["scientific_status"] = "NOT_EVALUATED"
    completion["gates_sha256"] = file_sha256(directory / "GATES.json")
    completion["results_sha256"] = file_sha256(directory / "RESULTS.json")
    _write_json(directory / "RUN_COMPLETE.json", completion)
    with pytest.raises(VerificationError, match="execution integrity did not pass"):
        verify_package(root)
