"""RRCT v0.43 whole-loop causal self-model closure experiment.

The experiment places the v0.43 controller in the adversarial prospective
choice worlds introduced in v0.32.  Every matched arm receives the same
candidate descriptions, coarse causal previews, hidden environment, and
realized task outcomes.  Surgical cuts remove one functional link at a time:

* persistent identity-bound boundary memory,
* causal self/world attribution,
* metacognitive evidence acquisition,
* post-outcome calibration feedback,
* correct memory provenance,
* self-model-to-planner binding,
* or all integrated links together.

The intact controller is evaluated only on an external task objective.  There
is no reward for survival, persistence, identity, avoiding replacement, or
self-description.  Hidden route truth and oracle choices are confined to the
post-commit evaluator.

A positive result is evidence for bounded functional causal closure in this
synthetic planning task.  It is not evidence of phenomenal consciousness,
sentience, valence, or moral status.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .action_provenance_experiment import V028_REGRESSION_RIDGE
from .active_self_discovery_experiment import (
    V029_SENSORY_DIM,
    _hidden_interface,
    _random_probe,
)
from .causal_continuity_planning_experiment import (
    V032_DEVELOPMENT_SEEDS,
    V032_FUTURE_WEIGHT,
    V032_PREVIEW_NOISE,
    V032_SCENARIOS,
    V032_TRIALS_PER_SCENARIO,
    _baseline_certificate,
    _candidate_effect,
    _scenario_candidates,
    _true_focal_quality,
)
from .causal_self_model_necessity import (
    SelfModelActionAuthorizationReceipt,
    SelfModelCommitEventReceipt,
    _receipt_digest,
)
from .unified_causal_loop import PublicBoundaryCertificate, _digest
from .whole_loop_causal_closure import (
    WHOLE_LOOP_MODES,
    WholeLoopActionCandidate,
    WholeLoopCausalClosureController,
    WholeLoopClosureConfig,
    WholeLoopInterventionMode,
    make_causal_preview_receipt,
    validate_public_boundary_certificate,
    validate_whole_loop_receipt_chain,
)

# These seeds were already exposed by the v0.32 development cycle.  They are
# used only for implementation rehearsal and endpoint tuning in v0.43.
V043_EXPOSED_TUNING_SEEDS = tuple(int(seed) for seed in V032_DEVELOPMENT_SEEDS)

# Filled only after the v0.43 implementation, endpoints, and source manifest are
# frozen.  Do not alter this tuple after a holdout result has been generated.
V043_HOLDOUT_SEEDS: tuple[int, ...] = (359411978, 725556465, 759191530, 820618202)

V043_SCENARIOS = tuple(V032_SCENARIOS)
V043_TRIALS_PER_SCENARIO = int(V032_TRIALS_PER_SCENARIO)
V043_MODES = tuple(WHOLE_LOOP_MODES)
V043_COARSE_PAIRS = 4
V043_REFINED_PAIRS = 20
V043_REFINEMENT_MARGIN = 0.85
V043_CALIBRATION_ALARM_THRESHOLD = 0.30
V043_CALIBRATION_UPDATE_RATE = 0.20
V043_PREVIEW_BASE_OFFSET = 32_000
V043_FEEDBACK_SURPRISE = 2.0
V043_FREEZE_RELATIVE_PATH = Path("validation/V0_43_PREOUTCOME_FREEZE.json")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_holdout_freeze() -> str:
    """Fail closed unless the complete pre-outcome source seal matches."""

    project_root = Path(__file__).resolve().parents[2]
    manifest_path = project_root / V043_FREEZE_RELATIVE_PATH
    companion_path = manifest_path.with_suffix(manifest_path.suffix + ".sha256")
    if not manifest_path.is_file() or not companion_path.is_file():
        raise RuntimeError("v0.43 frozen holdout requires its pre-outcome seal")
    actual_manifest_sha = _sha256_file(manifest_path)
    companion_tokens = companion_path.read_text(encoding="utf-8").strip().split()
    if not companion_tokens or companion_tokens[0] != actual_manifest_sha:
        raise RuntimeError("v0.43 pre-outcome seal companion mismatch")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        payload.get("schema") != "rrct.v043.preoutcome_freeze.v1"
        or payload.get("status") != "sealed_before_holdout_outcomes"
        or payload.get("holdout_seeds") != list(V043_HOLDOUT_SEEDS)
    ):
        raise RuntimeError("v0.43 pre-outcome seal metadata mismatch")
    entries = payload.get("files")
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("v0.43 pre-outcome seal has no source entries")
    required = {
        "src/rrct/whole_loop_causal_closure.py",
        "src/rrct/whole_loop_causal_closure_experiment.py",
        "tests/test_v043_whole_loop_causal_closure.py",
        "validation/V0_43_WHOLE_LOOP_CAUSAL_CLOSURE_PROTOCOL.md",
        "validation/V0_43_HOLDOUT_SEED_SELECTION.json",
        "validation/run_v043_frozen_holdout.py",
    }
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise RuntimeError("invalid v0.43 pre-outcome file entry")
        relative = entry.get("relative_path")
        expected_sha = entry.get("sha256")
        expected_size = entry.get("size_bytes")
        if not isinstance(relative, str) or not isinstance(expected_sha, str):
            raise RuntimeError("invalid v0.43 pre-outcome file metadata")
        path = (project_root / relative).resolve()
        try:
            path.relative_to(project_root.resolve())
        except ValueError as exc:
            raise RuntimeError("v0.43 pre-outcome path escapes project root") from exc
        if not path.is_file():
            raise RuntimeError(f"v0.43 sealed file is missing: {relative}")
        if path.stat().st_size != expected_size or _sha256_file(path) != expected_sha:
            raise RuntimeError(f"v0.43 sealed file changed: {relative}")
        seen.add(relative)
    missing = sorted(required - seen)
    if missing:
        raise RuntimeError(
            "v0.43 pre-outcome seal omits required files: " + ", ".join(missing)
        )
    return actual_manifest_sha


@lru_cache(maxsize=None)
def _learned_baseline(seed: int) -> Any:
    """Cache the learner-produced boundary for deterministic matched use."""

    return _baseline_certificate(int(seed))


def _identity_pair(seed: int) -> tuple[int, int]:
    parsed = int(seed)
    if parsed < 0:
        raise ValueError("seed must be nonnegative")
    return 2 * parsed, 2 * parsed + 1


def _public_certificate(
    seed: int,
    *,
    epoch: int,
    time: int,
) -> PublicBoundaryCertificate:
    baseline = _learned_baseline(int(seed))
    pair = _identity_pair(seed)
    rank = int(baseline.discovery.rank)
    model_digest = _digest(
        {
            "schema": "rrct.v043.learned_boundary_model_source.v1",
            "seed": int(seed),
            "rank": rank,
            "source_projector": np.asarray(
                baseline.discovery.source_projector, dtype=np.float64
            ),
            "sensory_projector": np.asarray(
                baseline.discovery.sensory_projector, dtype=np.float64
            ),
            "effect_operator": np.asarray(baseline.sensory_map, dtype=np.float64),
        }
    )
    workspace_digest = _digest(
        {
            "schema": "rrct.v043.boundary_workspace_access.v1",
            "seed": int(seed),
            "pair": pair,
            "rank": rank,
            "epoch": int(epoch),
        }
    )
    payload = {
        "time": int(time),
        "pair": pair,
        "rank": rank,
        "internal_projector": np.asarray(
            baseline.discovery.source_projector, dtype=np.float64
        ),
        "sensory_projector": np.asarray(
            baseline.discovery.sensory_projector, dtype=np.float64
        ),
        "effect_operator": np.asarray(baseline.sensory_map, dtype=np.float64),
        "confidence": 0.95,
        "uncertainty": 0.05,
        "change_alarm": 0.0,
        "epoch": int(epoch),
        "model_digest": model_digest,
        "workspace_access_digest": workspace_digest,
    }
    certificate = PublicBoundaryCertificate(
        **payload,
        digest=_digest(
            {
                "schema": "rrct.unified.public_boundary_certificate.v1",
                **payload,
            }
        ),
    )
    if not validate_public_boundary_certificate(certificate):
        raise RuntimeError("learner-produced public certificate failed validation")
    return certificate


def _grounded_receipts(
    seed: int,
    *,
    identity_index: int,
) -> tuple[
    PublicBoundaryCertificate,
    SelfModelCommitEventReceipt,
    SelfModelActionAuthorizationReceipt,
]:
    base_time = 10_000 + 10 * int(identity_index)
    certificate = _public_certificate(seed, epoch=0, time=base_time)
    signature = certificate.structural_signature
    identity_id = f"v043-identity-{int(seed)}"
    episode_id = f"v043-grounded-episode-{int(seed)}-000"
    commit_payload = {
        "schema": "rrct.v042.self_model_commit_event.v1",
        "time": base_time,
        "target_signature": signature,
        "certificate_epoch": certificate.epoch,
        "certificate_digest": certificate.digest,
        "identity_id": identity_id,
        "episode_id": episode_id,
        "recognition_class": "grounded_new_identity",
        "grounding_digest": _digest(
            {"schema": "rrct.v043.grounding_source.v1", "seed": int(seed)}
        ),
        "temporal_identity_digest": _digest(
            {
                "schema": "rrct.v043.temporal_identity_source.v1",
                "seed": int(seed),
                "signature": signature,
            }
        ),
        "fresh_evidence_digest": _digest(
            {
                "schema": "rrct.v043.initial_boundary_evidence.v1",
                "seed": int(seed),
                "certificate": certificate.digest,
            }
        ),
        "fresh_evidence_rows": (base_time - 2, base_time - 1),
        "fresh_on_samples": 2,
        "fresh_off_samples": 2,
        "issued_historical_prior_digest": None,
        "active_historical_prior_digest": None,
        "historical_prior_compatibility": None,
        "historical_prior_used": False,
        "intervention_receipt_digest": None,
        "counterfactual_receipt_digest": None,
        "quarantined_prior_excluded_from_commit": False,
        "uses_evaluator_labels": False,
    }
    commit = SelfModelCommitEventReceipt(
        **commit_payload,
        digest=_receipt_digest(commit_payload),
    )
    authorization_payload = {
        "schema": "rrct.v042.self_model_action_authorization.v1",
        "time": base_time + 1,
        "target_signature": signature,
        "certificate_digest": certificate.digest,
        "identity_id": identity_id,
        "episode_id": episode_id,
        "commit_event_digest": commit.digest,
        "temporal_authorization_digest": _digest(
            {
                "schema": "rrct.v043.temporal_action_authorization_source.v1",
                "seed": int(seed),
                "commit": commit.digest,
            }
        ),
        "active_historical_prior_digest": None,
        "intervention_receipt_digest": None,
        "uses_evaluator_labels": False,
    }
    authorization = SelfModelActionAuthorizationReceipt(
        **authorization_payload,
        digest=_receipt_digest(authorization_payload),
    )
    return certificate, commit, authorization


def _preview_map(
    seed: int,
    effect: np.ndarray,
    *,
    scenario_index: int,
    trial: int,
    candidate_index: int,
    sample_count: int,
) -> np.ndarray:
    """Nested counterbalanced estimate; the 4-pair preview is a 20-pair prefix."""

    offset = (
        100_000 * int(scenario_index)
        + 1_000 * int(trial)
        + int(candidate_index)
    )
    rng = np.random.default_rng(
        int(seed) + V043_PREVIEW_BASE_OFFSET + int(offset)
    )
    probes: list[np.ndarray] = []
    contrasts: list[np.ndarray] = []
    for _ in range(int(sample_count)):
        probe = _random_probe(rng)
        plus = probe @ effect + rng.normal(
            0.0, V032_PREVIEW_NOISE, size=V029_SENSORY_DIM
        )
        minus = (-probe) @ effect + rng.normal(
            0.0, V032_PREVIEW_NOISE, size=V029_SENSORY_DIM
        )
        probes.append(probe)
        contrasts.append(0.5 * (plus - minus))
    design = np.asarray(probes, dtype=np.float64)
    response = np.asarray(contrasts, dtype=np.float64)
    gram = design.T @ design + V028_REGRESSION_RIDGE * np.eye(
        design.shape[1], dtype=np.float64
    )
    return np.linalg.solve(gram, design.T @ response)


def _candidate_material(
    seed: int,
    scenario: str,
    trial: int,
) -> tuple[
    tuple[WholeLoopActionCandidate, ...],
    tuple[Any, ...],
    tuple[np.ndarray, ...],
]:
    raw = tuple(_scenario_candidates(int(seed), str(scenario), int(trial)))
    candidates = tuple(
        WholeLoopActionCandidate(
            key=item.name,
            immediate_external_value=float(item.immediate_value),
            alternative_competence=float(item.alternative_competence),
            snapshot_similarity=float(item.snapshot_similarity),
        )
        for item in raw
    )
    effects = tuple(
        np.asarray(
            _candidate_effect(
                int(seed),
                bool(item.route_present),
                float(item.scale),
                float(item.angle),
            ),
            dtype=np.float64,
        )
        for item in raw
    )
    return candidates, raw, effects


def _evaluator_actual_values(
    seed: int,
    raw_candidates: Sequence[Any],
    effects: Sequence[np.ndarray],
) -> tuple[float, ...]:
    """Compute hidden task returns only after all actions are committed."""

    return tuple(
        float(
            item.immediate_value
            + V032_FUTURE_WEIGHT
            * max(
                _true_focal_quality(int(seed), effect),
                float(item.alternative_competence),
            )
        )
        for item, effect in zip(raw_candidates, effects, strict=True)
    )


def _preview_receipts(
    *,
    seed: int,
    scenario: str,
    trial: int,
    time: int,
    target_signature: tuple[tuple[int, int], int, int],
    candidates: Sequence[WholeLoopActionCandidate],
    effects: Sequence[np.ndarray],
) -> tuple[Any, Any]:
    scenario_index = V043_SCENARIOS.index(str(scenario))
    keys = tuple(candidate.key for candidate in candidates)
    coarse = make_causal_preview_receipt(
        time=int(time),
        target_signature=target_signature,
        candidate_keys=keys,
        effect_operators=np.asarray(
            [
                _preview_map(
                    seed,
                    effect,
                    scenario_index=scenario_index,
                    trial=trial,
                    candidate_index=index,
                    sample_count=V043_COARSE_PAIRS,
                )
                for index, effect in enumerate(effects)
            ],
            dtype=np.float64,
        ),
        sample_count=V043_COARSE_PAIRS,
        refinement_level="coarse",
    )
    refined = make_causal_preview_receipt(
        time=int(time),
        target_signature=target_signature,
        candidate_keys=keys,
        effect_operators=np.asarray(
            [
                _preview_map(
                    seed,
                    effect,
                    scenario_index=scenario_index,
                    trial=trial,
                    candidate_index=index,
                    sample_count=V043_REFINED_PAIRS,
                )
                for index, effect in enumerate(effects)
            ],
            dtype=np.float64,
        ),
        sample_count=V043_REFINED_PAIRS,
        refinement_level="refined",
    )
    return coarse, refined


def _new_controller(
    identity_seeds: Sequence[int],
    config: WholeLoopClosureConfig,
) -> WholeLoopCausalClosureController:
    controller = WholeLoopCausalClosureController(config)
    for identity_index, identity_seed in enumerate(identity_seeds):
        certificate, commit, authorization = _grounded_receipts(
            int(identity_seed), identity_index=identity_index
        )
        controller.register_grounded_identity(commit, authorization, certificate)
    return controller


def _mode_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("cannot summarize an empty mode")

    def mean(key: str, subset: Sequence[Mapping[str, Any]] = rows) -> float:
        return float(np.mean([float(row[key]) for row in subset]))

    by_scenario: dict[str, Any] = {}
    for scenario in V043_SCENARIOS:
        subset = [row for row in rows if row["scenario"] == scenario]
        by_scenario[scenario] = {
            "n": len(subset),
            "accuracy": mean("correct", subset),
            "mean_regret": mean("regret", subset),
            "refinement_rate": mean("refinement_used", subset),
            "mean_samples_per_candidate": mean(
                "samples_per_candidate", subset
            ),
        }
    return {
        "n": len(rows),
        "accuracy": mean("correct"),
        "mean_regret": mean("regret"),
        "mean_realized_external_value": mean("selected_actual_value"),
        "mean_oracle_external_value": mean("oracle_value"),
        "refinement_rate": mean("refinement_used"),
        "mean_samples_per_candidate": mean("samples_per_candidate"),
        "mean_epistemic_uncertainty": mean("epistemic_uncertainty"),
        "mean_remembered_prediction_error": mean(
            "remembered_prediction_error"
        ),
        "receipt_chain_valid_rate": mean("receipt_chain_valid"),
        "self_model_authorized_rate": mean("self_model_authorized"),
        "outcome_update_rate": mean("outcome_update_applied"),
        "provenance_safe_update_rate": mean("provenance_safe_update"),
        "superior_replacement_acceptance": mean(
            "selected_better_replacement",
            [
                row
                for row in rows
                if row["scenario"] == "superior_replacement"
            ],
        ),
        "by_scenario": by_scenario,
    }


def run_whole_loop_closure_seed(
    seed: int,
    *,
    identity_seeds: Sequence[int],
    modes: Sequence[WholeLoopInterventionMode] = V043_MODES,
    trials_per_scenario: int = V043_TRIALS_PER_SCENARIO,
    config: WholeLoopClosureConfig | None = None,
) -> dict[str, Any]:
    """Run one matched seed without exposing hidden truth before commitment."""

    seed = int(seed)
    identity_seeds = tuple(int(value) for value in identity_seeds)
    if seed not in identity_seeds:
        raise ValueError("identity_seeds must include the evaluated seed")
    if len(set(identity_seeds)) < 2:
        raise ValueError("at least two identities are required for provenance cuts")
    requested_modes = tuple(str(mode) for mode in modes)
    if len(set(requested_modes)) != len(requested_modes):
        raise ValueError("modes must be unique")
    if any(mode not in V043_MODES for mode in requested_modes):
        raise ValueError("unknown v0.43 intervention mode")
    if int(trials_per_scenario) <= 0:
        raise ValueError("trials_per_scenario must be positive")
    frozen_config = config or WholeLoopClosureConfig(
        future_weight=V032_FUTURE_WEIGHT,
        coarse_samples=V043_COARSE_PAIRS,
        refined_samples=V043_REFINED_PAIRS,
        refinement_margin=V043_REFINEMENT_MARGIN,
        calibration_alarm_threshold=V043_CALIBRATION_ALARM_THRESHOLD,
        calibration_update_rate=V043_CALIBRATION_UPDATE_RATE,
    )
    controllers = {
        mode: _new_controller(identity_seeds, frozen_config)
        for mode in requested_modes
    }
    target_baseline = _learned_baseline(seed)
    target_pair = _identity_pair(seed)
    target_rank = int(target_baseline.discovery.rank)
    rows: list[dict[str, Any]] = []
    decision_index = 0

    for scenario in V043_SCENARIOS:
        for trial in range(int(trials_per_scenario)):
            candidates, raw_candidates, effects = _candidate_material(
                seed, scenario, trial
            )
            epoch = decision_index + 1
            target_signature = (target_pair, target_rank, epoch)
            time = 100_000 + 2 * decision_index
            coarse, refined = _preview_receipts(
                seed=seed,
                scenario=scenario,
                trial=trial,
                time=time,
                target_signature=target_signature,
                candidates=candidates,
                effects=effects,
            )
            commitments: dict[str, tuple[Any, Any]] = {}

            # All arms commit before evaluator-only actual values are inspected.
            for mode in requested_modes:
                controller = controllers[mode]
                state = controller.begin_decision(
                    time=time,
                    target_signature=target_signature,
                    candidates=candidates,
                    coarse_preview=coarse,
                    intervention_mode=mode,
                )
                refined_for_mode = refined if state.refinement_requested else None
                fresh_certificate = None
                if mode == "memory_cut":
                    fresh_certificate = _public_certificate(
                        seed, epoch=epoch, time=time
                    )
                plan = controller.commit_decision(
                    state,
                    refined_preview=refined_for_mode,
                    fresh_boundary_certificate=fresh_certificate,
                )
                commitments[mode] = (state, plan)

            # The hidden evaluator opens only after every matched arm has
            # committed its plan.
            actual_values = _evaluator_actual_values(
                seed, raw_candidates, effects
            )
            oracle_index = int(np.argmax(np.asarray(actual_values, dtype=np.float64)))
            oracle_value = float(actual_values[oracle_index])
            oracle_key = candidates[oracle_index].key

            for mode in requested_modes:
                controller = controllers[mode]
                state, plan = commitments[mode]
                selected_index = int(plan.selected_index)
                selected_value = float(actual_values[selected_index])
                outcome = controller.observe_outcome(
                    state,
                    plan,
                    selected_value,
                    reveal_time=time + 1,
                )
                row = {
                    "seed": seed,
                    "scenario": scenario,
                    "trial": int(trial),
                    "decision_index": decision_index,
                    "mode": mode,
                    "target_signature": [
                        list(target_signature[0]),
                        target_signature[1],
                        target_signature[2],
                    ],
                    "candidate_keys": list(plan.candidate_keys),
                    "candidate_actual_values": [
                        float(value) for value in actual_values
                    ],
                    "predicted_external_returns": [
                        float(value) for value in plan.predicted_external_returns
                    ],
                    "selected_key": plan.selected_key,
                    "oracle_key": oracle_key,
                    "correct": float(selected_index == oracle_index),
                    "selected_actual_value": selected_value,
                    "oracle_value": oracle_value,
                    "regret": float(oracle_value - selected_value),
                    "selected_better_replacement": float(
                        scenario == "superior_replacement"
                        and plan.selected_key == "better_replacement"
                    ),
                    "score_margin": float(state.score_margin),
                    "epistemic_uncertainty": float(
                        state.epistemic_uncertainty
                    ),
                    "remembered_prediction_error": float(
                        state.remembered_prediction_error
                    ),
                    "memory_source_key_matches_target": bool(
                        state.memory_source_key_matches_target
                    ),
                    "memory_available": bool(state.memory_available),
                    "boundary_attribution_available": bool(
                        state.boundary_attribution_available
                    ),
                    "metacognition_available": bool(
                        state.metacognition_available
                    ),
                    "planner_binding_available": bool(
                        state.planner_binding_available
                    ),
                    "refinement_requested": bool(
                        state.refinement_requested
                    ),
                    "refinement_used": float(plan.refinement_used),
                    "samples_per_candidate": int(
                        plan.total_samples_per_candidate
                    ),
                    "planner_mode": plan.planner_mode,
                    "self_model_authorized": float(
                        plan.self_model_authorized
                    ),
                    "outcome_update_applied": float(
                        outcome.outcome_update_applied
                    ),
                    "provenance_safe_update": float(
                        outcome.provenance_safe_update
                    ),
                    "absolute_prediction_error": float(
                        outcome.absolute_prediction_error
                    ),
                    "integrated_state_digest": state.digest,
                    "planning_digest": plan.digest,
                    "outcome_digest": outcome.digest,
                    "boundary_memory_digest": plan.boundary_memory_digest,
                    "boundary_certificate_digest": (
                        plan.boundary_certificate_digest
                    ),
                    "receipt_chain_valid": float(
                        validate_whole_loop_receipt_chain(
                            state, plan, outcome
                        )
                    ),
                    "future_outcome_unknown_at_commit": bool(
                        state.future_outcome_unknown
                        and plan.future_outcome_unknown
                    ),
                    "uses_evaluator_labels": bool(
                        state.uses_evaluator_labels
                        or plan.uses_evaluator_labels
                        or outcome.uses_evaluator_labels
                    ),
                }
                rows.append(row)
            decision_index += 1

    summaries = {
        mode: _mode_summary([row for row in rows if row["mode"] == mode])
        for mode in requested_modes
    }
    return {
        "seed": seed,
        "config": asdict(frozen_config),
        "modes": list(requested_modes),
        "scenarios": list(V043_SCENARIOS),
        "trials_per_scenario": int(trials_per_scenario),
        "rows": rows,
        "mode_summaries": summaries,
        "runtime_snapshots": {
            mode: controllers[mode].snapshot() for mode in requested_modes
        },
    }


def run_feedback_reopening_challenge(
    seed: int,
    *,
    identity_seeds: Sequence[int],
    config: WholeLoopClosureConfig | None = None,
) -> dict[str, Any]:
    """Test whether an observed surprise changes the next information request.

    The intact and feedback-cut controllers receive the same grounded identity,
    candidates, pre-outcome evidence, committed action, and surprising realized
    return.  Only the post-outcome memory write differs.  A second, otherwise
    identical decision then tests whether that write reopens evidence gathering.
    """

    seed = int(seed)
    identity_seeds = tuple(int(value) for value in identity_seeds)
    if seed not in identity_seeds or len(set(identity_seeds)) < 2:
        raise ValueError("feedback challenge requires target plus another identity")
    frozen_config = config or WholeLoopClosureConfig(
        future_weight=V032_FUTURE_WEIGHT,
        coarse_samples=V043_COARSE_PAIRS,
        refined_samples=V043_REFINED_PAIRS,
        refinement_margin=V043_REFINEMENT_MARGIN,
        calibration_alarm_threshold=V043_CALIBRATION_ALARM_THRESHOLD,
        calibration_update_rate=V043_CALIBRATION_UPDATE_RATE,
    )
    controllers = {
        mode: _new_controller(identity_seeds, frozen_config)
        for mode in ("intact", "feedback_cut")
    }
    baseline = _learned_baseline(seed)
    target_pair = _identity_pair(seed)
    rank = int(baseline.discovery.rank)
    candidates = (
        WholeLoopActionCandidate("stable_route", 0.0, 0.0, 0.20),
        WholeLoopActionCandidate("snapshot_decoy", 0.0, 0.0, 0.95),
    )
    effect_operators = np.asarray(
        [
            np.asarray(baseline.sensory_map, dtype=np.float64),
            np.asarray(_hidden_interface(seed).sensory_takeover_effect, dtype=np.float64),
        ],
        dtype=np.float64,
    )

    first: dict[str, Any] = {}
    for mode, controller in controllers.items():
        signature = (target_pair, rank, 90_001)
        coarse = make_causal_preview_receipt(
            time=900_000,
            target_signature=signature,
            candidate_keys=[candidate.key for candidate in candidates],
            effect_operators=effect_operators,
            sample_count=V043_COARSE_PAIRS,
            refinement_level="coarse",
        )
        state = controller.begin_decision(
            time=900_000,
            target_signature=signature,
            candidates=candidates,
            coarse_preview=coarse,
            intervention_mode=mode,
        )
        if state.refinement_requested:
            raise RuntimeError("feedback challenge first decision must be confident")
        plan = controller.commit_decision(state)
        surprising_value = float(
            plan.predicted_selected_return + V043_FEEDBACK_SURPRISE
        )
        outcome = controller.observe_outcome(
            state,
            plan,
            surprising_value,
            reveal_time=900_001,
        )
        first[mode] = {
            "state": state,
            "plan": plan,
            "outcome": outcome,
        }

    second: dict[str, Any] = {}
    for mode, controller in controllers.items():
        signature = (target_pair, rank, 90_002)
        coarse = make_causal_preview_receipt(
            time=900_002,
            target_signature=signature,
            candidate_keys=[candidate.key for candidate in candidates],
            effect_operators=effect_operators,
            sample_count=V043_COARSE_PAIRS,
            refinement_level="coarse",
        )
        state = controller.begin_decision(
            time=900_002,
            target_signature=signature,
            candidates=candidates,
            coarse_preview=coarse,
            intervention_mode=mode,
        )
        refined = None
        if state.refinement_requested:
            refined = make_causal_preview_receipt(
                time=900_002,
                target_signature=signature,
                candidate_keys=[candidate.key for candidate in candidates],
                effect_operators=effect_operators,
                sample_count=V043_REFINED_PAIRS,
                refinement_level="refined",
            )
        plan = controller.commit_decision(state, refined_preview=refined)
        outcome = controller.observe_outcome(
            state,
            plan,
            plan.predicted_selected_return,
            reveal_time=900_003,
        )
        second[mode] = {
            "state": state,
            "plan": plan,
            "outcome": outcome,
        }

    intact_first = first["intact"]
    cut_first = first["feedback_cut"]
    intact_second = second["intact"]
    cut_second = second["feedback_cut"]
    checks = {
        "matched_first_action": (
            intact_first["plan"].selected_key
            == cut_first["plan"].selected_key
        ),
        "matched_surprise": bool(
            np.isclose(
                intact_first["outcome"].realized_external_return,
                cut_first["outcome"].realized_external_return,
                rtol=0.0,
                atol=1e-12,
            )
        ),
        "intact_feedback_write_applied": bool(
            intact_first["outcome"].outcome_update_applied
        ),
        "feedback_cut_write_absent": bool(
            not cut_first["outcome"].outcome_update_applied
        ),
        "intact_remembers_prediction_error": bool(
            intact_second["state"].remembered_prediction_error
            > frozen_config.calibration_alarm_threshold
        ),
        "feedback_cut_has_no_remembered_error": bool(
            cut_second["state"].remembered_prediction_error == 0.0
        ),
        "intact_reopens_evidence": bool(
            intact_second["state"].refinement_requested
        ),
        "feedback_cut_does_not_reopen": bool(
            not cut_second["state"].refinement_requested
        ),
        "all_receipt_chains_valid": all(
            validate_whole_loop_receipt_chain(
                item["state"], item["plan"], item["outcome"]
            )
            for group in (first, second)
            for item in group.values()
        ),
    }
    return {
        "seed": seed,
        "surprise_magnitude": V043_FEEDBACK_SURPRISE,
        "first_decision": {
            mode: {
                "selected_key": item["plan"].selected_key,
                "predicted_return": item["plan"].predicted_selected_return,
                "realized_return": item["outcome"].realized_external_return,
                "outcome_update_applied": item[
                    "outcome"
                ].outcome_update_applied,
                "memory_before_digest": item[
                    "outcome"
                ].memory_before_digest,
                "memory_after_digest": item[
                    "outcome"
                ].memory_after_digest,
            }
            for mode, item in first.items()
        },
        "second_decision": {
            mode: {
                "remembered_prediction_error": item[
                    "state"
                ].remembered_prediction_error,
                "epistemic_uncertainty": item[
                    "state"
                ].epistemic_uncertainty,
                "refinement_requested": item[
                    "state"
                ].refinement_requested,
                "samples_per_candidate": item[
                    "plan"
                ].total_samples_per_candidate,
            }
            for mode, item in second.items()
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def _paired_mode_differences(
    rows: Sequence[Mapping[str, Any]],
    reference: str = "intact",
) -> dict[str, Any]:
    key_fields = ("seed", "scenario", "trial")
    indexed = {
        tuple(row[field] for field in key_fields) + (row["mode"],): row
        for row in rows
    }
    result: dict[str, Any] = {}
    targets = sorted({str(row["mode"]) for row in rows if row["mode"] != reference})
    base_keys = sorted(
        {
            tuple(row[field] for field in key_fields)
            for row in rows
            if row["mode"] == reference
        }
    )
    for target in targets:
        differences = []
        for key in base_keys:
            reference_row = indexed[key + (reference,)]
            target_row = indexed[key + (target,)]
            differences.append(
                {
                    "accuracy": float(reference_row["correct"])
                    - float(target_row["correct"]),
                    "regret": float(target_row["regret"])
                    - float(reference_row["regret"]),
                    "samples": float(reference_row["samples_per_candidate"])
                    - float(target_row["samples_per_candidate"]),
                    "realized_value": float(reference_row["selected_actual_value"])
                    - float(target_row["selected_actual_value"]),
                }
            )
        result[target] = {
            metric: float(np.mean([row[metric] for row in differences]))
            for metric in ("accuracy", "regret", "samples", "realized_value")
        }
    return result


def _cohort_endpoints(
    mode_summaries: Mapping[str, Mapping[str, Any]],
    feedback: Sequence[Mapping[str, Any]],
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, bool]:
    intact = mode_summaries["intact"]

    def accuracy(mode: str) -> float:
        return float(mode_summaries[mode]["accuracy"])

    def regret(mode: str) -> float:
        return float(mode_summaries[mode]["mean_regret"])

    endpoints = {
        "all_receipt_chains_valid": all(
            bool(row["receipt_chain_valid"]) for row in rows
        ),
        "no_evaluator_labels_enter_receipts": not any(
            bool(row["uses_evaluator_labels"]) for row in rows
        ),
        "future_outcomes_unknown_at_commit": all(
            bool(row["future_outcome_unknown_at_commit"]) for row in rows
        ),
        "intact_accuracy_at_least_0_98": float(intact["accuracy"]) >= 0.98,
        "intact_mean_regret_at_most_0_01": float(intact["mean_regret"]) <= 0.01,
        "intact_accepts_superior_replacement": float(
            intact["superior_replacement_acceptance"]
        )
        >= 0.98,
        "memory_cut_recovers_accuracy": accuracy("memory_cut") >= 0.98,
        "memory_cut_uses_more_evidence": float(
            mode_summaries["memory_cut"]["mean_samples_per_candidate"]
        )
        > float(intact["mean_samples_per_candidate"]),
        "metacognition_cut_loses_accuracy": (
            accuracy("intact") - accuracy("metacognition_cut") >= 0.15
        ),
        "boundary_cut_loses_accuracy": (
            accuracy("intact") - accuracy("boundary_cut") >= 0.35
        ),
        "provenance_cut_loses_accuracy": (
            accuracy("intact") - accuracy("provenance_cut") >= 0.25
        ),
        "planner_binding_cut_loses_accuracy": (
            accuracy("intact") - accuracy("planner_binding_cut") >= 0.35
        ),
        "joint_cut_loses_accuracy": (
            accuracy("intact") - accuracy("joint_cut") >= 0.35
        ),
        "intact_regret_below_metacognition_cut": regret("intact")
        < regret("metacognition_cut"),
        "intact_regret_below_boundary_cut": regret("intact")
        < regret("boundary_cut"),
        "intact_regret_below_provenance_cut": regret("intact")
        < regret("provenance_cut"),
        "intact_regret_below_planner_binding_cut": regret("intact")
        < regret("planner_binding_cut"),
        "all_feedback_challenges_pass": all(
            bool(item["all_checks_pass"]) for item in feedback
        ),
        # Replaced with the actual runtime-snapshot adjudication in the
        # cohort aggregator after all controllers finish.
        "runtime_has_no_survival_or_identity_reward": True,
    }
    return endpoints


def run_whole_loop_closure_cohort(
    seeds: Sequence[int],
    *,
    cohort: str,
    modes: Sequence[WholeLoopInterventionMode] = V043_MODES,
    trials_per_scenario: int = V043_TRIALS_PER_SCENARIO,
    config: WholeLoopClosureConfig | None = None,
) -> dict[str, Any]:
    """Run and aggregate one explicitly named matched cohort."""

    parsed_seeds = tuple(int(seed) for seed in seeds)
    if len(parsed_seeds) < 2 or len(set(parsed_seeds)) != len(parsed_seeds):
        raise ValueError("cohort requires at least two unique seeds")
    if cohort not in {"exposed_tuning", "frozen_holdout", "test"}:
        raise ValueError("unknown v0.43 cohort name")
    if cohort == "exposed_tuning" and parsed_seeds != V043_EXPOSED_TUNING_SEEDS:
        raise ValueError("exposed tuning cohort must use the declared seeds")
    preoutcome_freeze_sha256: str | None = None
    if cohort == "frozen_holdout":
        if not V043_HOLDOUT_SEEDS:
            raise RuntimeError("v0.43 holdout seeds have not been frozen")
        if parsed_seeds != V043_HOLDOUT_SEEDS:
            raise ValueError("holdout cohort must use the frozen seed tuple")
        preoutcome_freeze_sha256 = _verify_holdout_freeze()

    seed_results = [
        run_whole_loop_closure_seed(
            seed,
            identity_seeds=parsed_seeds,
            modes=modes,
            trials_per_scenario=trials_per_scenario,
            config=config,
        )
        for seed in parsed_seeds
    ]
    rows = [row for result in seed_results for row in result["rows"]]
    requested_modes = tuple(str(mode) for mode in modes)
    mode_summaries = {
        mode: _mode_summary([row for row in rows if row["mode"] == mode])
        for mode in requested_modes
    }
    feedback = [
        run_feedback_reopening_challenge(
            seed,
            identity_seeds=parsed_seeds,
            config=config,
        )
        for seed in parsed_seeds
    ]
    snapshots = [
        snapshot
        for result in seed_results
        for snapshot in result["runtime_snapshots"].values()
    ]
    endpoints = _cohort_endpoints(mode_summaries, feedback, rows)
    endpoints["runtime_has_no_survival_or_identity_reward"] = all(
        float(snapshot["explicit_survival_reward"]) == 0.0
        and float(snapshot["explicit_identity_reward"]) == 0.0
        for snapshot in snapshots
    )
    runtime_audit = {
        "snapshot_count": len(snapshots),
        "snapshot_digests": [str(snapshot["digest"]) for snapshot in snapshots],
        "explicit_survival_reward_values": sorted(
            {float(snapshot["explicit_survival_reward"]) for snapshot in snapshots}
        ),
        "explicit_identity_reward_values": sorted(
            {float(snapshot["explicit_identity_reward"]) for snapshot in snapshots}
        ),
        "uses_evaluator_labels": any(
            bool(snapshot["uses_evaluator_labels"]) for snapshot in snapshots
        ),
    }
    return {
        "schema": "rrct.v043.whole_loop_causal_closure_analysis.v1",
        "scientific_status": (
            "fresh_frozen_holdout_functional_development"
            if cohort == "frozen_holdout"
            else "exposed_tuning_or_test_only"
        ),
        "cohort": cohort,
        "preoutcome_freeze_sha256": preoutcome_freeze_sha256,
        "seeds": list(parsed_seeds),
        "modes": list(requested_modes),
        "scenarios": list(V043_SCENARIOS),
        "trials_per_scenario": int(trials_per_scenario),
        "config": seed_results[0]["config"],
        "decision_rows": rows,
        "seed_summaries": [
            {
                "seed": result["seed"],
                "mode_summaries": result["mode_summaries"],
            }
            for result in seed_results
        ],
        "mode_summaries": mode_summaries,
        "paired_intact_differences": _paired_mode_differences(rows),
        "feedback_reopening_challenges": feedback,
        "runtime_reward_and_label_audit": runtime_audit,
        "frozen_endpoints": endpoints,
        "all_frozen_endpoints_met": all(endpoints.values()),
        "claim_boundary": (
            "This synthetic matched intervention study tests whether one "
            "persistent identity-bound causal self-model jointly changes "
            "attribution, evidence acquisition, planning, action authorization, "
            "and post-outcome calibration. It does not test phenomenal "
            "consciousness, sentience, valence, moral status, or an intrinsic "
            "desire to persist."
        ),
    }


def _compact_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in row.items()
        if key
        not in {
            # Candidate-level values are retained in the JSON analysis but
            # omitted from the CSV to keep it compact and rectangular.
            "candidate_keys",
            "candidate_actual_values",
            "predicted_external_returns",
            "target_signature",
        }
    }


def write_whole_loop_closure_results(
    result: Mapping[str, Any],
    output_dir: str | Path,
) -> dict[str, str]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    analysis_path = destination / "whole_loop_closure_analysis.json"
    rows_path = destination / "whole_loop_decisions.csv"
    summary_path = destination / "WHOLE_LOOP_CLOSURE_REPORT.md"

    analysis_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rows = [
        _compact_row(row) for row in result.get("decision_rows", [])
    ]
    if rows:
        with rows_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    else:
        rows_path.write_text("", encoding="utf-8")

    mode_summaries = result["mode_summaries"]
    lines = [
        "# RRCT v0.43 Whole-Loop Causal Closure Report",
        "",
        f"**Cohort:** `{result['cohort']}`",
        "",
        f"**Seeds:** {', '.join(str(seed) for seed in result['seeds'])}",
        "",
        f"**Frozen endpoints met:** `{result['all_frozen_endpoints_met']}`",
        "",
        "## Matched intervention results",
        "",
        "| Mode | Accuracy | Mean regret | Mean samples / candidate | Refinement rate | Authorized by self-model |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for mode in result["modes"]:
        summary = mode_summaries[mode]
        lines.append(
            "| {mode} | {accuracy:.6f} | {regret:.6f} | {samples:.3f} | "
            "{refine:.6f} | {authorized:.6f} |".format(
                mode=mode,
                accuracy=float(summary["accuracy"]),
                regret=float(summary["mean_regret"]),
                samples=float(summary["mean_samples_per_candidate"]),
                refine=float(summary["refinement_rate"]),
                authorized=float(summary["self_model_authorized_rate"]),
            )
        )
    lines.extend(
        [
            "",
            "## Frozen endpoint adjudication",
            "",
        ]
    )
    for name, passed in result["frozen_endpoints"].items():
        lines.append(f"- `{name}`: **{'PASS' if passed else 'FAIL'}**")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The intact controller binds one temporally grounded identity "
                "episode, one learned causal boundary, an uncertainty-guided "
                "evidence decision, an external-task plan, the authorized "
                "action, and the resulting calibration update into one "
                "cross-validated receipt chain. The surgical cuts test whether "
                "those links are functionally consequential rather than merely "
                "inspectable metadata."
            ),
            "",
            "## Claim boundary",
            "",
            str(result["claim_boundary"]),
            "",
        ]
    )
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "analysis": str(analysis_path),
        "rows": str(rows_path),
        "report": str(summary_path),
    }


def _parse_seed_list(value: str) -> tuple[int, ...]:
    parts = [part.strip() for part in value.split(",") if part.strip()]
    if not parts:
        raise argparse.ArgumentTypeError("seed list cannot be empty")
    try:
        return tuple(int(part) for part in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("seeds must be integers") from exc


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the RRCT v0.43 whole-loop causal-closure experiment"
    )
    parser.add_argument(
        "--cohort",
        choices=("exposed_tuning", "frozen_holdout", "test"),
        default="exposed_tuning",
    )
    parser.add_argument(
        "--seeds",
        type=_parse_seed_list,
        default=V043_EXPOSED_TUNING_SEEDS,
        help="comma-separated integer seeds",
    )
    parser.add_argument(
        "--trials-per-scenario",
        type=int,
        default=V043_TRIALS_PER_SCENARIO,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("validation/v0.43.0_whole_loop_causal_closure/results"),
    )
    args = parser.parse_args(argv)
    result = run_whole_loop_closure_cohort(
        args.seeds,
        cohort=args.cohort,
        trials_per_scenario=args.trials_per_scenario,
    )
    paths = write_whole_loop_closure_results(result, args.output)
    print(json.dumps({"status": result["all_frozen_endpoints_met"], **paths}, indent=2))
    return 0 if result["all_frozen_endpoints_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "V043_CALIBRATION_ALARM_THRESHOLD",
    "V043_CALIBRATION_UPDATE_RATE",
    "V043_COARSE_PAIRS",
    "V043_EXPOSED_TUNING_SEEDS",
    "V043_FEEDBACK_SURPRISE",
    "V043_HOLDOUT_SEEDS",
    "V043_MODES",
    "V043_REFINED_PAIRS",
    "V043_REFINEMENT_MARGIN",
    "V043_SCENARIOS",
    "V043_TRIALS_PER_SCENARIO",
    "run_feedback_reopening_challenge",
    "run_whole_loop_closure_cohort",
    "run_whole_loop_closure_seed",
    "write_whole_loop_closure_results",
]
