#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.ambient_eval import (
    FAMILY_TO_GENERATOR,
    episode_bank_receipts,
    episode_contract,
    exact_chart_packet_control,
    family_rollout_metrics,
    file_sha256,
    gauge_synthetic_controls,
    json_ready,
    learned_gauge_diagnostic,
    load_projective_pilot_models,
    make_episode_bank,
    null_loop_margin_audit,
    packet_audit,
    per_episode_observability,
    switched_synthetic_controls,
    switched_word_audit,
    trajectory_tensor_receipts,
)
from komorebi_neuralese.reporting import source_files, tree_digest


PROFILES: dict[str, dict[str, Any]] = {
    "smoke": {
        "model_seeds": [0],
        "contexts_per_family": 32,
        "families": ["d4", "c8", "mixed_cycle", "random_permutation_pairs"],
        "prefixes": [0, 64, 128],
        "packet_horizon": 6,
        "observability_depth": 4,
        "observability_contexts": 16,
        "tangent_contexts": 4,
        "null_contexts": 4,
        "null_repeats": [1, 2, 4],
        "bank_seed": 31001,
    },
    "pilot": {
        "model_seeds": [0, 1],
        "contexts_per_family": 256,
        "families": ["d4", "c8", "mixed_cycle", "random_permutation_pairs"],
        "prefixes": [0, 64, 128, 256],
        "packet_horizon": 8,
        "observability_depth": 4,
        "observability_contexts": 64,
        "tangent_contexts": 32,
        "null_contexts": 16,
        "null_repeats": [1, 2, 4, 8, 16, 32],
        "bank_seed": 31001,
    },
}


def atomic_json(path: Path, value: Any) -> None:
    payload = json_ready(value)
    text = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def _gate(observed: Any, criterion: str, passed: bool, *, evaluable: bool = True) -> dict[str, Any]:
    return {
        "observed": observed,
        "criterion": criterion,
        "status": "PASS" if passed else ("FAIL" if evaluable else "NOT_EVALUABLE"),
    }


def adjudicate(
    *,
    profile: str,
    checkpoint_receipts: dict[str, Any],
    contracts: dict[str, Any],
    controls: dict[str, Any],
    records: dict[str, Any],
    prefixes: list[int],
) -> dict[str, Any]:
    gauge = controls["gauge"]
    exact_packet_rows = controls["exact_chart_packet"]
    exact_packet_floor = min(
        row["membership_fraction"]
        for key, row in exact_packet_rows.items()
        if key.isdigit()
    )
    exact_switch = controls["switched"]["exact_chart"]
    nonnormal = controls["switched"]["nonnormal"]
    contract_pass = all(
        contract["intermediates_exact"]
        and contract["target_exact"]
        and contract["canonical_visible_slots_exact"]
        for contract in contracts.values()
    )

    assay_gates = {
        "A01_checkpoint_integrity": _gate(
            len(checkpoint_receipts), ">= 1 SHA/config-validated frozen checkpoint", len(checkpoint_receipts) >= 1
        ),
        "A02_episode_and_slot_contract": _gate(contract_pass, "all exact", contract_pass),
        "A03_exact_global_gauge_control": _gate(
            gauge["exact_global"]["global_residual_max"],
            "<= 1e-12",
            gauge["exact_global"]["global_residual_max"] <= 1e-12,
        ),
        "A04_statewise_gauge_control": _gate(
            {
                "statewise_max": gauge["exact_statewise"]["statewise_residual_max"],
                "global_min": gauge["exact_statewise"]["global_residual_min"],
            },
            "statewise <= 1e-12 and global >= 0.10",
            gauge["exact_statewise"]["statewise_residual_max"] <= 1e-12
            and gauge["exact_statewise"]["global_residual_min"] >= 0.10,
        ),
        "A05_negative_and_leakage_controls": _gate(
            {
                "negative_coefficients": gauge["negative_scale"]["invalid_coefficients"],
                "leakage_residual": gauge["leakage"]["statewise_residual_max"],
                "reconstruction_error": gauge["leakage"]["reconstruction_error_max"],
            },
            "negative detected, leakage > 1e-3, reconstruction <= 1e-12",
            gauge["negative_scale"]["invalid_coefficients"] >= 1
            and gauge["leakage"]["statewise_residual_max"] > 1e-3
            and gauge["leakage"]["reconstruction_error_max"] <= 1e-12,
        ),
        "A06_exact_chart_packet_control": _gate(
            exact_packet_floor, "== 1.0 at every audited prefix", exact_packet_floor == 1.0
        ),
        "A07_exact_chart_switched_control": _gate(
            {
                "accuracy": exact_switch["accuracy"],
                "gain_min": exact_switch["gain"]["minimum"],
                "gain_max": exact_switch["gain"]["maximum"],
            },
            "accuracy == 1 and gains within 1e-10 of 1",
            exact_switch["accuracy"] == 1.0
            and abs(exact_switch["gain"]["minimum"] - 1.0) <= 1e-10
            and abs(exact_switch["gain"]["maximum"] - 1.0) <= 1e-10,
        ),
        "A08_nonnormal_control": _gate(
            nonnormal,
            "flagged with individual radii < 1 and projective gain > 30",
            nonnormal["flagged"]
            and max(nonnormal["individual_spectral_radii"]) < 1.0
            and nonnormal["projective_worst_amplification"] > 30.0,
        ),
    }
    assay_valid = all(gate["status"] == "PASS" for gate in assay_gates.values())

    statewise_fractions = [
        family_record["gauge"]["statewise_better_fraction"]
        for seed_record in records.values()
        for family_record in seed_record["families"].values()
    ]
    observability_min = min(
        seed_record["d4_observability"]["minimum_rank"] for seed_record in records.values()
    )
    packet_floor = min(
        row["membership_fraction"]
        for seed_record in records.values()
        for key, row in seed_record["d4_packets"].items()
        if key.isdigit()
    )
    domain_min = min(
        family_record["rollout"]["domain"]["minimum_pre_normalization_l2"]
        for seed_record in records.values()
        for family_record in seed_record["families"].values()
    )
    switch_undefined = sum(
        seed_record["d4_switched"]["undefined_applications"] for seed_record in records.values()
    )
    null_memberships = [
        row["membership_fraction"]
        for seed_record in records.values()
        for relation in seed_record["d4_null_loops"]["relations"].values()
        for key, row in relation.items()
        if key.isdigit()
    ]

    mechanism_gates = {
        "M01_statewise_gauge_advantage": _gate(
            min(statewise_fractions), ">= 0.50 of operators per family", min(statewise_fractions) >= 0.50, evaluable=assay_valid
        ),
        "M02_full_per_episode_observability": _gate(
            observability_min, "rank == 8", observability_min == 8, evaluable=assay_valid
        ),
        "M03_exhaustive_d4_packet_membership": _gate(
            packet_floor, ">= 0.90 at every audited prefix", packet_floor >= 0.90, evaluable=assay_valid
        ),
        "M04_null_loop_packet_retention": _gate(
            min(null_memberships), ">= 0.90 for every tested relation/repeat", min(null_memberships) >= 0.90, evaluable=assay_valid
        ),
        "M05_projective_domain_safety": _gate(
            {"minimum_preimage_norm": domain_min, "undefined_switches": switch_undefined},
            "minimum > 1e-8 and no undefined switched applications",
            domain_min > 1e-8 and switch_undefined == 0,
            evaluable=assay_valid,
        ),
    }
    if not assay_valid:
        for gate in mechanism_gates.values():
            gate["status"] = "NOT_EVALUABLE"

    final_prefix = str(max(prefixes))
    structured_floor = min(
        seed_record["families"][family]["rollout"][final_prefix]["accuracy"]
        for seed_record in records.values()
        for family in ("d4", "c8", "mixed_cycle")
    )
    random_values = [
        seed_record["families"]["random_permutation_pairs"]["rollout"][final_prefix]["accuracy"]
        for seed_record in records.values()
    ]
    capability_gates = {
        "C01_structured_long_depth_accuracy": _gate(
            structured_floor,
            ">= 0.70 per seed/family at final profile depth",
            structured_floor >= 0.70,
            evaluable=assay_valid,
        ),
        "C02_random_family_reported_not_required": {
            "observed": random_values,
            "criterion": "descriptive only; no success threshold",
            "status": "OBSERVED" if assay_valid else "NOT_EVALUABLE",
        },
    }
    if not assay_valid:
        capability_gates["C01_structured_long_depth_accuracy"]["status"] = "NOT_EVALUABLE"

    mechanism_pass = assay_valid and all(
        gate["status"] == "PASS" for gate in mechanism_gates.values()
    )
    capability_pass = assay_valid and capability_gates["C01_structured_long_depth_accuracy"]["status"] == "PASS"
    return {
        "study_status": "developmental_posthoc_frozen_checkpoint_diagnostics",
        "execution_status": "PASS",
        "assay_status": "PASS" if assay_valid else "FAIL",
        "mechanism_reference_status": (
            "PASS" if mechanism_pass else ("FAIL" if assay_valid else "NOT_EVALUABLE")
        ),
        "capability_reference_status": (
            "PASS" if capability_pass else ("FAIL" if assay_valid else "NOT_EVALUABLE")
        ),
        "full_developmental_claim": "NOT_EVALUATED" if profile == "smoke" else "NOT_CLAIMED_POSTHOC",
        "assay_valid": assay_valid,
        "assay_gates": assay_gates,
        "mechanism_reference_gates": mechanism_gates,
        "capability_reference_gates": capability_gates,
    }


def render_report(result: dict[str, Any]) -> str:
    gates = result["adjudication"]
    lines = [
        "# Ambient packet frozen-checkpoint diagnostics",
        "",
        f"- Profile: `{result['profile']}`",
        f"- Status: `{result['study_status']}`",
        f"- Assay: `{gates['assay_status']}`",
        f"- Mechanism reference: `{gates['mechanism_reference_status']}`",
        f"- Capability reference: `{gates['capability_reference_status']}`",
        f"- Full developmental claim: `{gates['full_developmental_claim']}`",
        "",
        "This is a diagnostics-only, developmental posthoc evaluation of frozen, retrospectively selected projective checkpoints. Scientific gate failure is retained as a result and does not make the run incomplete.",
        "",
        "## Assay gates",
        "",
        "| Gate | Status | Criterion |",
        "|---|---|---|",
    ]
    for name, gate in gates["assay_gates"].items():
        lines.append(f"| `{name}` | {gate['status']} | {gate['criterion']} |")
    lines += [
        "",
        "## Learned mechanism reference gates",
        "",
        "| Gate | Status | Criterion |",
        "|---|---|---|",
    ]
    for name, gate in gates["mechanism_reference_gates"].items():
        lines.append(f"| `{name}` | {gate['status']} | {gate['criterion']} |")
    lines += [
        "",
        "## Capability reference gates",
        "",
        "| Gate | Status | Criterion |",
        "|---|---|---|",
    ]
    for name, gate in gates["capability_reference_gates"].items():
        lines.append(f"| `{name}` | {gate['status']} | {gate['criterion']} |")
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "A pass describes finite, task-relative packet behavior in this explicit permutation-table model. It does not establish an infinite quotient, spontaneous Neuralese, architecture-independent emergence, or awareness. A failure localizes the corresponding gauge, packet, null-loop, switched-dynamics, or capability hypothesis without erasing earlier causal execution results.",
        "",
    ]
    return "\n".join(lines)


def validate_gate_contract(adjudication: dict[str, Any], contract: dict[str, Any]) -> None:
    groups = (
        ("assay_gates", "assay_gates"),
        ("mechanism_reference_gates", "learned_mechanism_reference_gates"),
        ("capability_reference_gates", "capability_reference_gates"),
    )
    for emitted_key, contract_key in groups:
        emitted = {
            name: gate["criterion"] for name, gate in adjudication[emitted_key].items()
        }
        if emitted != contract.get(contract_key):
            raise SystemExit(f"emitted {emitted_key} do not match the frozen contract")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Developmental posthoc ambient-packet diagnostics on frozen projective checkpoints"
    )
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    if torch.device(args.device).type != "cpu":
        raise SystemExit("ambient diagnostics currently require CPU for deterministic float64 geometry")

    config = dict(PROFILES[args.profile])
    contract_path = ROOT / "AMBIENT_PREREGISTRATION.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if contract.get("schema") != "komorebi.neuralese.ambient_diagnostics.contract.v1":
        raise SystemExit("ambient diagnostic contract schema mismatch")
    if contract.get("version") != "0.3.0":
        raise SystemExit("ambient diagnostic contract version mismatch")
    frozen_profile = contract.get("profiles", {}).get(args.profile)
    if frozen_profile != config:
        raise SystemExit(
            f"implementation profile {args.profile!r} does not match AMBIENT_PREREGISTRATION.json"
        )
    output_dir = args.output_dir or ROOT / "results" / f"ambient_{args.profile}"
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    diagnostic_constants = contract["diagnostic_constants"]
    torch.set_num_threads(
        max(1, min(int(diagnostic_constants["cpu_thread_cap"]), os.cpu_count() or 1))
    )
    torch.manual_seed(0)
    np.random.seed(0)
    torch.use_deterministic_algorithms(True)
    started = time.perf_counter()
    source_digest = tree_digest(ROOT, source_files(ROOT))

    loaded = load_projective_pilot_models(ROOT, config["model_seeds"], device="cpu")
    checkpoint_receipts = {str(seed): item.receipt for seed, item in loaded.items()}
    max_prefix = max(config["prefixes"])
    banks = {
        family: make_episode_bank(
            contexts=config["contexts_per_family"],
            length=max_prefix,
            family=family,
            seed=config["bank_seed"],
        )
        for family in config["families"]
    }
    contracts = {family: episode_contract(batch) for family, batch in banks.items()}
    bank_receipts = {family: episode_bank_receipts(batch) for family, batch in banks.items()}

    controls: dict[str, Any] = {"gauge": gauge_synthetic_controls()}
    records: dict[str, Any] = {}
    first_d4_capture = None
    for seed, loaded_checkpoint in loaded.items():
        model = loaded_checkpoint.model
        family_records: dict[str, Any] = {}
        captures: dict[str, Any] = {}
        for family, batch in banks.items():
            rollout, capture = family_rollout_metrics(model, batch, config["prefixes"])
            captures[family] = capture
            family_records[family] = {
                "rollout": rollout,
                "gauge": learned_gauge_diagnostic(model, capture),
                "tensor_receipts": trajectory_tensor_receipts(model, capture),
            }
        d4_capture = captures["d4"]
        if first_d4_capture is None:
            first_d4_capture = d4_capture
        records[str(seed)] = {
            "checkpoint_sha256": loaded_checkpoint.receipt["sha256"],
            "families": family_records,
            "d4_packets": packet_audit(
                model,
                d4_capture,
                prefixes=config["prefixes"],
                horizon=config["packet_horizon"],
            ),
            "d4_observability": per_episode_observability(
                model,
                d4_capture,
                max_depth=config["observability_depth"],
                episode_limit=config["observability_contexts"],
            ),
            "d4_switched": switched_word_audit(
                model,
                d4_capture,
                prefix=int(diagnostic_constants["switched_prefix"]),
                episode_limit=config["tangent_contexts"],
                word_length=int(diagnostic_constants["switched_word_length"]),
            ),
            "d4_null_loops": null_loop_margin_audit(
                model,
                d4_capture,
                prefix=int(diagnostic_constants["null_loop_prefix"]),
                horizon=config["packet_horizon"],
                repeats=config["null_repeats"],
                episode_limit=config["null_contexts"],
            ),
        }

    assert first_d4_capture is not None
    controls["exact_chart_packet"] = exact_chart_packet_control(
        first_d4_capture,
        prefixes=config["prefixes"],
        horizon=config["packet_horizon"],
    )
    controls["switched"] = switched_synthetic_controls(
        first_d4_capture.canonical_transitions[0],
        word_length=int(diagnostic_constants["switched_word_length"]),
    )
    adjudication = adjudicate(
        profile=args.profile,
        checkpoint_receipts=checkpoint_receipts,
        contracts=contracts,
        controls=controls,
        records=records,
        prefixes=config["prefixes"],
    )
    validate_gate_contract(adjudication, contract)
    contract_sha256 = file_sha256(contract_path)
    result = {
        "schema": "komorebi.neuralese.ambient_diagnostics.result.v1",
        "version": "0.3.0",
        "profile": args.profile,
        "study_status": "developmental_posthoc_frozen_checkpoint_diagnostics",
        "source_digest": source_digest,
        "implementation_contract": config,
        "contract_schema": contract["schema"],
        "contract_version": contract["version"],
        "contract_status": contract["status"],
        "contract_sha256": contract_sha256,
        "family_to_generator": FAMILY_TO_GENERATOR,
        "checkpoint_receipts": checkpoint_receipts,
        "bank_contracts": contracts,
        "bank_receipts": bank_receipts,
        "controls": controls,
        "records": records,
        "adjudication": adjudication,
    }
    atomic_json(output_dir / "RESULTS.json", result)
    atomic_json(output_dir / "GATES.json", adjudication)
    report = render_report(result)
    (output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    environment = {
        "schema": "komorebi.neuralese.ambient_diagnostics.environment.v1",
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "torch": torch.__version__,
        "device": "cpu",
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "elapsed_seconds": time.perf_counter() - started,
    }
    atomic_json(output_dir / "ENVIRONMENT.json", environment)
    completion = {
        "schema": "komorebi.neuralese.ambient_diagnostics.completion.v1",
        "version": "0.3.0",
        "profile": args.profile,
        "execution_status": "PASS",
        "assay_status": adjudication["assay_status"],
        "mechanism_reference_status": adjudication["mechanism_reference_status"],
        "capability_reference_status": adjudication["capability_reference_status"],
        "full_developmental_claim": adjudication["full_developmental_claim"],
        "contract_schema": contract["schema"],
        "contract_version": contract["version"],
        "contract_status": contract["status"],
        "contract_sha256": contract_sha256,
        "results_sha256": file_sha256(output_dir / "RESULTS.json"),
        "gates_sha256": file_sha256(output_dir / "GATES.json"),
        "report_sha256": file_sha256(output_dir / "REPORT.md"),
        "environment_sha256": file_sha256(output_dir / "ENVIRONMENT.json"),
        "evaluation_source_digest": source_digest,
    }
    atomic_json(output_dir / "RUN_COMPLETE.json", completion)
    print(json.dumps(completion, sort_keys=True, allow_nan=False))
    return 0 if adjudication["assay_valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
