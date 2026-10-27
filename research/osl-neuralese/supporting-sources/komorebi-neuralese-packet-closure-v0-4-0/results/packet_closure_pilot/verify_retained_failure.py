#!/usr/bin/env python3
"""Failure-aware archival verification for the retained v0.4 pilot.

This posthoc utility does not convert the official assay into a pass. It permits
only the exact consequences of the frozen A15 invalidation and the additive
schema evolution in the inherited v0.3 episode contract, while leaving every
other packaged verification assertion fail-closed.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


if not (sys.flags.ignore_environment and sys.flags.safe_path):
    raise SystemExit(
        "Run with: python -E -P -B "
        "results/packet_closure_pilot/verify_retained_failure.py"
    )
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "verify_package.py"
spec = importlib.util.spec_from_file_location(
    "_frozen_packet_closure_verifier", VERIFIER
)
if spec is None or spec.loader is None:
    raise SystemExit("cannot load the frozen package verifier")
vp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vp)


LEGACY_CONTRACT_KEYS = {
    "canonical_visible_slots_exact",
    "contexts",
    "intermediates_exact",
    "length",
    "target_exact",
}
STRENGTHENED_TRUE_KEYS = {
    "tables_exact_one_hot_maps",
    "tables_finite",
    "maps_are_permutations",
    "phi_is_permutation",
    "visible_slots_are_permutations",
    "shapes_exact",
    "values_in_range",
}


def verify_legacy_contract_extension() -> dict[str, object]:
    """Prove that the v0.3 mismatch is additive schema hardening only."""

    result = vp.require_mapping(
        vp.load_json("results/ambient_pilot/RESULTS.json"),
        "ambient result",
    )
    contract = vp.require_mapping(
        vp.load_json("AMBIENT_PREREGISTRATION.json"),
        "ambient contract",
    )
    profile = contract["profiles"]["pilot"]
    receipts: dict[str, object] = {}
    for external_family in profile["families"]:
        bank = vp.make_episode_bank(
            contexts=profile["contexts_per_family"],
            length=max(profile["prefixes"]),
            family=external_family,
            seed=profile["bank_seed"],
        )
        stored_receipt = result["bank_receipts"][external_family]
        current_receipt = vp.episode_bank_receipts(bank)
        vp.require(
            vp.closure.strict_json_equal(stored_receipt, current_receipt),
            f"legacy bank bytes changed: {external_family}",
        )

        stored = result["bank_contracts"][external_family]
        current = vp.episode_contract(bank)
        vp.require(
            set(stored) == LEGACY_CONTRACT_KEYS,
            f"unexpected legacy contract schema: {external_family}",
        )
        projection = {key: current[key] for key in sorted(LEGACY_CONTRACT_KEYS)}
        vp.require(
            vp.closure.strict_json_equal(stored, projection),
            f"legacy contract semantics changed: {external_family}",
        )
        vp.require(
            all(current[key] is True for key in STRENGTHENED_TRUE_KEYS),
            f"strengthened contract invariant failed: {external_family}",
        )
        expected_internal_family = (
            "random" if external_family == "random_permutation_pairs" else external_family
        )
        vp.require(
            current["family"] == expected_internal_family,
            f"strengthened family label mismatch: {external_family}",
        )
        expected_family_realization = external_family != "random_permutation_pairs"
        vp.require(
            current["canonical_family_realization_exact"]
            is expected_family_realization,
            f"strengthened family-realization invariant mismatch: {external_family}",
        )
        receipts[external_family] = {
            "bank_receipt_exact": True,
            "legacy_projection_exact": True,
            "strengthened_invariants_valid": True,
        }
    return receipts


def collect_nonfinite_paths(value: object, path: str = "$") -> list[str]:
    """Return every non-finite float path in a JSON-shaped in-memory object."""

    import math

    if isinstance(value, float) and not math.isfinite(value):
        return [path]
    if isinstance(value, dict):
        output: list[str] = []
        for key, child in value.items():
            output.extend(collect_nonfinite_paths(child, f"{path}.{key}"))
        return output
    if isinstance(value, list):
        output = []
        for index, child in enumerate(value):
            output.extend(collect_nonfinite_paths(child, f"{path}[{index}]"))
        return output
    return []


def verify_aggregate_serialization_normalization() -> dict[str, object]:
    """Prove that the aggregate mismatch is only JSON NaN-to-null normalization."""

    result = vp.require_mapping(
        vp.load_json("results/packet_closure_pilot/RESULTS.json"),
        "packet-closure result",
    )
    recomputed = vp.closure.aggregate_records(result["records"], result["config"])
    expected_nonfinite_paths = sorted(
        f"$.{arm}.metrics.operator_conditions_defined_minimum.{field}"
        for arm in ("euclidean_cr", "euclidean_supervised")
        for field in ("maximum", "mean", "minimum")
    )
    observed_nonfinite_paths = sorted(collect_nonfinite_paths(recomputed))
    vp.require(
        observed_nonfinite_paths == expected_nonfinite_paths,
        "unexpected non-finite aggregate paths",
    )
    vp.require(
        vp.closure.strict_json_equal(
            result["aggregate"], vp.closure.json_ready(recomputed)
        ),
        "stored aggregate is not the canonical JSON-ready recomputation",
    )
    recomputed_paired = vp.closure.paired_2x2_analysis(
        result["records"], result["config"]
    )
    vp.require(
        vp.closure.strict_json_equal(
            result["paired_2x2_analysis"], recomputed_paired
        ),
        "stored paired analysis differs from exact recomputation",
    )
    return {
        "status": "JSON_NAN_TO_NULL_ONLY",
        "nonfinite_paths": observed_nonfinite_paths,
        "json_ready_recomputation_exact": True,
        "paired_recomputation_exact": True,
    }


def verify_gate_observation_order() -> dict[str, object]:
    """Prove that gate readjudication differs only in two unordered row lists."""

    import copy

    result = vp.require_mapping(
        vp.load_json("results/packet_closure_pilot/RESULTS.json"),
        "packet-closure result",
    )
    contract = vp.load_json(vp.closure.CONTRACT_FILENAME)
    contract_sha256 = vp.file_sha256(ROOT / vp.closure.CONTRACT_FILENAME)
    validation = vp.closure.validate_contract(
        contract,
        "pilot",
        vp.closure.PROFILES["pilot"],
        vp.closure.contract_source_digest(ROOT),
    )
    contract_status = {
        "available": True,
        "path": vp.closure.CONTRACT_FILENAME,
        "sha256": contract_sha256,
        **validation,
    }
    aggregate = vp.closure.aggregate_records(result["records"], result["config"])
    paired = vp.closure.paired_2x2_analysis(result["records"], result["config"])
    recomputed = vp.closure.json_ready(
        vp.closure.adjudicate(
            "pilot",
            result["config"],
            contract_status,
            result["records"],
            aggregate,
            paired,
            result["checkpoint_seal"],
            vp.load_json("results/packet_closure_pilot/EVAL_BANK.json"),
            result["phase_times"],
            run_mode="official",
            source_integrity=result["source_integrity"],
        )
    )
    stored = copy.deepcopy(result["gates"])
    normalized = copy.deepcopy(recomputed)
    paths = (
        (
            "assay_gates",
            "A12_ambient_control_geometry",
        ),
        (
            "ambient_attribution_gates",
            "D01_specific_ambient_complement_use",
        ),
    )
    counts: dict[str, int] = {}
    for group, gate in paths:
        stored_rows = stored[group][gate]["observed"]
        recomputed_rows = normalized[group][gate]["observed"]
        vp.require(
            isinstance(stored_rows, list) and isinstance(recomputed_rows, list),
            f"unordered gate observation is not a list: {group}.{gate}",
        )
        sort_key = lambda row: json.dumps(
            row, sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        stored[group][gate]["observed"] = sorted(stored_rows, key=sort_key)
        normalized[group][gate]["observed"] = sorted(
            recomputed_rows, key=sort_key
        )
        counts[f"{group}.{gate}"] = len(stored_rows)
    vp.require(
        vp.closure.strict_json_equal(stored, normalized),
        "gate readjudication differs beyond unordered observation rows",
    )
    return {
        "status": "UNORDERED_OBSERVATION_ROWS_ONLY",
        "normalized_lists": counts,
        "normalized_gate_readjudication_exact": True,
    }


def verify_report_metric_order() -> dict[str, object]:
    """Prove that report replay differs only in paired-metric row order."""

    import copy

    result = vp.require_mapping(
        vp.load_json("results/packet_closure_pilot/RESULTS.json"),
        "packet-closure result",
    )
    metric_order = (
        "packet_membership",
        "packet_margin_p10",
        "d4_accuracy",
        "cross_family_minimum_accuracy",
        "structured_minimum_accuracy",
        "null_closure",
        "switched_max_gain",
        "switched_word_accuracy",
        "feshbach_return_fraction",
        "ambient_q_ablation_drop",
        "ambient_q_specific_excess_drop",
    )
    vp.require(
        set(result["paired_2x2_analysis"]["metrics"]) == set(metric_order),
        "paired metric set changed before report compatibility check",
    )
    ordered = copy.deepcopy(result)
    metrics = ordered["paired_2x2_analysis"]["metrics"]
    ordered["paired_2x2_analysis"]["metrics"] = {
        key: metrics[key] for key in metric_order
    }
    retained = (
        ROOT / "results/packet_closure_pilot/REPORT.md"
    ).read_text(encoding="utf-8")
    vp.require(
        retained == vp.closure.render_report(ordered),
        "retained report differs beyond paired-metric row ordering",
    )
    return {
        "status": "PAIRED_METRIC_ROW_ORDER_ONLY",
        "metric_order": list(metric_order),
        "ordered_report_replay_exact": True,
    }


def verify_chart_pixels_with_known_report_order() -> dict[str, object]:
    """Run the frozen renderer while permitting only the known report-order issue."""

    result = vp.require_mapping(
        vp.load_json("results/packet_closure_pilot/RESULTS.json"),
        "packet-closure result",
    )
    completion = vp.require_mapping(
        vp.load_json("results/packet_closure_pilot/RUN_COMPLETE.json"),
        "packet-closure completion",
    )
    expected = "Retained REPORT.md differs from the deterministic verified rendering"
    seen: list[str] = []
    strict_require = vp.require

    def report_aware_require(condition: bool, message: str) -> None:
        if condition:
            return
        if message == expected:
            seen.append(message)
            return
        strict_require(False, message)

    vp.require = report_aware_require
    try:
        vp.verify_rendered_outputs(
            ROOT / "results/packet_closure_pilot", result, completion
        )
    finally:
        vp.require = strict_require
    vp.require(seen == [expected], "known report-order failure was not reproduced")
    return {
        "status": "PASS",
        "decoded_chart_pixels_exact": True,
    }


def main() -> int:
    source_digest = vp.tree_digest(ROOT, vp.source_files(ROOT))
    vp.verify_manifest()
    vp.verify_legacy_lineage()
    vp.verify_v02_parent(
        "results/stability_pilot",
        "komorebi.neuralese.stable_quotient.completion.v1",
        "komorebi.neuralese.stable_quotient.result.v1",
    )
    vp.verify_v02_parent(
        "results/projective_pilot",
        "komorebi.neuralese.projective_training.completion.v1",
        "komorebi.neuralese.projective_training.result.v1",
    )
    legacy_compatibility = verify_legacy_contract_extension()
    aggregate_compatibility = verify_aggregate_serialization_normalization()
    gate_order_compatibility = verify_gate_observation_order()
    report_order_compatibility = verify_report_metric_order()
    chart_preflight = verify_chart_pixels_with_known_report_order()

    expected_failures = tuple(
        [
            f"Archived deterministic contract mismatch: {family}"
            for family in (
                "d4",
                "c8",
                "mixed_cycle",
                "random_permutation_pairs",
            )
        ]
        + [
            "v0.4 pilot did not complete",
            "v0.4 assay failed",
            "Pilot full claim is not evaluable",
            "Aggregate metrics mismatch",
            "Stored gates do not match independent adjudication",
            "Stored aggregate differs from checkpoint-replayed evaluation",
            "Stored scientific decisions differ from checkpoint-replayed adjudication",
            "Retained REPORT.md differs from the deterministic verified rendering",
        ]
    )
    seen: list[str] = []
    strict_require = vp.require

    def failure_aware_require(condition: bool, message: str) -> None:
        if condition:
            return
        if message in expected_failures:
            seen.append(message)
            return
        strict_require(False, message)

    vp.require = failure_aware_require
    try:
        ambient = vp.verify_v03_ambient()
        pilot = vp.verify_v04_pilot(source_digest)
    finally:
        vp.require = strict_require

    if tuple(seen) != expected_failures:
        raise SystemExit(
            "expected retained-failure sequence mismatch: "
            + json.dumps(seen, sort_keys=True)
        )

    output = {
        "schema": "komorebi.neuralese.packet_closure.archival_verification.v1",
        "status": "PASS_WITH_RETAINED_ASSAY_INVALIDATION",
        "manifest": "PASS",
        "parent_lineage": "PASS",
        "legacy_v03_contract_compatibility": legacy_compatibility,
        "aggregate_serialization_compatibility": aggregate_compatibility,
        "gate_observation_order_compatibility": gate_order_compatibility,
        "report_metric_order_compatibility": report_order_compatibility,
        "chart_preflight": chart_preflight,
        "ambient_assay": ambient["assay_status"],
        "pilot_execution": pilot["execution_status"],
        "pilot_assay": pilot["assay_status"],
        "pilot_full_claim": pilot["full_developmental_claim"],
        "permitted_retained_failures": seen,
        "all_other_packaged_checks": "PASS",
        "checkpoint_evaluation_replay": "PASS",
        "aggregate_recomputation": "PASS",
        "paired_analysis_recomputation": "PASS",
        "gate_readjudication": "PASS",
        "report_replay": "PASS",
        "chart_pixel_replay": "PASS",
        "source_digest": source_digest,
    }
    retained_receipt = vp.require_mapping(
        vp.load_json(
            "results/packet_closure_pilot/ARCHIVAL_VERIFICATION.json"
        ),
        "archival verification receipt",
    )
    vp.require(
        vp.closure.strict_json_equal(retained_receipt, output),
        "archival verification receipt mismatch",
    )
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
