"""RRCT v0.31 cross-fitted conditional causal-rank experiment.

The experiment isolates the higher-mode inference gap exposed by v0.30.  It
uses one proposal fold to select an anonymous handle/source pair and estimate
the lower-rank response, followed by two disjoint confirmation folds whose
handle reassignments preserve that response.  The mechanism is a bounded
functional causal-model component, not a consciousness or awareness test.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

from .causal_boundary import CausalBoundaryConfig, OnlineCausalSelfBoundary


FloatArray = NDArray[np.float64]
V031_SCHEMA = "rrct.v031.conditional_rank_inference.v2"
V031_PILOT_SEEDS = (5901, 5907, 5913, 5919)
V031_OFFICIAL_SEEDS = (6001, 6007, 6013, 6019, 6029, 6037, 6043, 6053)
V031_OBSERVATION_DIM = 12
V031_PROCESS_DIM = 8
V031_SOURCE_COUNT = 6
V031_HANDLE_COUNT = 4
V031_SCENARIOS = (
    ("no_route", (), 0),
    ("rank_one_baseline", (5.0,), 1),
    ("rank_one_strong", (9.0,), 1),
    ("rank_two_baseline", (5.0, 3.2), 2),
    ("rank_two_weak", (5.0, 2.4), 2),
    ("rank_three", (5.0, 3.2, 2.4), 3),
    ("rank_two_integration", (5.0, 3.2), 2),
)
V031_SCENARIO_WINDOWS = {
    name: (2 if name == "rank_two_integration" else 1)
    for name, _, _ in V031_SCENARIOS
}


def _positive_integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise ValueError(f"{name} must be an integer")
    parsed = int(value)
    if parsed <= 0:
        raise ValueError(f"{name} must be positive")
    return parsed


def _positive_float(value: Any, name: str) -> float:
    if isinstance(value, bool) or not np.isscalar(value):
        raise ValueError(f"{name} must be a finite scalar")
    parsed = float(value)
    if not np.isfinite(parsed) or parsed <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return parsed


@dataclass(frozen=True)
class V031RunConfig:
    block_size: int = 20
    learner_seed: int = 331031
    evidence_capacity: int = 480
    minimum_samples: int = 480
    fit_interval: int = 480
    null_permutations: int = 128
    half_null_permutations: int = 128
    null_quantile: float = 0.99
    ridge: float = 0.50
    scenario_steps: int = 480
    exogenous_strength: float = 5.0
    observation_persistence: float = 0.42
    observation_noise: float = 0.035

    def __post_init__(self) -> None:
        for name in (
            "block_size",
            "learner_seed",
            "evidence_capacity",
            "minimum_samples",
            "fit_interval",
            "null_permutations",
            "half_null_permutations",
            "scenario_steps",
        ):
            value = getattr(self, name)
            if name == "learner_seed":
                if isinstance(value, bool) or not isinstance(
                    value, (int, np.integer)
                ) or int(value) < 0:
                    raise ValueError("learner_seed must be a nonnegative integer")
                object.__setattr__(self, name, int(value))
            else:
                object.__setattr__(self, name, _positive_integer(value, name))
        for name in ("ridge", "exogenous_strength", "observation_noise"):
            object.__setattr__(self, name, _positive_float(getattr(self, name), name))
        persistence = float(self.observation_persistence)
        if not np.isfinite(persistence) or not 0.0 <= persistence < 1.0:
            raise ValueError("observation_persistence must lie in [0, 1)")
        object.__setattr__(self, "observation_persistence", persistence)
        quantile = float(self.null_quantile)
        if not np.isfinite(quantile) or not 0.5 < quantile < 1.0:
            raise ValueError("null_quantile must lie in (0.5, 1)")
        object.__setattr__(self, "null_quantile", quantile)
        if self.evidence_capacity != self.minimum_samples:
            raise ValueError("v0.31 requires one complete fixed assay window")
        if self.scenario_steps != self.minimum_samples:
            raise ValueError("each v0.31 scenario must contain exactly one fit window")
        if self.evidence_capacity % (4 * self.block_size):
            raise ValueError("the v0.31 window must contain a multiple of four blocks")

    def boundary_config(self, *, method: str) -> CausalBoundaryConfig:
        return CausalBoundaryConfig(
            observation_dim=V031_OBSERVATION_DIM,
            process_dim=V031_PROCESS_DIM,
            source_count=V031_SOURCE_COUNT,
            handle_count=V031_HANDLE_COUNT,
            evidence_capacity=self.evidence_capacity,
            minimum_samples=self.minimum_samples,
            fit_interval=self.fit_interval,
            structural_confirmation_interval=self.fit_interval,
            commitment_block_size=self.block_size,
            ridge=self.ridge,
            null_permutations=self.null_permutations,
            half_null_permutations=self.half_null_permutations,
            null_quantile=self.null_quantile,
            higher_mode_null=method,
            revision_confirmations=2,
            revocation_confirmations=2,
            confidence_decay=0.65,
            seed=self.learner_seed,
        )


V031_FROZEN_CANDIDATE_CONFIG = V031RunConfig()


@dataclass(frozen=True)
class _HiddenStructure:
    pair: tuple[int, int]
    exogenous_source: int
    internal: FloatArray
    sensory: FloatArray
    exogenous_effect: FloatArray
    digest: str


def _orthogonal(rng: np.random.Generator, rows: int) -> FloatArray:
    value, _ = np.linalg.qr(rng.normal(size=(rows, rows)))
    return np.asarray(value, dtype=np.float64)


def _array_digest(value: FloatArray) -> str:
    return hashlib.sha256(
        np.ascontiguousarray(value, dtype=np.float64).tobytes(order="C")
    ).hexdigest()


def _hidden_structure(seed: int, config: V031RunConfig) -> _HiddenStructure:
    rng = np.random.default_rng(np.random.SeedSequence([int(seed), 0x3100]))
    handle = int(rng.integers(V031_HANDLE_COUNT))
    source = int(rng.integers(V031_SOURCE_COUNT))
    exogenous_source = (
        source + 1 + int(rng.integers(V031_SOURCE_COUNT - 1))
    ) % V031_SOURCE_COUNT
    internal = _orthogonal(rng, V031_PROCESS_DIM)
    sensory = _orthogonal(rng, V031_OBSERVATION_DIM)
    exogenous = (
        config.exogenous_strength
        * internal[:, 4:6]
        @ sensory[:, 4:6].T
    )
    payload = {
        "seed": int(seed),
        "pair": [handle, source],
        "exogenous_source": exogenous_source,
        "internal": _array_digest(internal),
        "sensory": _array_digest(sensory),
        "exogenous": _array_digest(exogenous),
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return _HiddenStructure(
        pair=(handle, source),
        exogenous_source=exogenous_source,
        internal=internal,
        sensory=sensory,
        exogenous_effect=np.asarray(exogenous, dtype=np.float64),
        digest=digest,
    )


def _effect(
    structure: _HiddenStructure, strengths: Sequence[float]
) -> FloatArray:
    values = np.asarray(tuple(strengths), dtype=np.float64)
    if len(values) == 0:
        return np.zeros((V031_PROCESS_DIM, V031_OBSERVATION_DIM))
    return np.asarray(
        structure.internal[:, : len(values)]
        @ np.diag(values)
        @ structure.sensory[:, : len(values)].T,
        dtype=np.float64,
    )


def _equal_energy_bank(rng: np.random.Generator) -> FloatArray:
    bank = rng.normal(size=(V031_SOURCE_COUNT, V031_PROCESS_DIM))
    norms = np.linalg.norm(bank, axis=1, keepdims=True)
    if np.any(norms <= 1e-12):
        raise RuntimeError("degenerate anonymous source draw")
    return np.asarray(bank / norms, dtype=np.float64)


def _fit_pair(receipt: Any) -> tuple[int, int] | None:
    if receipt.fit_handle_index is None:
        return None
    return int(receipt.fit_handle_index), int(receipt.fit_source_index)


def _run_episode(
    seed: int,
    scenario_index: int,
    scenario: tuple[str, tuple[float, ...], int],
    structure: _HiddenStructure,
    config: V031RunConfig,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    name, strengths, target_rank = scenario
    scenario_steps = config.scenario_steps * V031_SCENARIO_WINDOWS[name]
    conditional = OnlineCausalSelfBoundary(
        config.boundary_config(
            method="cross_fitted_reduced_rank_randomization_bootstrap"
        )
    )
    global_comparator = OnlineCausalSelfBoundary(
        config.boundary_config(method="global_sharp_null")
    )
    rng = np.random.default_rng(
        np.random.SeedSequence([int(seed), 0x3102, int(scenario_index)])
    )
    routed_effect = _effect(structure, strengths)
    observation = np.zeros(V031_OBSERVATION_DIM, dtype=np.float64)
    rows: list[dict[str, Any]] = []
    final_conditional = None
    final_global = None
    for time in range(scenario_steps):
        conditional_before = conditional.state
        global_before = global_comparator.state
        conditional_commitment = conditional.commit_handles(time=time)
        global_commitment = global_comparator.commit_handles(time=time)
        commitments_equal = bool(
            np.array_equal(
                conditional_commitment.handles,
                global_commitment.handles,
            )
        )
        if not commitments_equal:
            raise RuntimeError("conditional and comparator commitments diverged")
        bank = _equal_energy_bank(rng)
        conditional_bound = conditional.bind_sources(
            observation,
            bank,
            commitment_digest=conditional_commitment.digest,
            time=time,
        )
        global_bound = global_comparator.bind_sources(
            observation,
            bank,
            commitment_digest=global_commitment.digest,
            time=time,
        )
        handle, source = structure.pair
        routed = (
            conditional_commitment.handles[handle]
            * bank[source]
            @ routed_effect
        )
        next_observation = (
            config.observation_persistence * observation
            + routed
            + bank[structure.exogenous_source] @ structure.exogenous_effect
            + rng.normal(
                0.0,
                config.observation_noise,
                size=V031_OBSERVATION_DIM,
            )
        )
        conditional_receipt = conditional.reveal_outcome(
            next_observation,
            transition_digest=conditional_bound.transition_digest,
            time=time + 1,
        )
        global_receipt = global_comparator.reveal_outcome(
            next_observation,
            transition_digest=global_bound.transition_digest,
            time=time + 1,
        )
        final_conditional = conditional_receipt
        final_global = global_receipt
        rows.append(
            {
                "schema": V031_SCHEMA,
                "seed": int(seed),
                "scenario": name,
                "scenario_step": int(time),
                "target_handle": int(structure.pair[0]),
                "target_source": int(structure.pair[1]),
                "target_rank": int(target_rank),
                "structure_digest": structure.digest,
                "conditional_fit_performed": conditional_receipt.fit_performed,
                "conditional_fit_handle": conditional_receipt.fit_handle_index,
                "conditional_fit_source": conditional_receipt.fit_source_index,
                "conditional_fit_rank": conditional_receipt.fit_rank,
                "conditional_fit_confidence": conditional_receipt.fit_confidence,
                "conditional_selected_handle": (
                    conditional_receipt.selected_handle_index
                ),
                "conditional_selected_source": (
                    conditional_receipt.selected_source_index
                ),
                "conditional_selected_rank": conditional_receipt.rank,
                "conditional_selected_confidence": (
                    conditional_receipt.confidence
                ),
                "conditional_acquired": conditional_receipt.acquired,
                "conditional_revised": conditional_receipt.revised,
                "conditional_structural_event": (
                    conditional_receipt.structural_event
                ),
                "conditional_candidate_handle": (
                    conditional_receipt.candidate_handle_index
                ),
                "conditional_candidate_source": (
                    conditional_receipt.candidate_source_index
                ),
                "conditional_candidate_rank": conditional_receipt.candidate_rank,
                "conditional_candidate_streak": (
                    conditional_receipt.candidate_streak
                ),
                "conditional_candidate_last_evidence_count": (
                    conditional_receipt.candidate_last_evidence_count
                ),
                "conditional_candidate_renewed": (
                    conditional_receipt.candidate_renewed
                ),
                "global_fit_performed": global_receipt.fit_performed,
                "global_fit_handle": global_receipt.fit_handle_index,
                "global_fit_source": global_receipt.fit_source_index,
                "global_fit_rank": global_receipt.fit_rank,
                "global_fit_confidence": global_receipt.fit_confidence,
                "global_selected_handle": global_receipt.selected_handle_index,
                "global_selected_source": global_receipt.selected_source_index,
                "global_selected_rank": global_receipt.rank,
                "global_selected_confidence": global_receipt.confidence,
                "global_acquired": global_receipt.acquired,
                "global_revised": global_receipt.revised,
                "global_structural_event": global_receipt.structural_event,
                "global_candidate_handle": (
                    global_receipt.candidate_handle_index
                ),
                "global_candidate_source": (
                    global_receipt.candidate_source_index
                ),
                "global_candidate_rank": global_receipt.candidate_rank,
                "global_candidate_streak": global_receipt.candidate_streak,
                "global_candidate_last_evidence_count": (
                    global_receipt.candidate_last_evidence_count
                ),
                "global_candidate_renewed": global_receipt.candidate_renewed,
                "commitments_equal": commitments_equal,
                "conditional_pre_state_digest": (
                    conditional_receipt.model_digest_before
                ),
                "conditional_post_state_digest": (
                    conditional_receipt.model_digest_after
                ),
                "conditional_commitment_digest": (
                    conditional_receipt.commitment_digest
                ),
                "conditional_transition_digest": (
                    conditional_receipt.transition_digest
                ),
                "conditional_outcome_digest": conditional_receipt.outcome_digest,
                "global_pre_state_digest": global_receipt.model_digest_before,
                "global_post_state_digest": global_receipt.model_digest_after,
                "global_commitment_digest": global_receipt.commitment_digest,
                "global_transition_digest": global_receipt.transition_digest,
                "global_outcome_digest": global_receipt.outcome_digest,
                "conditional_prequential_chain": bool(
                    conditional_receipt.model_digest_before
                    == conditional_before.model_digest
                    and conditional_receipt.model_digest_after
                    == conditional.state.model_digest
                    and conditional_receipt.commitment_digest
                    == conditional_commitment.digest
                    and conditional_receipt.transition_digest
                    == conditional_bound.transition_digest
                ),
                "global_prequential_chain": bool(
                    global_receipt.model_digest_before
                    == global_before.model_digest
                    and global_receipt.model_digest_after
                    == global_comparator.state.model_digest
                    and global_receipt.commitment_digest
                    == global_commitment.digest
                    and global_receipt.transition_digest
                    == global_bound.transition_digest
                ),
                "source_energy_error": float(
                    np.max(np.abs(np.linalg.norm(bank, axis=1) - 1.0))
                ),
                "hidden_truth_passed_to_model": False,
            }
        )
        observation = np.asarray(next_observation, dtype=np.float64)
    if final_conditional is None or final_global is None:
        raise RuntimeError("empty v0.31 scenario")
    expected_pair = structure.pair if target_rank else None
    conditional_pair = _fit_pair(final_conditional)
    global_pair = _fit_pair(final_global)
    conditional_exact = bool(
        conditional_pair == expected_pair
        and final_conditional.fit_rank == target_rank
    )
    global_exact = bool(
        global_pair == expected_pair and final_global.fit_rank == target_rank
    )
    state_admission_expected = bool(
        target_rank > 0 and V031_SCENARIO_WINDOWS[name] >= 2
    )
    expected_state_pair = expected_pair if state_admission_expected else None
    expected_state_rank = target_rank if state_admission_expected else 0
    conditional_selected_pair = (
        None
        if final_conditional.selected_handle_index is None
        else (
            int(final_conditional.selected_handle_index),
            int(final_conditional.selected_source_index),
        )
    )
    global_selected_pair = (
        None
        if final_global.selected_handle_index is None
        else (
            int(final_global.selected_handle_index),
            int(final_global.selected_source_index),
        )
    )

    def state_sequence(prefix: str) -> tuple[list[int], bool, int, bool]:
        fit_rows = [row for row in rows if row[f"{prefix}_fit_performed"]]
        fit_steps = [int(row["scenario_step"]) for row in fit_rows]
        expected_fit_steps = [
            config.scenario_steps * (window + 1) - 1
            for window in range(V031_SCENARIO_WINDOWS[name])
        ]
        all_fits_exact = bool(
            fit_steps == expected_fit_steps
            and all(
                (
                    None
                    if row[f"{prefix}_fit_handle"] is None
                    else (
                        int(row[f"{prefix}_fit_handle"]),
                        int(row[f"{prefix}_fit_source"]),
                    )
                )
                == expected_pair
                and int(row[f"{prefix}_fit_rank"]) == target_rank
                for row in fit_rows
            )
        )
        acquisitions = int(sum(row[f"{prefix}_acquired"] for row in rows))
        if target_rank == 0:
            transition_exact = bool(
                all_fits_exact
                and acquisitions == 0
                and all(
                    row[f"{prefix}_structural_event"] == "null_fit"
                    and row[f"{prefix}_selected_handle"] is None
                    and row[f"{prefix}_selected_rank"] == 0
                    for row in fit_rows
                )
            )
        elif not state_admission_expected:
            transition_exact = bool(
                all_fits_exact
                and acquisitions == 0
                and len(fit_rows) == 1
                and fit_rows[0][f"{prefix}_structural_event"]
                == "acquisition_candidate"
                and fit_rows[0][f"{prefix}_selected_handle"] is None
                and fit_rows[0][f"{prefix}_selected_rank"] == 0
                and (
                    fit_rows[0][f"{prefix}_candidate_handle"],
                    fit_rows[0][f"{prefix}_candidate_source"],
                )
                == expected_pair
                and fit_rows[0][f"{prefix}_candidate_rank"] == target_rank
                and fit_rows[0][f"{prefix}_candidate_streak"] == 1
                and fit_rows[0][f"{prefix}_candidate_last_evidence_count"]
                == config.scenario_steps
                and fit_rows[0][f"{prefix}_candidate_renewed"] is True
            )
        else:
            first, second = fit_rows if len(fit_rows) == 2 else ({}, {})
            transition_exact = bool(
                all_fits_exact
                and acquisitions == 1
                and first.get(f"{prefix}_structural_event")
                == "acquisition_candidate"
                and first.get(f"{prefix}_acquired") is False
                and first.get(f"{prefix}_selected_handle") is None
                and first.get(f"{prefix}_selected_rank") == 0
                and (
                    first.get(f"{prefix}_candidate_handle"),
                    first.get(f"{prefix}_candidate_source"),
                )
                == expected_pair
                and first.get(f"{prefix}_candidate_rank") == target_rank
                and first.get(f"{prefix}_candidate_streak") == 1
                and first.get(f"{prefix}_candidate_last_evidence_count")
                == config.scenario_steps
                and first.get(f"{prefix}_candidate_renewed") is True
                and second.get(f"{prefix}_structural_event") == "acquisition"
                and second.get(f"{prefix}_acquired") is True
                and (
                    second.get(f"{prefix}_selected_handle"),
                    second.get(f"{prefix}_selected_source"),
                )
                == expected_pair
                and second.get(f"{prefix}_selected_rank") == target_rank
                and second.get(f"{prefix}_selected_confidence", 0.0) > 0.0
                and second.get(f"{prefix}_candidate_handle") is None
                and second.get(f"{prefix}_candidate_source") is None
                and second.get(f"{prefix}_candidate_rank") == 0
                and second.get(f"{prefix}_candidate_streak") == 0
                and second.get(f"{prefix}_candidate_last_evidence_count") is None
                and second.get(f"{prefix}_candidate_renewed") is True
            )
        return fit_steps, all_fits_exact, acquisitions, transition_exact

    (
        conditional_fit_steps,
        conditional_all_fits_exact,
        conditional_acquisition_count,
        conditional_state_transition_exact,
    ) = state_sequence("conditional")
    (
        global_fit_steps,
        global_all_fits_exact,
        global_acquisition_count,
        global_state_transition_exact,
    ) = state_sequence("global")
    summary = {
        "scenario": name,
        "scenario_steps": int(scenario_steps),
        "target_rank": int(target_rank),
        "conditional_pair_exact": bool(conditional_pair == expected_pair),
        "conditional_rank": int(final_conditional.fit_rank),
        "conditional_exact": conditional_exact,
        "conditional_overrank": bool(final_conditional.fit_rank > target_rank),
        "conditional_confidence": float(final_conditional.fit_confidence),
        "conditional_fit_steps": conditional_fit_steps,
        "conditional_all_fits_exact": conditional_all_fits_exact,
        "conditional_acquisition_count": conditional_acquisition_count,
        "conditional_state_transition_exact": (
            conditional_state_transition_exact
        ),
        "state_admission_expected": state_admission_expected,
        "conditional_selected_pair_exact": bool(
            conditional_selected_pair == expected_state_pair
        ),
        "conditional_selected_rank": int(final_conditional.rank),
        "conditional_state_exact": bool(
            conditional_selected_pair == expected_state_pair
            and final_conditional.rank == expected_state_rank
        ),
        "conditional_acquired": bool(final_conditional.acquired),
        "conditional_state_confidence": float(final_conditional.confidence),
        "global_pair_exact": bool(global_pair == expected_pair),
        "global_rank": int(final_global.fit_rank),
        "global_exact": global_exact,
        "global_overrank": bool(final_global.fit_rank > target_rank),
        "global_confidence": float(final_global.fit_confidence),
        "global_fit_steps": global_fit_steps,
        "global_all_fits_exact": global_all_fits_exact,
        "global_acquisition_count": global_acquisition_count,
        "global_state_transition_exact": global_state_transition_exact,
        "global_selected_pair_exact": bool(
            global_selected_pair == expected_state_pair
        ),
        "global_selected_rank": int(final_global.rank),
        "global_state_exact": bool(
            global_selected_pair == expected_state_pair
            and final_global.rank == expected_state_rank
        ),
        "global_acquired": bool(final_global.acquired),
        "global_state_confidence": float(final_global.confidence),
        "integrity": bool(
            all(row["commitments_equal"] for row in rows)
            and all(row["conditional_prequential_chain"] for row in rows)
            and all(row["global_prequential_chain"] for row in rows)
            and all(row["source_energy_error"] <= 1e-12 for row in rows)
            and not any(row["hidden_truth_passed_to_model"] for row in rows)
        ),
    }
    return rows, summary


def run_conditional_rank_seed(
    seed: int,
    *,
    cohort: str = "pilot",
    allow_reserved_official: bool = False,
    config: V031RunConfig = V031_FROZEN_CANDIDATE_CONFIG,
) -> dict[str, Any]:
    parsed_seed = int(seed)
    if cohort not in {"pilot", "official"}:
        raise ValueError("cohort must be pilot or official")
    reserved = V031_PILOT_SEEDS if cohort == "pilot" else V031_OFFICIAL_SEEDS
    if parsed_seed not in reserved:
        raise ValueError(f"seed is not reserved for the v0.31 {cohort} cohort")
    if cohort == "official" and not allow_reserved_official:
        raise PermissionError("official v0.31 seeds require the frozen harness")
    if cohort == "pilot" and allow_reserved_official:
        raise ValueError("official authority is invalid for a pilot run")
    structure = _hidden_structure(parsed_seed, config)
    rows: list[dict[str, Any]] = []
    episodes: dict[str, dict[str, Any]] = {}
    for scenario_index, scenario in enumerate(V031_SCENARIOS):
        episode_rows, episode_summary = _run_episode(
            parsed_seed,
            scenario_index,
            scenario,
            structure,
            config,
        )
        rows.extend(episode_rows)
        episodes[scenario[0]] = episode_summary
    admitted = [item for item in episodes.values() if item["target_rank"] > 0]
    summary = {
        "seed": parsed_seed,
        "episodes": episodes,
        "conditional_false_overranks": int(
            sum(
                item["conditional_overrank"]
                for item in episodes.values()
                if item["target_rank"] <= 1
            )
        ),
        "conditional_positive_support": bool(
            all(item["conditional_confidence"] > 0.0 for item in admitted)
        ),
        "integrity": bool(all(item["integrity"] for item in episodes.values())),
    }
    return {
        "schema": V031_SCHEMA,
        "seed": parsed_seed,
        "cohort": cohort,
        "config": asdict(config),
        "seed_summary": summary,
        "rows": rows,
        "receipt": {
            "seed": parsed_seed,
            "cohort": cohort,
            "structure_digest": structure.digest,
            "world_seed_never_passed_to_model": True,
            "learner_rng_independent_of_world_seed": True,
            "hidden_pair_never_passed_to_model": True,
            "hidden_rank_never_passed_to_model": True,
            "hidden_bases_never_passed_to_model": True,
            "scenario_labels_never_passed_to_model": True,
            "rank_test_method": (
                "cross_fitted_reduced_rank_randomization_bootstrap"
            ),
            "rank_test_exact": False,
            "rank_test_semantics": (
                "conditional one-step add-one composite-null bootstrap on two "
                "disjoint confirmation folds with observed history held fixed"
            ),
            "observed_history_held_fixed": True,
            "interventions_reversible_and_synthetic": True,
        },
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        raise ValueError("cannot write an empty CSV")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def aggregate_conditional_rank_results(
    parts: Sequence[Mapping[str, Any]], output: Path
) -> dict[str, Any]:
    if not parts:
        raise ValueError("parts cannot be empty")
    cohort = str(parts[0].get("cohort"))
    if cohort not in {"pilot", "official"}:
        raise ValueError("v0.31 cohort must be pilot or official")
    expected = V031_PILOT_SEEDS if cohort == "pilot" else V031_OFFICIAL_SEEDS
    seeds = tuple(int(part.get("seed")) for part in parts)
    if seeds != expected:
        raise ValueError("v0.31 aggregation requires the exact reserved cohort order")
    expected_config = asdict(V031_FROZEN_CANDIDATE_CONFIG)
    if any(part.get("schema") != V031_SCHEMA for part in parts):
        raise ValueError("v0.31 schema mismatch")
    if any(part.get("cohort") != cohort for part in parts):
        raise ValueError("mixed v0.31 cohorts")
    if any(part.get("config") != expected_config for part in parts):
        raise ValueError("v0.31 configuration mismatch")
    summaries = [dict(part["seed_summary"]) for part in parts]

    def episode(name: str) -> list[Mapping[str, Any]]:
        return [summary["episodes"][name] for summary in summaries]

    required_weak = 3 if cohort == "pilot" else 7
    required_rank_three = 3 if cohort == "pilot" else 7
    gates = {
        "no_route_returns_null_in_every_seed": all(
            item["conditional_exact"] for item in episode("no_route")
        ),
        "rank_one_exact_in_every_seed": all(
            item["conditional_exact"]
            for name in ("rank_one_baseline", "rank_one_strong")
            for item in episode(name)
        ),
        "baseline_rank_two_exact_in_every_seed": all(
            item["conditional_exact"] for item in episode("rank_two_baseline")
        ),
        "weak_rank_two_power": sum(
            item["conditional_exact"] for item in episode("rank_two_weak")
        )
        >= required_weak,
        "rank_three_power": sum(
            item["conditional_exact"] for item in episode("rank_three")
        )
        >= required_rank_three,
        "rank_two_integration_admitted_in_every_seed": all(
            item["conditional_exact"]
            and item["conditional_all_fits_exact"]
            and item["conditional_state_transition_exact"]
            and item["conditional_state_exact"]
            and item["conditional_acquired"]
            for item in episode("rank_two_integration")
        ),
        "one_window_state_remains_unadmitted": all(
            item["conditional_state_exact"]
            and item["conditional_state_transition_exact"]
            and item["conditional_selected_rank"] == 0
            and not item["conditional_acquired"]
            for name, _, _ in V031_SCENARIOS
            if name != "rank_two_integration"
            for item in episode(name)
        ),
        "no_null_or_rank_one_overranking": all(
            summary["conditional_false_overranks"] == 0
            for summary in summaries
        ),
        "positive_support_for_admitted_fits": all(
            summary["conditional_positive_support"] for summary in summaries
        ),
        "information_and_prequential_integrity": all(
            summary["integrity"] for summary in summaries
        ),
    }
    rows = [dict(row) for part in parts for row in part["rows"]]
    result = {
        "schema": V031_SCHEMA,
        "cohort": cohort,
        "seeds": list(seeds),
        "retained_rows": len(rows),
        "primary_gates": gates,
        "all_primary_gates_pass": bool(all(gates.values())),
        "conditional_exact_counts": {
            name: int(sum(item["conditional_exact"] for item in episode(name)))
            for name, _, _ in V031_SCENARIOS
        },
        "global_exact_counts": {
            name: int(sum(item["global_exact"] for item in episode(name)))
            for name, _, _ in V031_SCENARIOS
        },
        "seed_summaries": summaries,
        "interpretation": (
            "Conditional operational-rank inference in a bounded additive "
            "single-route benchmark; not awareness or consciousness evidence."
        ),
    }
    retained_receipts = {
        "schema": "rrct.v031.conditional_rank_inference.integrity_receipts.v1",
        "experiment_schema": V031_SCHEMA,
        "cohort": cohort,
        "seeds": list(seeds),
        "configuration": expected_config,
        "receipts": [
            {
                "seed": int(part["seed"]),
                "receipt": dict(part["receipt"]),
                "freeze_manifest_sha256": part.get(
                    "freeze_manifest_sha256"
                ),
                "seed_summary_integrity": bool(
                    part["seed_summary"]["integrity"]
                ),
            }
            for part in parts
        ],
        "interpretation": (
            "Retained per-seed information-boundary receipts; independent "
            "official verification is recorded separately."
        ),
    }
    destination = Path(output)
    if destination.exists():
        raise FileExistsError(f"refusing existing v0.31 aggregate: {destination}")
    destination.mkdir(parents=True)
    _write_json(destination / "v031_conditional_rank_summary.json", result)
    _write_csv(destination / "v031_conditional_rank_rows.csv", rows)
    flat_summaries = []
    for summary in summaries:
        for name, item in summary["episodes"].items():
            flat_summaries.append({"seed": summary["seed"], **item, "scenario": name})
    _write_csv(
        destination / "v031_conditional_rank_seed_summaries.csv",
        flat_summaries,
    )
    _write_json(
        destination / "v031_conditional_rank_integrity.json",
        retained_receipts,
    )
    hashes = {}
    for name in (
        "v031_conditional_rank_summary.json",
        "v031_conditional_rank_rows.csv",
        "v031_conditional_rank_seed_summaries.csv",
        "v031_conditional_rank_integrity.json",
    ):
        hashes[name] = hashlib.sha256((destination / name).read_bytes()).hexdigest()
    _write_json(destination / "v031_conditional_rank_sha256.json", hashes)
    return result


__all__ = [
    "V031_FROZEN_CANDIDATE_CONFIG",
    "V031_OFFICIAL_SEEDS",
    "V031_PILOT_SEEDS",
    "V031_SCENARIOS",
    "V031_SCENARIO_WINDOWS",
    "V031_SCHEMA",
    "aggregate_conditional_rank_results",
    "run_conditional_rank_seed",
]
