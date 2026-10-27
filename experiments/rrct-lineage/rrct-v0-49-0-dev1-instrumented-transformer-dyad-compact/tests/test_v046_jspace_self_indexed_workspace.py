"""Focused checks for RRCT v0.46 neutral self-indexed workspace."""
from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path

import numpy as np

from rrct.jspace_self_indexed_workspace import (
    NeutralSelfIndexedWorkspaceController,
    discover_jacobian_workspace,
    make_content_origin_receipt,
    validate_self_indexed_workspace_receipt,
    validate_workspace_closure_chain,
    validate_workspace_planning_receipt,
)
from rrct.jspace_self_indexed_workspace_experiment import (
    NeutralWorkspaceBenchmarkConfig,
    _ablation_probe,
    _case_spec,
    _evaluate_case,
    _mode_controller,
    _subspace_controls,
    _origin,
    _swap_probe,
    _workspace,
    _world,
    run_neutral_workspace_benchmark,
)
from rrct.transformational_self_continuity import _digest
from rrct.transformational_self_continuity_experiment import (
    V044_EXPOSED_TUNING_SEEDS,
    _make_root,
)


def test_jacobian_workspace_is_recovered_and_selective() -> None:
    config = NeutralWorkspaceBenchmarkConfig(calibration_samples=256)
    world = _world(46011, config)
    workspace = _workspace(world)
    receipt = workspace.discovery_receipt
    true_projector = world.concept_basis @ world.concept_basis.T
    overlap = float(np.trace(workspace.projector @ true_projector) / config.concept_count)
    assert receipt.workspace_rank == config.concept_count
    assert receipt.calibration_report_r2 > 0.99
    assert receipt.workspace_activation_variance_fraction < 0.10
    assert overlap > 0.999999
    assert receipt.packet_certificate_valid
    assert receipt.hilbert_certificate_valid
    assert receipt.atlas_certificate_valid


def test_jacobian_workspace_beats_variance_and_random_subspaces() -> None:
    world = _world(46011, NeutralWorkspaceBenchmarkConfig(calibration_samples=256))
    workspace = _workspace(world)
    controls = _subspace_controls(world, workspace)
    assert controls["jacobian_report_accuracy"] > 0.99
    assert controls["pca_report_accuracy"] < 0.30
    assert controls["random_report_accuracy"] < 0.40
    assert controls["pca_activation_variance_fraction"] > (
        workspace.discovery_receipt.workspace_activation_variance_fraction
    )


def test_workspace_swap_redirects_report_reasoning_and_flexible_use() -> None:
    world = _world(46012, NeutralWorkspaceBenchmarkConfig(calibration_samples=256))
    workspace = _workspace(world)
    row = _swap_probe(world, workspace, 3)
    assert row["report_swap_success"] == 1.0
    assert row["flexible_broadcast_swap_success"] == 1.0
    assert row["reasoning_swap_success"] == 1.0
    assert row["automatic_route_preserved"] == 1.0


def test_workspace_ablation_spares_routine_processing_but_breaks_access() -> None:
    world = _world(46013, NeutralWorkspaceBenchmarkConfig(calibration_samples=256))
    workspace = _workspace(world)
    rows = [_ablation_probe(world, workspace, trial) for trial in range(16)]
    assert np.mean([row["intact_report_correct"] for row in rows]) == 1.0
    assert np.mean([row["intact_flexible_correct"] for row in rows]) == 1.0
    assert np.mean([row["ablated_routine_correct"] for row in rows]) == 1.0
    assert np.mean([row["ablated_flexible_correct"] for row in rows]) < 0.35


def test_full_closure_separates_access_from_autobiographical_ownership() -> None:
    world = _world(46014, NeutralWorkspaceBenchmarkConfig(calibration_samples=256))
    workspace = _workspace(world)
    full = _evaluate_case(
        world, workspace, scenario="injected_workspace", trial=0, mode="full_closure"
    )
    access_only = _evaluate_case(
        world, workspace, scenario="injected_workspace", trial=0, mode="workspace_only"
    )
    unbound = _evaluate_case(
        world, workspace, scenario="injected_workspace", trial=0, mode="unbound"
    )
    assert full["initial_provenance_status"] == "quarantined_external"
    assert full["initial_memory_action"] == "quarantine"
    assert full["used_refinement"] == 1.0
    assert full["task_correct"] == 1.0
    assert access_only["workspace_enabled"] == 1.0
    assert access_only["initial_memory_action"] == "none"
    assert access_only["task_correct"] == 0.0
    assert unbound["workspace_enabled"] == 1.0
    assert unbound["initial_memory_action"] == "none"


def test_identical_workspace_content_does_not_erase_origin_difference() -> None:
    world = _world(46011, NeutralWorkspaceBenchmarkConfig(calibration_samples=256))
    workspace = _workspace(world)
    full = _evaluate_case(
        world,
        workspace,
        scenario="injected_same_content",
        trial=0,
        mode="full_closure",
    )
    cut = _evaluate_case(
        world,
        workspace,
        scenario="injected_same_content",
        trial=0,
        mode="provenance_cut",
    )
    assert full["workspace_content_correct"] == 1.0
    assert full["initial_provenance_status"] == "quarantined_external"
    assert full["initial_memory_action"] == "quarantine"
    assert cut["workspace_content_correct"] == 1.0
    assert cut["false_autobiographical_write"] == 1.0


def test_provenance_cut_writes_foreign_content_as_self() -> None:
    world = _world(46011, NeutralWorkspaceBenchmarkConfig(calibration_samples=256))
    workspace = _workspace(world)
    intact = _evaluate_case(
        world, workspace, scenario="foreign_memory", trial=1, mode="full_closure"
    )
    cut = _evaluate_case(
        world, workspace, scenario="foreign_memory", trial=1, mode="provenance_cut"
    )
    assert intact["false_autobiographical_write"] == 0.0
    assert intact["initial_memory_action"] == "quarantine"
    assert cut["false_autobiographical_write"] == 1.0
    assert cut["initial_memory_action"] in {"write_observed", "write_inferred"}


def test_planner_binding_is_distinct_from_correct_workspace_and_ownership() -> None:
    world = _world(46012, NeutralWorkspaceBenchmarkConfig(calibration_samples=256))
    workspace = _workspace(world)
    intact = _evaluate_case(
        world, workspace, scenario="flexible_use", trial=2, mode="full_closure"
    )
    cut = _evaluate_case(
        world,
        workspace,
        scenario="flexible_use",
        trial=2,
        mode="planner_binding_cut",
    )
    assert intact["workspace_content_correct"] == 1.0
    assert intact["memory_action_correct"] == 1.0
    assert intact["task_correct"] == 1.0
    assert cut["workspace_content_correct"] == 1.0
    assert cut["memory_action_correct"] == 1.0
    assert cut["planner_bound"] == 0.0


def test_feedback_recurrence_changes_the_next_evidence_request() -> None:
    result = run_neutral_workspace_benchmark(
        (46011, 46012), trials_per_scenario=1
    )
    full = result["mode_summaries"]["full_closure"]
    cut = result["mode_summaries"]["recurrence_cut"]
    assert full["feedback_reopen_rate"] == 1.0
    assert full["feedback_second_decision_accuracy"] == 1.0
    assert cut["feedback_reopen_rate"] == 0.0
    assert cut["feedback_second_decision_accuracy"] == 0.0


def test_rehashed_but_misbound_plan_fails_complete_chain() -> None:
    config = NeutralWorkspaceBenchmarkConfig(calibration_samples=256)
    world = _world(46013, config)
    workspace = _workspace(world)
    controller = _mode_controller(world, workspace)
    spec = _case_spec(world, "verbal_report", 0)
    hidden = world.encode(spec["presented_concept"], spec["automatic"], noise_seed=1)
    access = controller.access(
        time=1, case_id="tamper", hidden=hidden, mode="full_closure"
    )
    origin = _origin(
        world,
        time=1,
        event_type=spec["event_type"],
        content_id=spec["presented_concept"],
        origin_lineage=spec["origin_lineage"],
        parent=spec["parent"],
    )
    binding = controller.bind(access, origin, mode="full_closure")
    plan = controller.plan(
        time=2,
        case_id="tamper",
        mode="full_closure",
        access=access,
        binding=binding,
        task_kind="report",
        query_id=0,
        answer_lookup=world.answer_lookup(),
        routine_answer=spec["automatic"],
        relation_lookup=world.relation_lookup(),
    )
    outcome = controller.observe(
        time=3,
        case_id="tamper",
        mode="full_closure",
        plan=plan,
        actual_answer=spec["presented_concept"],
    )
    assert validate_workspace_closure_chain(
        workspace.discovery_receipt, origin, access, binding, plan, outcome
    )
    tampered = replace(plan, self_index_receipt_digest="0" * 64, digest="")
    payload = asdict(tampered)
    payload.pop("digest")
    tampered = replace(tampered, digest=_digest(payload))
    assert validate_workspace_planning_receipt(tampered)
    assert not validate_workspace_closure_chain(
        workspace.discovery_receipt, origin, access, binding, tampered, outcome
    )


def test_workspace_accepts_an_actual_rrct_lineage_digest() -> None:
    seeds = V044_EXPOSED_TUNING_SEEDS
    root = _make_root(seeds[0], seeds)
    world = _world(46014, NeutralWorkspaceBenchmarkConfig(calibration_samples=256))
    workspace = _workspace(world)
    parent = _digest({"actual_rrct_lineage": root.digest, "event": "observation"})
    controller = NeutralSelfIndexedWorkspaceController(
        workspace,
        root.digest,
        known_current_ancestor_digests=(parent,),
    )
    hidden = world.encode(2, 3, noise_seed=9)
    access = controller.access(
        time=1, case_id="rrct-lineage", hidden=hidden, mode="full_closure"
    )
    origin = make_content_origin_receipt(
        time=1,
        event_type="observation",
        content_id=2,
        origin_lineage_digest=root.digest,
        current_lineage_digest=root.digest,
        parent_event_digest=parent,
    )
    binding = controller.bind(access, origin, mode="full_closure")
    assert validate_self_indexed_workspace_receipt(binding)
    assert binding.provenance_status == "owned_observation"
    assert binding.autobiographical_write_authorized


def test_development_benchmark_meets_all_declared_endpoints() -> None:
    result = run_neutral_workspace_benchmark(
        (46011, 46012), trials_per_scenario=3
    )
    assert result["all_endpoints_met"], [
        key for key, value in result["endpoints"].items() if not value
    ]
    assert result["mode_summaries"]["full_closure"]["functional_closure_score"] == 1.0
    assert (
        result["mode_summaries"]["workspace_only"]["flexible_task_accuracy"]
        > result["mode_summaries"]["self_model_only"]["flexible_task_accuracy"]
    )
    assert (
        result["mode_summaries"]["full_closure"]["memory_action_accuracy"]
        > result["mode_summaries"]["unbound"]["memory_action_accuracy"]
    )


def test_preoutcome_freeze_verifies_when_present() -> None:
    root = Path(__file__).resolve().parents[1]
    freeze = root / "validation/V0_46_PREOUTCOME_FREEZE.json"
    if not freeze.exists():
        return
    payload = json.loads(freeze.read_text(encoding="utf-8"))
    assert payload["schema"] == "rrct.v046.preoutcome_freeze.v1"
    assert payload["status"] == "frozen_before_holdout_execution"
    for entry in payload["files"]:
        path = root / entry["relative_path"]
        assert path.is_file()
        assert path.stat().st_size == entry["size_bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
