"""RRCT v0.40 robust reflexive-diagnosis experiment.

This successor preserves the v0.39 evaluator-blind consequence-grounding and
action path.  It adds a prequential two-timescale diagnostic receipt that must
separate world-model change from causal-boundary failure, public-access-path
failure, explicit boundary absence, and restoration in one persistent runtime.
"""
from __future__ import annotations

import copy
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict
from typing import Any

from .agent import RRCTAgent
from .autonomous_self_diagnosis import (
    ConsequenceGroundingConfig,
    GroundingOutcomeReceipt,
)
from .autonomous_self_diagnosis_experiment import (
    V039_ACCESS_FAULT_PHASE,
    V039_ACCESS_FAULT_START_OFFSET,
    V039_ACCESS_FAULT_STEPS,
    V039_MAX_ACCESS_FAULT_DIAGNOSIS_LATENCY,
    V039_MIN_REMAP_CORRECT_ACTIONS,
    V039_MIN_RESTORE_CORRECT_ACTIONS,
    V039_MIN_SHOCK_CORRECT_ACTIONS,
    _V039FaultInjectableAgent,
    _agent_v039,
    _build_v039_summary,
    _wrap_v039_row,
)
from .causal_boundary import CausalBoundaryConfig, DIRECT_ACCESS_SNAPSHOT_SCHEMA
from .post_change_closure_experiment import (
    V037_D1_CONFIG,
    V037ExperimentConfig,
    V037_MIN_CORRECT_TAIL_ACTIONS,
    run_post_change_closure_trace,
)
from .robust_reflexive_diagnosis import (
    ReflexiveDiagnosisReceipt,
    RobustReflexiveDiagnosisConfig,
    RobustReflexiveDiagnosticUnifiedCausalLoop,
    validate_reflexive_diagnosis_receipt,
)
from .unified_causal_loop import UnifiedCausalLoop, UnifiedCausalLoopConfig
from .unified_causal_loop_experiment import _json_sha256

V040_VERSION = "0.40.0.dev1"
V040_ROW_SCHEMA = "rrct.v040.robust_reflexive_diagnosis.row.v1"
V040_SUMMARY_SCHEMA = "rrct.v040.robust_reflexive_diagnosis.summary.v1"
V040_DEVELOPMENT_SEED = 40001
V040_PILOT_SEEDS = (54975, 30328, 23875, 81356)
V040_FIRST_PILOT_SEED = V040_PILOT_SEEDS[0]
V040_MAX_WORLD_SHIFT_DIAGNOSIS_LATENCY = 32


def _receipt_mapping(receipt: ReflexiveDiagnosisReceipt) -> dict[str, Any]:
    return copy.deepcopy(asdict(receipt))


def _wrap_v040_row(
    v039_row: Mapping[str, Any],
    *,
    grounding: GroundingOutcomeReceipt,
    reflexive: ReflexiveDiagnosisReceipt,
) -> dict[str, Any]:
    wrapped = copy.deepcopy(dict(v039_row))
    v039_schema = wrapped.get("schema")
    v039_sha = _json_sha256(wrapped)
    wrapped["schema"] = V040_ROW_SCHEMA
    wrapped["v039_row_schema"] = v039_schema
    wrapped["v039_row_sha256"] = v039_sha
    wrapped["robust_reflexive_diagnosis"] = _receipt_mapping(reflexive)
    wrapper_payload = {
        "v039_row_sha256": v039_sha,
        "grounding_digest": grounding.digest,
        "reflexive_digest": reflexive.digest,
    }
    wrapped["v040_wrapper_digest"] = _json_sha256(wrapper_payload)
    wrapped["v040_wrapper_integrity"] = bool(
        wrapped.get("v039_wrapper_integrity", False)
        and v039_schema == "rrct.v039.autonomous_self_diagnosis.row.v1"
        and reflexive.time == int(wrapped["transition_index"])
        and reflexive.inherited_grounding_digest == grounding.digest
        and validate_reflexive_diagnosis_receipt(reflexive)
        and not reflexive.uses_evaluator_labels
    )
    return wrapped


def _phase_rows(
    rows: Sequence[Mapping[str, Any]], phase: str
) -> list[Mapping[str, Any]]:
    return [row for row in rows if row["phase"] == phase]


def _reflexive_event_rows(
    rows: Sequence[Mapping[str, Any]], event: str
) -> list[Mapping[str, Any]]:
    return [
        row
        for row in rows
        if event in row["robust_reflexive_diagnosis"]["events"]
    ]


def _grounding_event_rows(
    rows: Sequence[Mapping[str, Any]], event: str
) -> list[Mapping[str, Any]]:
    return [
        row
        for row in rows
        if event in row["autonomous_grounding"]["events"]
    ]


def _first_grounding_event(
    rows: Sequence[Mapping[str, Any]], event: str, phase: str
) -> Mapping[str, Any] | None:
    candidates = [
        row
        for row in rows
        if row["phase"] == phase
        and event in row["autonomous_grounding"]["events"]
    ]
    return min(candidates, key=lambda row: int(row["phase_offset"])) if candidates else None


def _build_v040_summary(
    seed: int,
    rows: Sequence[Mapping[str, Any]],
    v039_summary: Mapping[str, Any],
    runtime: RobustReflexiveDiagnosticUnifiedCausalLoop,
    agent: RRCTAgent,
    experiment_config: V037ExperimentConfig,
) -> dict[str, Any]:
    reflexive_snapshot = runtime.reflexive_snapshot
    grounding_snapshot = runtime.grounding_snapshot
    access_snapshot = agent.causal_boundary_snapshot()["access_readout"]

    shift_rows = _reflexive_event_rows(rows, "external_dynamics_shift")
    shock_shift_rows = [row for row in shift_rows if row["phase"] == "world_shock"]
    nonshock_shift_rows = [row for row in shift_rows if row["phase"] != "world_shock"]
    shift_offsets = [int(row["phase_offset"]) for row in shock_shift_rows]

    access_failure = _first_grounding_event(rows, "access_path_failure", "stable")
    access_restored = _first_grounding_event(rows, "access_path_restored", "stable")
    remap_revoked = _first_grounding_event(
        rows, "certificate_revoked_by_consequence", "remap"
    )
    disconnect_absent = _first_grounding_event(rows, "boundary_absent", "disconnect")
    restore_reacquired = _first_grounding_event(rows, "boundary_restored", "restore")

    response_counts: dict[str, int] = {}
    diagnosis_counts: dict[str, int] = {}
    for row in rows:
        payload = row["robust_reflexive_diagnosis"]
        response = str(payload["recommended_response"])
        diagnosis = str(payload["diagnosis"])
        response_counts[response] = response_counts.get(response, 0) + 1
        diagnosis_counts[diagnosis] = diagnosis_counts.get(diagnosis, 0) + 1

    condition_specific = {
        "world_shift_updates_world_model": bool(
            len(shock_shift_rows) == 1
            and shock_shift_rows[0]["robust_reflexive_diagnosis"]["diagnosis"]
            == "external_dynamics_shift"
            and shock_shift_rows[0]["robust_reflexive_diagnosis"][
                "recommended_response"
            ]
            == "retain_boundary_and_update_world_model"
            and shock_shift_rows[0]["robust_reflexive_diagnosis"][
                "causal_efficacy_intact"
            ]
        ),
        "remap_reconstructs_boundary": bool(
            remap_revoked is not None
            and remap_revoked["robust_reflexive_diagnosis"]["diagnosis"]
            == "boundary_effect_failed"
            and remap_revoked["robust_reflexive_diagnosis"][
                "recommended_response"
            ]
            == "retest_and_reconstruct_causal_boundary"
        ),
        "disconnection_suspends_boundary_action": bool(
            disconnect_absent is not None
            and disconnect_absent["robust_reflexive_diagnosis"]["diagnosis"]
            == "boundary_absent"
            and disconnect_absent["robust_reflexive_diagnosis"][
                "recommended_response"
            ]
            == "suspend_boundary_dependent_action"
        ),
        "restoration_resumes_boundary_action": bool(
            restore_reacquired is not None
            and restore_reacquired["robust_reflexive_diagnosis"]["diagnosis"]
            == "boundary_restored"
            and restore_reacquired["robust_reflexive_diagnosis"][
                "recommended_response"
            ]
            == "resume_boundary_dependent_action"
        ),
        "access_failure_repairs_access_path": bool(
            access_failure is not None
            and access_failure["robust_reflexive_diagnosis"]["diagnosis"]
            == "access_path_failure"
            and access_failure["robust_reflexive_diagnosis"][
                "recommended_response"
            ]
            == "repair_or_reopen_public_access_path"
        ),
        "access_restoration_resumes_access_path": bool(
            access_restored is not None
            and access_restored["robust_reflexive_diagnosis"]["diagnosis"]
            == "access_path_restored"
            and access_restored["robust_reflexive_diagnosis"][
                "recommended_response"
            ]
            == "resume_public_access_path"
        ),
    }

    integrity = {
        "row_count_exact": len(rows) == int(experiment_config.total_steps),
        "all_v039_wrappers_valid": all(
            bool(row.get("v039_wrapper_integrity")) for row in rows
        ),
        "all_v040_wrappers_valid": all(
            bool(row.get("v040_wrapper_integrity")) for row in rows
        ),
        "direct_access_schema_exact": (
            access_snapshot.get("schema") == DIRECT_ACCESS_SNAPSHOT_SCHEMA
        ),
        "zero_access_label_updates": bool(
            access_snapshot.get("uses_class_labels") is False
            and int(access_snapshot.get("update_count", -1)) == 0
            and all(int(row["causal_access_updates"]) == 0 for row in rows)
        ),
        "grounding_uses_no_evaluator_labels": bool(
            grounding_snapshot["uses_evaluator_labels"] is False
            and all(
                row["autonomous_grounding"]["uses_evaluator_labels"] is False
                for row in rows
            )
        ),
        "reflexive_monitor_uses_no_evaluator_labels": bool(
            reflexive_snapshot["uses_evaluator_labels"] is False
            and all(
                row["robust_reflexive_diagnosis"]["uses_evaluator_labels"]
                is False
                for row in rows
            )
        ),
        "world_shift_counter_matches_rows": int(
            reflexive_snapshot["world_shift_count"]
        )
        == len(shift_rows),
    }

    inherited = v039_summary["endpoints"]
    endpoints = {
        "H01_integrity_and_oracle_exclusion": bool(all(integrity.values())),
        "H02_self_selected_consequence_certification": bool(
            inherited["H02_self_selected_consequence_certification"]
        ),
        "H03_stable_and_shock_retention": bool(
            inherited["H03_stable_and_shock_retention"]
        ),
        "H04_consequence_detected_remap_and_recovery": bool(
            inherited["H04_consequence_detected_remap_and_recovery"]
        ),
        "H05_disconnection_absence_and_null_action": bool(
            inherited["H05_disconnection_absence_and_null_action"]
        ),
        "H06_restoration_reacquisition_and_action": bool(
            inherited["H06_restoration_reacquisition_and_action"]
        ),
        "H07_robust_world_versus_self_diagnostic_transfer": bool(
            len(shock_shift_rows) == 1
            and not nonshock_shift_rows
            and shift_offsets[0] <= V040_MAX_WORLD_SHIFT_DIAGNOSIS_LATENCY
            and condition_specific["world_shift_updates_world_model"]
        ),
        "H08_internal_access_fault_differential_diagnosis": bool(
            inherited["H08_internal_access_fault_differential_diagnosis"]
        ),
        "H09_condition_specific_response_policy": bool(
            all(condition_specific.values())
        ),
    }
    all_met = bool(all(endpoints.values()))
    return {
        "schema": V040_SUMMARY_SCHEMA,
        "version": V040_VERSION,
        "scientific_status": "developmental_robust_reflexive_diagnosis",
        "seed": int(seed),
        "monitor": {
            "config": asdict(reflexive_snapshot["config"]),
            "snapshot_digest": reflexive_snapshot["digest"],
            "world_shift_count": int(reflexive_snapshot["world_shift_count"]),
            "world_stabilization_count": int(
                reflexive_snapshot["world_stabilization_count"]
            ),
            "uses_evaluator_labels": False,
        },
        "world_shift_diagnosis": {
            "count": len(shift_rows),
            "world_shock_count": len(shock_shift_rows),
            "nonworld_count": len(nonshock_shift_rows),
            "world_shock_offsets": shift_offsets,
            "maximum_allowed_latency": V040_MAX_WORLD_SHIFT_DIAGNOSIS_LATENCY,
            "rows": [
                {
                    "transition_index": int(row["transition_index"]),
                    "phase": row["phase"],
                    "phase_offset": int(row["phase_offset"]),
                    "metrics": copy.deepcopy(row["robust_reflexive_diagnosis"]),
                }
                for row in shift_rows
            ],
        },
        "condition_specific_response_policy": condition_specific,
        "diagnosis_counts": diagnosis_counts,
        "recommended_response_counts": response_counts,
        "integrity": integrity,
        "endpoints": endpoints,
        "all_endpoints_met": all_met,
        "earliest_failed_layer": next(
            (name for name, value in endpoints.items() if not value), None
        ),
        "status": (
            "V040_DEVELOPMENT_ENDPOINTS_MET"
            if all_met
            else "V040_DEVELOPMENT_ENDPOINTS_NOT_MET"
        ),
        "v039_inherited_summary": copy.deepcopy(v039_summary),
        "interpretation_boundary": (
            "Evidence for oracle-free active certificate grounding plus robust "
            "world-versus-self differential diagnosis in a bounded synthetic "
            "persistent runtime. No phenomenal-awareness claim is made."
        ),
    }


def run_robust_reflexive_diagnosis_trace(
    seed: int,
    *,
    experiment_config: V037ExperimentConfig = V037_D1_CONFIG,
    boundary_config: CausalBoundaryConfig | None = None,
    runtime_config: UnifiedCausalLoopConfig | None = None,
    grounding_config: ConsequenceGroundingConfig | None = None,
    reflexive_config: RobustReflexiveDiagnosisConfig | None = None,
    inject_access_fault: bool = True,
    sealed_row_sink: Callable[[Mapping[str, Any]], None] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    created_agents: list[RRCTAgent] = []
    created_runtimes: list[RobustReflexiveDiagnosticUnifiedCausalLoop] = []
    wrapped_rows: list[dict[str, Any]] = []

    def agent_factory(config: CausalBoundaryConfig, run_seed: int) -> RRCTAgent:
        agent = _agent_v039(config, run_seed)
        created_agents.append(agent)
        return agent

    def runtime_factory(
        agent: RRCTAgent, config: UnifiedCausalLoopConfig
    ) -> RobustReflexiveDiagnosticUnifiedCausalLoop:
        runtime = RobustReflexiveDiagnosticUnifiedCausalLoop(
            agent,
            config,
            grounding_config=grounding_config,
            reflexive_config=reflexive_config,
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
            raise RuntimeError("v0.40 access-fault agent type was lost")
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
            raise RuntimeError("v0.40 row arrived before runtime construction")
        agent = created_agents[0]
        runtime = created_runtimes[0]
        result = agent.last_result
        grounding = runtime.last_grounding_outcome
        reflexive = runtime.last_reflexive_outcome
        if result is None or grounding is None or reflexive is None:
            raise RuntimeError("v0.40 row arrived without diagnostic telemetry")
        v039_row = _wrap_v039_row(
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
        wrapped = _wrap_v040_row(
            v039_row,
            grounding=grounding,
            reflexive=reflexive,
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
        raise RuntimeError("v0.40 did not retain one persistent runtime")
    v039_summary = _build_v039_summary(
        int(seed),
        wrapped_rows,
        v037_summary,
        created_runtimes[0],
        created_agents[0],
        experiment_config,
    )
    summary = _build_v040_summary(
        int(seed),
        wrapped_rows,
        v039_summary,
        created_runtimes[0],
        created_agents[0],
        experiment_config,
    )
    return wrapped_rows, summary


__all__ = [
    "V040_FIRST_PILOT_SEED",
    "V040_PILOT_SEEDS",
    "V040_ROW_SCHEMA",
    "V040_SUMMARY_SCHEMA",
    "run_robust_reflexive_diagnosis_trace",
]
