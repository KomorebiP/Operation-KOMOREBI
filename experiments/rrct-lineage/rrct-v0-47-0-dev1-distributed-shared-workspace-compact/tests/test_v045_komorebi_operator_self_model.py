"""Focused checks for the RRCT v0.45 Komorebi operator integration."""
from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path

import numpy as np

from rrct.komorebi_operator_self_model import (
    KOMOREBI_VERSION,
    KOMOREBI_WHEEL_SHA256,
    KomorebiTransformationalSelfContinuityController,
    discover_controllable_packets,
    validate_komorebi_assessment_chain,
    validate_komorebi_operator_assessment_receipt,
    validate_komorebi_transformational_receipt_chain,
)
from rrct.komorebi_operator_self_model_experiment import (
    OperatorBenchmarkConfig,
    V045_MODES,
    _case,
    evaluate_operator_case,
    run_operator_benchmark,
    run_v044_bridge_compatibility,
)
from rrct.transformational_self_continuity import _digest
from rrct.transformational_self_continuity_experiment import (
    V044_EXPOSED_TUNING_SEEDS,
    _actual_task_values,
    _evidence_receipt,
    _make_root,
    _other_seed,
    _scenario_material,
    _task_material,
)


def _one_integrated_decision():
    seeds = V044_EXPOSED_TUNING_SEEDS
    seed = seeds[0]
    other = _other_seed(seed, seeds)
    root = _make_root(seed, seeds)
    scenario = "basis_remap"
    trial = 0
    time = 4_500_000
    material = _scenario_material(seed, other, scenario, trial, root)
    coarse = [
        _evidence_receipt(
            seed=seed,
            scenario=scenario,
            trial=trial,
            root=root,
            spec=spec,
            level="coarse",
            time=time,
        )
        for spec in material.candidates
    ]
    refined = {
        spec.candidate_id: _evidence_receipt(
            seed=seed,
            scenario=scenario,
            trial=trial,
            root=root,
            spec=spec,
            level="refined",
            time=time,
        )
        for spec in material.candidates
    }
    task = _task_material(
        seed=seed,
        scenario=scenario,
        trial=trial,
        time=time + 1,
        root=root,
        material=material,
    )
    actual = _actual_task_values(task, material)
    controller = KomorebiTransformationalSelfContinuityController(root)
    transition = controller.begin_transition(
        time=time, coarse_evidence=coarse, intervention_mode="intact"
    )
    adjudication = controller.commit_transition(
        transition,
        refined_evidence=[
            refined[candidate]
            for candidate in transition.refinement_requested_candidate_ids
        ],
    )
    plan = controller.plan_successor_task(adjudication, task)
    outcome = controller.observe_outcome(
        adjudication,
        plan,
        float(actual[plan.selected_candidate_index, plan.selected_action_index]),
        reveal_time=time + 2,
        register_selected_successor=True,
    )
    return controller, transition, adjudication, plan, task, outcome, material


def test_vendored_komorebi_identity_and_projector_discovery() -> None:
    dynamics = np.diag([0.8, 0.6, 0.4, 0.2])
    actuation = np.array([[1.0], [1.0], [0.0], [0.0]])
    self_projector, world_projector, receipt = discover_controllable_packets(
        dynamics, actuation
    )
    assert KOMOREBI_VERSION == "1.0.0b4"
    assert KOMOREBI_WHEEL_SHA256 == (
        "7d51e3040aea84f6d540936c2427376205ef8660d44b6841c2848c542e628adb"
    )
    assert receipt.packet_certificate_valid
    assert receipt.hilbert_certificate_valid
    assert receipt.atlas_certificate_valid
    assert receipt.controllable_rank == 2
    assert np.linalg.norm(self_projector + world_projector - np.eye(4)) < 1e-10
    assert np.linalg.norm(self_projector @ world_projector) < 1e-10


def test_komorebi_projector_transport_survives_unknown_basis_change() -> None:
    config = OperatorBenchmarkConfig()
    case = _case(45101, 0, "no_change", config)
    row = evaluate_operator_case(case, "komorebi_packets", config)
    assert row["predicted_change_class"] == "no_change"
    assert row["change_class_correct"] == 1.0
    assert row["projector_discovery_valid"] == 1.0
    assert row["projector_transport_residual"] < 0.01


def test_packet_change_attribution_beats_coordinate_and_global_controls() -> None:
    result = run_operator_benchmark(
        (45101, 45102), trials_per_scenario=3, modes=V045_MODES
    )
    assert result["all_endpoints_met"]
    summaries = result["mode_summaries"]
    assert summaries["komorebi_packets"]["change_class_accuracy"] == 1.0
    assert (
        summaries["komorebi_packets"]["change_class_accuracy"]
        > summaries["coordinate_split"]["change_class_accuracy"]
    )
    assert (
        summaries["komorebi_packets"]["change_class_accuracy"]
        > summaries["global_residual"]["change_class_accuracy"]
    )


def test_packet_recompression_preserves_low_energy_self_memory() -> None:
    config = OperatorBenchmarkConfig()
    case = _case(45102, 2, "mixed_change", config)
    packet = evaluate_operator_case(case, "komorebi_packets", config)
    cut = evaluate_operator_case(case, "resolution_cut", config)
    assert packet["packet_self_memory_error"] < 1e-8
    assert packet["global_self_memory_error"] > 0.95
    assert packet["self_memory_task_error"] < 1e-8
    assert cut["self_memory_task_error"] > 0.95


def test_integrated_controller_preserves_v044_behavior_and_emits_operator_chain() -> None:
    controller, transition, adjudication, plan, task, outcome, material = (
        _one_integrated_decision()
    )
    assert tuple(adjudication.relations) == tuple(
        spec.true_relation for spec in material.candidates
    )
    receipts = controller.komorebi_operator_receipts
    assert receipts
    assert all(validate_komorebi_operator_assessment_receipt(r) for r in receipts)
    assert validate_komorebi_transformational_receipt_chain(
        transition=transition,
        adjudication=adjudication,
        plan=plan,
        task=task,
        outcome=outcome,
        operator_receipts=receipts,
    )
    snapshot = controller.snapshot()
    assert snapshot["komorebi_version"] == KOMOREBI_VERSION
    assert snapshot["komorebi_operator_receipt_count"] == len(receipts)
    assert not snapshot["uses_evaluator_labels"]


def test_individual_and_cross_assessment_receipts_are_bound() -> None:
    controller, *_ = _one_integrated_decision()
    # Select a final committed assessment.  Coarse assessments are also
    # receipt-bound but are intentionally not retained in the committed map.
    assessments = []
    for committed in controller._committed.values():
        assessments.extend(committed.assessments.values())
    by_digest = {value.digest: value for value in assessments}
    operator = next(
        value
        for value in controller.komorebi_operator_receipts
        if value.integrated_assessment_digest in by_digest
    )
    assessment = by_digest[operator.integrated_assessment_digest]
    assert validate_komorebi_assessment_chain(assessment, operator)

    tampered = replace(operator, integrated_assessment_digest="0" * 64, digest="")
    payload = asdict(tampered)
    payload.pop("digest")
    tampered = replace(tampered, digest=_digest(payload))
    assert validate_komorebi_operator_assessment_receipt(tampered)
    assert not validate_komorebi_assessment_chain(assessment, tampered)


def test_rehashed_operator_misbinding_breaks_complete_chain() -> None:
    controller, transition, adjudication, plan, task, outcome, _ = (
        _one_integrated_decision()
    )
    receipts = list(controller.komorebi_operator_receipts)
    target = receipts[0]
    tampered = replace(target, integrated_assessment_digest="f" * 64, digest="")
    payload = asdict(tampered)
    payload.pop("digest")
    receipts[0] = replace(tampered, digest=_digest(payload))
    assert validate_komorebi_operator_assessment_receipt(receipts[0])
    assert not validate_komorebi_transformational_receipt_chain(
        transition=transition,
        adjudication=adjudication,
        plan=plan,
        task=task,
        outcome=outcome,
        operator_receipts=receipts,
    )


def test_v044_bridge_compatibility_has_no_observed_regression() -> None:
    result = run_v044_bridge_compatibility(trials_per_scenario=1)
    assert result["all_endpoints_met"]
    baseline = result["summaries"]["v044_baseline"]
    bridge = result["summaries"]["komorebi_bridge"]
    assert bridge["relation_exact_rate"] >= baseline["relation_exact_rate"]
    assert bridge["task_accuracy"] >= baseline["task_accuracy"]
    assert bridge["operator_chain_valid_rate"] == 1.0
    assert bridge["mean_operator_receipt_count"] > 0.0


def test_preoutcome_freeze_verifies_when_present() -> None:
    root = Path(__file__).resolve().parents[1]
    freeze = root / "validation/V0_45_PREOUTCOME_FREEZE.json"
    if not freeze.exists():
        return
    payload = json.loads(freeze.read_text(encoding="utf-8"))
    assert payload["schema"] == "rrct.v045.preoutcome_freeze.v1"
    assert payload["status"] == "frozen_before_holdout_execution"
    assert payload["files"]
    for entry in payload["files"]:
        path = root / entry["relative_path"]
        assert path.is_file()
        assert path.stat().st_size == entry["size_bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
