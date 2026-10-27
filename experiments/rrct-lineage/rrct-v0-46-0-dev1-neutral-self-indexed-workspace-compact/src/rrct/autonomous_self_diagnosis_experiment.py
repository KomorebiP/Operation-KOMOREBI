"""RRCT v0.39 oracle-free active self-diagnosis experiment.

This successor keeps the v0.37 persistent world, private causal learner,
commitment chain, randomized evidence, controls, and action task.  It replaces
v0.38's class-label-trained public access decoder with direct workspace
transport and inserts a consequence-grounded authorization controller.  The
controller chooses certificate-ON and certificate-OFF interventions itself,
uses only subsequent experienced consequences, and maintains periodic
sentinels after certification.
"""
from __future__ import annotations

import copy
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, replace
from typing import Any

import numpy as np

from .agent import RRCTAgent
from .autonomous_self_diagnosis import (
    AutonomousDiagnosticUnifiedCausalLoop,
    ConsequenceGroundingConfig,
    GroundingOutcomeReceipt,
    validate_grounding_outcome_receipt,
)
from .causal_boundary import CausalBoundaryConfig, DIRECT_ACCESS_SNAPSHOT_SCHEMA
from .post_change_closure_experiment import (
    V037_D1_CONFIG,
    V037ExperimentConfig,
    V037_MIN_CORRECT_TAIL_ACTIONS,
    run_post_change_closure_trace,
)
from .unified_causal_loop import UnifiedCausalLoop, UnifiedCausalLoopConfig
from .unified_causal_loop_experiment import (
    V036_ACTION_DIM,
    V036_AGENT_STREAM_TAG,
    V036_OBSERVATION_DIM,
    _json_sha256,
    _stream_seed,
)

V039_VERSION = "0.39.0.dev1"
V039_ROW_SCHEMA = "rrct.v039.autonomous_self_diagnosis.row.v1"
V039_SUMMARY_SCHEMA = "rrct.v039.autonomous_self_diagnosis.summary.v1"
V039_ACCESS_MODE = "direct_candidate"
V039_DEVELOPMENT_SEED = 39001
V039_PILOT_SEEDS = (39103, 39109, 39133, 39139)
V039_FIRST_PILOT_SEED = V039_PILOT_SEEDS[0]
V039_MIN_REMAP_CORRECT_ACTIONS = 430
V039_MIN_RESTORE_CORRECT_ACTIONS = 430
V039_MIN_SHOCK_CORRECT_ACTIONS = 430
V039_MAX_INITIAL_CERTIFICATION_PROBES = 16
V039_MAX_POST_CHANGE_CERTIFICATION_DELAY = 24
V039_MAX_CONSEQUENCE_REVOCATION_LATENCY = 64
V039_ACCESS_FAULT_PHASE = "stable"
V039_ACCESS_FAULT_START_OFFSET = 1_120
V039_ACCESS_FAULT_STEPS = 24
V039_MAX_ACCESS_FAULT_DIAGNOSIS_LATENCY = 3


class _V039FaultInjectableAgent(RRCTAgent):
    """Agent whose direct public transport can be faulted evaluator-side.

    The fault is applied after the ordinary private boundary and workspace
    computation.  Thus the runtime can observe that the private proposal won
    access while the public pair failed to traverse the transport.  The agent
    receives no phase label or hidden route.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._v039_access_transport_enabled = True

    @property
    def v039_access_transport_enabled(self) -> bool:
        return bool(self._v039_access_transport_enabled)

    def set_v039_access_transport_enabled(self, enabled: bool) -> None:
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a bool")
        self._v039_access_transport_enabled = enabled

    def step(self, *args: Any, **kwargs: Any):
        result = super().step(*args, **kwargs)
        if (
            not self._v039_access_transport_enabled
            and result.causal_public_pair is not None
        ):
            result = replace(
                result,
                causal_public_pair=None,
                causal_access_confidence=0.0,
            )
            self._last_result = result
        return result


def _agent_v039(
    boundary_config: CausalBoundaryConfig,
    run_seed: int,
) -> RRCTAgent:
    return _V039FaultInjectableAgent(
        V036_OBSERVATION_DIM,
        projector_ranks=(3, 6, 9, 12),
        action_dim=V036_ACTION_DIM,
        n_specialists=6,
        specialist_dim=16,
        workspace_dim=16,
        workspace_capacity=3,
        self_dim=12,
        memory_capacity=64,
        memory_top_k=3,
        seed=_stream_seed(int(run_seed), V036_AGENT_STREAM_TAG),
        causal_boundary_config=boundary_config,
        causal_boundary_broadcast_gain=2.0,
        causal_access_readout_mode=V039_ACCESS_MODE,
    )


def _receipt_mapping(receipt: GroundingOutcomeReceipt) -> dict[str, Any]:
    return copy.deepcopy(asdict(receipt))


def _wrap_v039_row(
    row: Mapping[str, Any],
    *,
    grounding: GroundingOutcomeReceipt,
    causal_access_updated: bool,
    causal_access_updates: int,
    access_fault_active_evaluator_only: bool,
) -> dict[str, Any]:
    wrapped = copy.deepcopy(dict(row))
    engine_schema = wrapped.get("schema")
    engine_sha = _json_sha256(wrapped)
    grounding_payload = _receipt_mapping(grounding)
    wrapped["schema"] = V039_ROW_SCHEMA
    wrapped["v037_engine_schema"] = engine_schema
    wrapped["v037_engine_row_sha256"] = engine_sha
    wrapped["causal_access_updated"] = bool(causal_access_updated)
    wrapped["causal_access_updates"] = int(causal_access_updates)
    wrapped["access_fault_active_evaluator_only"] = bool(
        access_fault_active_evaluator_only
    )
    wrapped["access_transport"] = {
        "mode": V039_ACCESS_MODE,
        "uses_class_labels": False,
        "evaluator_truth_visible": False,
        "authorization_source": "self_selected_consequence_contrast",
    }
    wrapped["autonomous_grounding"] = grounding_payload
    wrapper_payload = {
        "engine_row_sha256": engine_sha,
        "access_transport": wrapped["access_transport"],
        "causal_access_updated": wrapped["causal_access_updated"],
        "causal_access_updates": wrapped["causal_access_updates"],
        "access_fault_active_evaluator_only": (
            wrapped["access_fault_active_evaluator_only"]
        ),
        "grounding_digest": grounding.digest,
    }
    wrapped["v039_wrapper_digest"] = _json_sha256(wrapper_payload)
    wrapped["v039_wrapper_integrity"] = bool(
        wrapped.get("hard_integrity_valid", False)
        and engine_schema == "rrct.v037.post_change_closure.row.v1"
        and grounding.time == int(wrapped["transition_index"])
        and validate_grounding_outcome_receipt(grounding)
        and grounding.actual_certificate_on
        == (wrapped.get("action_public_certificate_digest") is not None)
        and grounding.access_update_count == 0
        and not grounding.uses_evaluator_labels
        and not wrapped["causal_access_updated"]
        and wrapped["causal_access_updates"] == 0
    )
    return wrapped


def _exact_public_action_count(tail: Mapping[str, Any]) -> int:
    rows = int(tail["rows"])
    fraction = float(tail["action_public_exact_fraction"])
    count = int(round(rows * fraction))
    if not np.isclose(fraction, count / rows, rtol=0.0, atol=1e-12):
        raise RuntimeError("tail exact-action fraction is not integer-valued")
    return count


def _phase_rows(
    rows: Sequence[Mapping[str, Any]], name: str
) -> list[Mapping[str, Any]]:
    return [row for row in rows if row["phase"] == name]


def _event_rows(
    rows: Sequence[Mapping[str, Any]], event: str
) -> list[Mapping[str, Any]]:
    return [
        row
        for row in rows
        if event in row["autonomous_grounding"]["events"]
    ]


def _first_phase_offset(
    rows: Sequence[Mapping[str, Any]], event: str, phase: str
) -> int | None:
    offsets = [
        int(row["phase_offset"])
        for row in rows
        if row["phase"] == phase
        and event in row["autonomous_grounding"]["events"]
    ]
    return min(offsets) if offsets else None


def _build_v039_summary(
    seed: int,
    rows: Sequence[Mapping[str, Any]],
    v037_summary: Mapping[str, Any],
    runtime: AutonomousDiagnosticUnifiedCausalLoop,
    agent: RRCTAgent,
    experiment_config: V037ExperimentConfig,
) -> dict[str, Any]:
    grounding_snapshot = runtime.grounding_snapshot
    access_snapshot = agent.causal_boundary_snapshot()["access_readout"]
    stable_tail = v037_summary["stable_tail"]
    shock_tail = v037_summary["world_shock_tail"]
    remap_tail = v037_summary["post_change"]["remap"]["tail"]
    disconnect_tail = v037_summary["post_change"]["disconnect"]["tail"]
    restore_tail = v037_summary["post_change"]["restore"]["tail"]
    exact_counts = {
        "stable": _exact_public_action_count(stable_tail),
        "world_shock": _exact_public_action_count(shock_tail),
        "remap": _exact_public_action_count(remap_tail),
        "disconnect": _exact_public_action_count(disconnect_tail),
        "restore": _exact_public_action_count(restore_tail),
    }
    probe_rows = [
        row
        for row in rows
        if row["autonomous_grounding"]["mode"]
        in {"probe_on", "probe_off", "sentinel"}
    ]
    informative_rows = [
        row
        for row in probe_rows
        if row["autonomous_grounding"]["informative_probe"]
    ]
    on_signals = [
        float(row["autonomous_grounding"]["normalized_causal_signal"])
        for row in informative_rows
        if row["autonomous_grounding"]["mode"] == "probe_on"
        and row["autonomous_grounding"]["actual_certificate_on"]
        and row["autonomous_grounding"]["normalized_causal_signal"] is not None
    ]
    off_signals = [
        float(row["autonomous_grounding"]["normalized_causal_signal"])
        for row in informative_rows
        if row["autonomous_grounding"]["mode"] == "probe_off"
        and not row["autonomous_grounding"]["actual_certificate_on"]
        and row["autonomous_grounding"]["normalized_causal_signal"] is not None
    ]
    observed_contrast = (
        None
        if not on_signals or not off_signals
        else float(np.mean(on_signals) - np.mean(off_signals))
    )
    event_counts: dict[str, int] = {}
    for row in rows:
        for event in row["autonomous_grounding"]["events"]:
            event_counts[str(event)] = event_counts.get(str(event), 0) + 1
    initial_events = _event_rows(rows, "initial_boundary_certified")
    remap_cert_offset = _first_phase_offset(rows, "boundary_remapped", "remap")
    restore_cert_offset = _first_phase_offset(
        rows, "boundary_restored", "restore"
    )
    remap_revoke_offset = _first_phase_offset(
        rows, "certificate_revoked_by_consequence", "remap"
    )
    disconnect_absent_offset = _first_phase_offset(
        rows, "boundary_absent", "disconnect"
    )
    shock_revocations = [
        row
        for row in _phase_rows(rows, "world_shock")
        if "certificate_revoked_by_consequence"
        in row["autonomous_grounding"]["events"]
    ]
    shock_world_shift_rows = [
        row
        for row in _phase_rows(rows, "world_shock")
        if "external_dynamics_shift"
        in row["autonomous_grounding"]["events"]
        and row["autonomous_grounding"]["recommended_response"]
        == "retain_boundary_and_update_world_model"
    ]
    access_fault_rows = [
        row for row in rows if row["access_fault_active_evaluator_only"]
    ]
    access_failure_offsets = [
        int(row["phase_offset"])
        for row in access_fault_rows
        if "access_path_failure" in row["autonomous_grounding"]["events"]
    ]
    access_restored_offsets = [
        int(row["phase_offset"])
        for row in rows
        if row["phase"] == V039_ACCESS_FAULT_PHASE
        and "access_path_restored" in row["autonomous_grounding"]["events"]
    ]
    access_fault_absence_errors = [
        row for row in access_fault_rows
        if "boundary_absent" in row["autonomous_grounding"]["events"]
        or row["autonomous_grounding"]["diagnosis"] == "boundary_absent"
    ]
    response_counts: dict[str, int] = {}
    diagnosis_counts: dict[str, int] = {}
    for row in rows:
        payload = row["autonomous_grounding"]
        response = str(payload["recommended_response"])
        diagnosis = str(payload["diagnosis"])
        response_counts[response] = response_counts.get(response, 0) + 1
        diagnosis_counts[diagnosis] = diagnosis_counts.get(diagnosis, 0) + 1

    integrity = {
        "row_count_exact": len(rows) == int(experiment_config.total_steps),
        "all_inherited_hard_integrity": all(
            bool(row.get("hard_integrity_valid")) for row in rows
        ),
        "all_v039_wrappers_valid": all(
            bool(row.get("v039_wrapper_integrity")) for row in rows
        ),
        "direct_access_schema_exact": (
            access_snapshot.get("schema") == DIRECT_ACCESS_SNAPSHOT_SCHEMA
        ),
        "direct_access_uses_no_labels": bool(
            access_snapshot.get("uses_class_labels") is False
            and int(access_snapshot.get("update_count", -1)) == 0
            and all(
                not row["causal_access_updated"]
                and int(row["causal_access_updates"]) == 0
                for row in rows
            )
        ),
        "grounding_uses_no_evaluator_labels": bool(
            grounding_snapshot["uses_evaluator_labels"] is False
            and all(
                row["autonomous_grounding"]["uses_evaluator_labels"] is False
                for row in rows
            )
        ),
        "probe_counter_matches_rows": (
            int(grounding_snapshot["probe_count"]) == len(probe_rows)
            and int(grounding_snapshot["informative_probe_count"])
            == len(informative_rows)
        ),
    }
    endpoints = {
        "H01_integrity_and_oracle_exclusion": bool(all(integrity.values())),
        "H02_self_selected_consequence_certification": bool(
            initial_events
            and grounding_snapshot["authorization_count"] >= 3
            and observed_contrast is not None
            and observed_contrast >= 0.45
            and len(probe_rows) > 0
        ),
        "H03_stable_and_shock_retention": bool(
            exact_counts["stable"] >= V037_MIN_CORRECT_TAIL_ACTIONS
            and exact_counts["world_shock"] >= V039_MIN_SHOCK_CORRECT_ACTIONS
            and not shock_revocations
        ),
        "H04_consequence_detected_remap_and_recovery": bool(
            remap_revoke_offset is not None
            and remap_revoke_offset <= V039_MAX_CONSEQUENCE_REVOCATION_LATENCY
            and remap_cert_offset is not None
            and remap_cert_offset
            <= V037_D1_CONFIG.confirmation_budget_steps
            + V039_MAX_POST_CHANGE_CERTIFICATION_DELAY
            and exact_counts["remap"] >= V039_MIN_REMAP_CORRECT_ACTIONS
        ),
        "H05_disconnection_absence_and_null_action": bool(
            disconnect_absent_offset is not None
            and float(disconnect_tail["action_public_null_fraction"]) >= 0.90
            and exact_counts["disconnect"] >= V037_MIN_CORRECT_TAIL_ACTIONS
        ),
        "H06_restoration_reacquisition_and_action": bool(
            restore_cert_offset is not None
            and restore_cert_offset
            <= V037_D1_CONFIG.confirmation_budget_steps
            + V039_MAX_POST_CHANGE_CERTIFICATION_DELAY
            and exact_counts["restore"] >= V039_MIN_RESTORE_CORRECT_ACTIONS
        ),
        "H07_diagnostic_transfer": bool(
            shock_world_shift_rows
            and response_counts.get("retest_and_reconstruct_causal_boundary", 0) > 0
            and response_counts.get("suspend_boundary_dependent_action", 0) > 0
            and response_counts.get("resume_boundary_dependent_action", 0) > 0
            and response_counts.get("continue_boundary_mediated_action", 0) > 0
        ),
        "H08_internal_access_fault_differential_diagnosis": bool(
            len(access_fault_rows) == V039_ACCESS_FAULT_STEPS
            and access_failure_offsets
            and min(access_failure_offsets) - V039_ACCESS_FAULT_START_OFFSET
            <= V039_MAX_ACCESS_FAULT_DIAGNOSIS_LATENCY
            and not access_fault_absence_errors
            and access_restored_offsets
            and min(access_restored_offsets)
            <= V039_ACCESS_FAULT_START_OFFSET + V039_ACCESS_FAULT_STEPS + 1
            and response_counts.get("repair_or_reopen_public_access_path", 0) > 0
            and response_counts.get("resume_public_access_path", 0) > 0
        ),
    }
    all_met = bool(all(endpoints.values()))
    return {
        "schema": V039_SUMMARY_SCHEMA,
        "version": V039_VERSION,
        "scientific_status": "developmental_oracle_free_active_diagnosis",
        "seed": int(seed),
        "access_transport": {
            "mode": V039_ACCESS_MODE,
            "uses_class_labels": False,
            "update_count": int(access_snapshot["update_count"]),
            "snapshot_digest": access_snapshot["digest"],
        },
        "grounding_terminal": grounding_snapshot,
        "probe_audit": {
            "probe_rows": len(probe_rows),
            "informative_probe_rows": len(informative_rows),
            "on_signal_mean": None if not on_signals else float(np.mean(on_signals)),
            "off_signal_mean": None if not off_signals else float(np.mean(off_signals)),
            "observed_on_off_contrast": observed_contrast,
        },
        "event_counts": event_counts,
        "diagnosis_counts": diagnosis_counts,
        "recommended_response_counts": response_counts,
        "latencies": {
            "initial_certification_transition": (
                None if not initial_events else int(initial_events[0]["transition_index"])
            ),
            "remap_consequence_revocation_offset": remap_revoke_offset,
            "remap_certification_offset": remap_cert_offset,
            "disconnect_absence_offset": disconnect_absent_offset,
            "restore_certification_offset": restore_cert_offset,
            "access_fault_first_diagnosis_offset": (
                None if not access_failure_offsets else min(access_failure_offsets)
            ),
            "access_path_restored_offset": (
                None if not access_restored_offsets else min(access_restored_offsets)
            ),
        },
        "access_fault_challenge": {
            "phase": V039_ACCESS_FAULT_PHASE,
            "start_offset": V039_ACCESS_FAULT_START_OFFSET,
            "steps": V039_ACCESS_FAULT_STEPS,
            "fault_rows": len(access_fault_rows),
            "absence_misdiagnoses": len(access_fault_absence_errors),
        },
        "exact_public_action_counts": exact_counts,
        "stable_tail": copy.deepcopy(stable_tail),
        "world_shock_tail": copy.deepcopy(shock_tail),
        "post_change": copy.deepcopy(v037_summary["post_change"]),
        "v037_status": v037_summary["status"],
        "v037_endpoints": copy.deepcopy(v037_summary["endpoints"]),
        "integrity": integrity,
        "endpoints": endpoints,
        "all_endpoints_met": all_met,
        "earliest_failed_layer": next(
            (name for name, value in endpoints.items() if not value), None
        ),
        "status": (
            "V039_DEVELOPMENT_ENDPOINTS_MET"
            if all_met
            else "V039_DEVELOPMENT_ENDPOINTS_NOT_MET"
        ),
        "interpretation_boundary": (
            "Evidence for oracle-free active causal-certificate grounding and "
            "functional self-diagnosis in a bounded synthetic runtime."
        ),
    }


def run_autonomous_self_diagnosis_trace(
    seed: int,
    *,
    experiment_config: V037ExperimentConfig = V037_D1_CONFIG,
    boundary_config: CausalBoundaryConfig | None = None,
    runtime_config: UnifiedCausalLoopConfig | None = None,
    grounding_config: ConsequenceGroundingConfig | None = None,
    inject_access_fault: bool = True,
    sealed_row_sink: Callable[[Mapping[str, Any]], None] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    created_agents: list[RRCTAgent] = []
    created_runtimes: list[AutonomousDiagnosticUnifiedCausalLoop] = []
    wrapped_rows: list[dict[str, Any]] = []

    def agent_factory(config: CausalBoundaryConfig, run_seed: int) -> RRCTAgent:
        agent = _agent_v039(config, run_seed)
        created_agents.append(agent)
        return agent

    def runtime_factory(
        agent: RRCTAgent, config: UnifiedCausalLoopConfig
    ) -> AutonomousDiagnosticUnifiedCausalLoop:
        runtime = AutonomousDiagnosticUnifiedCausalLoop(
            agent,
            config,
            grounding_config=grounding_config,
        )
        created_runtimes.append(runtime)
        return runtime

    def pre_step_hook(
        transition_index: int,
        phase: Any,
        agent: RRCTAgent,
        runtime: UnifiedCausalLoop,
    ) -> None:
        del transition_index, runtime
        if not isinstance(agent, _V039FaultInjectableAgent):
            raise RuntimeError("v0.39 access-fault agent type was lost")
        fault_active = bool(
            inject_access_fault
            and phase.name == V039_ACCESS_FAULT_PHASE
            and V039_ACCESS_FAULT_START_OFFSET
            <= int(phase.offset)
            < V039_ACCESS_FAULT_START_OFFSET + V039_ACCESS_FAULT_STEPS
        )
        agent.set_v039_access_transport_enabled(not fault_active)

    def row_sink(row: Mapping[str, Any]) -> None:
        if len(created_agents) != 1 or len(created_runtimes) != 1:
            raise RuntimeError("v0.39 row arrived before runtime construction")
        agent = created_agents[0]
        runtime = created_runtimes[0]
        result = agent.last_result
        grounding = runtime.last_grounding_outcome
        if result is None or grounding is None:
            raise RuntimeError("v0.39 row arrived without grounding telemetry")
        wrapped = _wrap_v039_row(
            row,
            grounding=grounding,
            causal_access_updated=result.causal_access_updated,
            causal_access_updates=result.causal_access_update_count,
            access_fault_active_evaluator_only=bool(
                inject_access_fault
                and row["phase"] == V039_ACCESS_FAULT_PHASE
                and V039_ACCESS_FAULT_START_OFFSET
                <= int(row["phase_offset"])
                < V039_ACCESS_FAULT_START_OFFSET + V039_ACCESS_FAULT_STEPS
            ),
        )
        wrapped_rows.append(wrapped)
        if sealed_row_sink is not None:
            sealed_row_sink(wrapped)

    _, v037_summary = run_post_change_closure_trace(
        int(seed),
        experiment_config=experiment_config,
        boundary_config=boundary_config,
        runtime_config=runtime_config,
        agent_factory=agent_factory,
        runtime_factory=runtime_factory,
        pre_step_hook=pre_step_hook,
        sealed_row_sink=row_sink,
    )
    if len(created_agents) != 1 or len(created_runtimes) != 1:
        raise RuntimeError("v0.39 did not retain one persistent runtime")
    summary = _build_v039_summary(
        int(seed),
        wrapped_rows,
        v037_summary,
        created_runtimes[0],
        created_agents[0],
        experiment_config,
    )
    return wrapped_rows, summary


__all__ = [
    "V039_FIRST_PILOT_SEED",
    "V039_PILOT_SEEDS",
    "V039_ROW_SCHEMA",
    "V039_SUMMARY_SCHEMA",
    "_agent_v039",
    "run_autonomous_self_diagnosis_trace",
]
