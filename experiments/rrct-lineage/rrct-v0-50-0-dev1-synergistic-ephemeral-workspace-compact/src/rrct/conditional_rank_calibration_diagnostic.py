"""Prefrozen v0.31 composite-rank calibration diagnostics.

This module is deliberately separate from the v0.31 candidate estimator and
its reserved official cohort.  It evaluates the rank-one composite null in a
larger development-only world cohort at an observable Monte Carlo tail.  The
diagnostic compares the cross-fitted lower-mode-preserving bootstrap with the
legacy global sharp-null mode-two screen.  It also provides a deterministic
receipt showing exactly which lower-rank response the two null constructions
do and do not preserve.

The diagnostic concerns one-step operational rank in a bounded synthetic
model.  It is not an exact Fisher test, a recursively regenerated dynamic
null, or evidence of awareness or consciousness.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

from . import causal_boundary as _boundary
from .causal_boundary import CausalBoundaryConfig, OnlineCausalSelfBoundary
from .conditional_rank_inference_experiment import (
    V031_FROZEN_CANDIDATE_CONFIG,
    V031_HANDLE_COUNT,
    V031_OBSERVATION_DIM,
    V031_PROCESS_DIM,
    V031_SOURCE_COUNT,
    V031RunConfig,
    _effect,
    _equal_energy_bank,
    _hidden_structure,
)


FloatArray = NDArray[np.float64]
V031_CALIBRATION_SCHEMA = "rrct.v031.rank_one_calibration_diagnostic.v2"
V031_CALIBRATION_SEEDS = tuple(range(891_000, 891_200))
V031_CALIBRATION_STRENGTH = 5.0
V031_CALIBRATION_RANDOMIZATIONS = 24
V031_CALIBRATION_QUANTILE = 0.95
V031_CALIBRATION_ALPHA = 0.05
V031_CALIBRATION_WORLD_SALT = 0x31CA
V031_CALIBRATION_CONFIG = V031RunConfig(
    null_permutations=V031_CALIBRATION_RANDOMIZATIONS,
    half_null_permutations=V031_CALIBRATION_RANDOMIZATIONS,
    null_quantile=V031_CALIBRATION_QUANTILE,
)

EXPECTED_PYTHON_VERSION = (3, 12, 13)
EXPECTED_NUMPY_VERSION = "2.2.6"
EXPECTED_THREAD_ENVIRONMENT = {
    "OPENBLAS_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
}
EXPECTED_RUNTIME_RECEIPT = {
    "python": ".".join(map(str, EXPECTED_PYTHON_VERSION)),
    "numpy": EXPECTED_NUMPY_VERSION,
    "thread_environment": dict(EXPECTED_THREAD_ENVIRONMENT),
}
_WORLD_RECORD_KEYS = {
    "schema",
    "seed",
    "mode_two_config",
    "online_learner_config",
    "target_handle",
    "target_source",
    "target_rank",
    "structure_digest",
    "trajectory_digest",
    "source_energy_error",
    "prequential_chain",
    "conditioned_handle",
    "conditioned_source",
    "pair_conditioning",
    "conditional_fold_a",
    "conditional_fold_b",
    "global_fold_a",
    "global_fold_b",
    "integrity",
}
_PAIR_CONDITIONING_KEYS = {
    "source",
    "conditioned_pair_equals_target",
    "pair_passed_to_online_causal_self_boundary",
    "pair_discovery_claimed_by_diagnostic",
    "pair_discovery_assigned_to_candidate_assays",
}
_FOLD_RECEIPT_KEYS = {
    "observed",
    "threshold",
    "p_value",
    "reject",
    "lower_modes_preserved_in_null",
}
_INTEGRITY_KEYS = {
    "retained_rows",
    "nonce_exact",
    "prequential_chain",
    "source_energy_error",
    "equal_source_energy",
    "structure_digest",
    "trajectory_digest",
    "target_handle",
    "target_source",
    "target_rank",
    "learner_seed",
    "learner_rng_independent_of_world_seed",
    "world_seed_passed_to_model",
    "hidden_pair_passed_to_model",
    "hidden_rank_passed_to_model",
    "conditioned_pair_passed_to_online_model",
    "observed_history_held_fixed",
}


def verify_rank_calibration_runtime() -> dict[str, Any]:
    """Require the exact predeclared diagnostic numerical runtime."""

    python_version = tuple(int(value) for value in sys.version_info[:3])
    if python_version != EXPECTED_PYTHON_VERSION:
        raise RuntimeError(
            "v0.31 calibration Python runtime mismatch: expected "
            f"{EXPECTED_RUNTIME_RECEIPT['python']}, observed "
            f"{'.'.join(map(str, python_version))}"
        )
    numpy_version = str(np.__version__)
    if numpy_version != EXPECTED_NUMPY_VERSION:
        raise RuntimeError(
            "v0.31 calibration NumPy runtime mismatch: expected "
            f"{EXPECTED_NUMPY_VERSION}, observed {numpy_version}"
        )
    observed_threads = {
        name: os.environ.get(name) for name in EXPECTED_THREAD_ENVIRONMENT
    }
    if observed_threads != EXPECTED_THREAD_ENVIRONMENT:
        raise RuntimeError(
            "v0.31 calibration numerical thread environment mismatch: "
            f"expected {EXPECTED_THREAD_ENVIRONMENT!r}, observed "
            f"{observed_threads!r}"
        )
    receipt = {
        "python": ".".join(map(str, python_version)),
        "numpy": numpy_version,
        "thread_environment": dict(observed_threads),
    }
    if receipt != EXPECTED_RUNTIME_RECEIPT:
        raise RuntimeError("v0.31 calibration runtime receipt mismatch")
    return receipt


def _diagnostic_boundary_config() -> CausalBoundaryConfig:
    return V031_CALIBRATION_CONFIG.boundary_config(
        method="cross_fitted_reduced_rank_randomization_bootstrap"
    )


def _online_learner_boundary_config() -> CausalBoundaryConfig:
    """Keep the online handle owner on the untouched candidate config."""

    return V031_FROZEN_CANDIDATE_CONFIG.boundary_config(
        method="cross_fitted_reduced_rank_randomization_bootstrap"
    )


def _arrays(
    observation: Sequence[FloatArray],
    bank: Sequence[FloatArray],
    handles: Sequence[FloatArray],
    next_observation: Sequence[FloatArray],
    nonces: Sequence[int],
) -> tuple[FloatArray, FloatArray, FloatArray, FloatArray, NDArray[np.int64]]:
    return (
        np.asarray(observation, dtype=np.float64),
        np.asarray(bank, dtype=np.float64),
        np.asarray(handles, dtype=np.float64),
        np.asarray(next_observation, dtype=np.float64),
        np.asarray(nonces, dtype=np.int64),
    )


def _trajectory_digest(
    arrays: tuple[FloatArray, FloatArray, FloatArray, FloatArray, NDArray[np.int64]],
) -> str:
    digest = hashlib.sha256()
    for value in arrays:
        array = np.ascontiguousarray(value)
        digest.update(array.dtype.str.encode("ascii"))
        digest.update(json.dumps(array.shape).encode("ascii"))
        digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _is_sha256(value: Any) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and value == value.lower()
        and all(character in "0123456789abcdef" for character in value)
    )


def _exact_bool(value: Any, name: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"v0.31 calibration {name} must be an exact boolean")
    return value


def _exact_int(value: Any, name: str) -> int:
    if type(value) is not int:
        raise ValueError(f"v0.31 calibration {name} must be an exact integer")
    return value


def _exact_finite_number(value: Any, name: str) -> float:
    if type(value) not in {int, float}:
        raise ValueError(f"v0.31 calibration {name} must be an exact number")
    parsed = float(value)
    if not np.isfinite(parsed):
        raise ValueError(f"v0.31 calibration {name} must be finite")
    return parsed


def _generate_rank_one_world(
    seed: int,
) -> tuple[
    tuple[FloatArray, FloatArray, FloatArray, FloatArray, NDArray[np.int64]],
    dict[str, Any],
]:
    """Generate one world while the frozen learner owns every handle."""

    structure = _hidden_structure(seed, V031_FROZEN_CANDIDATE_CONFIG)
    learner_config = _online_learner_boundary_config()
    learner = OnlineCausalSelfBoundary(learner_config)
    learner.freeze()
    rng = np.random.default_rng(
        np.random.SeedSequence([int(seed), V031_CALIBRATION_WORLD_SALT])
    )
    routed_effect = _effect(structure, (V031_CALIBRATION_STRENGTH,))
    current = np.zeros(V031_OBSERVATION_DIM, dtype=np.float64)
    observations: list[FloatArray] = []
    banks: list[FloatArray] = []
    handle_rows: list[FloatArray] = []
    outcomes: list[FloatArray] = []
    nonces: list[int] = []
    source_energy_error = 0.0
    prequential_chain = True
    for time in range(V031_FROZEN_CANDIDATE_CONFIG.scenario_steps):
        before = learner.state.model_digest
        commitment = learner.commit_handles(time=time)
        bank = _equal_energy_bank(rng)
        bound = learner.bind_sources(
            current,
            bank,
            commitment_digest=commitment.digest,
            time=time,
        )
        handle_index, source_index = structure.pair
        routed = (
            commitment.handles[handle_index]
            * bank[source_index]
            @ routed_effect
        )
        following = (
            V031_FROZEN_CANDIDATE_CONFIG.observation_persistence * current
            + routed
            + bank[structure.exogenous_source] @ structure.exogenous_effect
            + rng.normal(
                0.0,
                V031_FROZEN_CANDIDATE_CONFIG.observation_noise,
                size=V031_OBSERVATION_DIM,
            )
        )
        receipt = learner.reveal_outcome(
            following,
            transition_digest=bound.transition_digest,
            time=time + 1,
        )
        if receipt.fit_performed:
            raise RuntimeError("frozen calibration handle learner performed a fit")
        prequential_chain = bool(
            prequential_chain
            and receipt.model_digest_before == before
            and receipt.model_digest_after == learner.state.model_digest
            and receipt.commitment_digest == commitment.digest
            and receipt.transition_digest == bound.transition_digest
        )
        source_energy_error = max(
            source_energy_error,
            float(np.max(np.abs(np.linalg.norm(bank, axis=1) - 1.0))),
        )
        observations.append(np.asarray(current, dtype=np.float64))
        banks.append(np.asarray(bank, dtype=np.float64))
        handle_rows.append(np.asarray(commitment.handles, dtype=np.float64))
        outcomes.append(np.asarray(following, dtype=np.float64))
        nonces.append(int(commitment.nonce))
        current = np.asarray(following, dtype=np.float64)
    values = _arrays(observations, banks, handle_rows, outcomes, nonces)
    metadata = {
        "target_handle": int(structure.pair[0]),
        "target_source": int(structure.pair[1]),
        "target_rank": 1,
        "structure_digest": structure.digest,
        "trajectory_digest": _trajectory_digest(values),
        "source_energy_error": float(source_energy_error),
        "prequential_chain": bool(prequential_chain),
    }
    return values, metadata


def _conditional_fold_result(
    proposal: tuple[FloatArray, FloatArray, FloatArray, FloatArray, NDArray[np.int64]],
    confirmation: tuple[
        FloatArray,
        FloatArray,
        FloatArray,
        FloatArray,
        NDArray[np.int64],
    ],
    config: CausalBoundaryConfig,
    *,
    selected_pair: tuple[int, int],
    salt: int,
) -> dict[str, Any]:
    observed, threshold, p_value = _boundary._conditional_rank_randomization_test(
        proposal,
        confirmation,
        config,
        selected_pair=selected_pair,
        null_rank=1,
        permutations=V031_CALIBRATION_RANDOMIZATIONS,
        salt=salt,
    )
    return {
        "observed": float(observed),
        "threshold": float(threshold),
        "p_value": float(p_value),
        "reject": bool(observed > threshold),
        "lower_modes_preserved_in_null": True,
    }


def _global_sharp_null_fold_result(
    confirmation: tuple[
        FloatArray,
        FloatArray,
        FloatArray,
        FloatArray,
        NDArray[np.int64],
    ],
    config: CausalBoundaryConfig,
    *,
    selected_pair: tuple[int, int],
    salt: int,
) -> dict[str, Any]:
    """Apply the favorable same-fold ordered-mode global-null screen.

    The observed value is the selected pair's same-fold second singular value.
    Every null draw destroys all handle-mediated modes and uses the maximum
    second singular value over every pair.  This intentionally gives the old
    global screen a data-adaptive same-fold direction; it does not make that
    screen a conditional test of ``rank <= 1``.
    """

    observation, bank, handles, next_observation, nonces = confirmation
    outcome, interactions = _boundary._residual_problem(
        observation, bank, handles, next_observation, config
    )
    effects, _ = _boundary._operators(interactions, outcome, config)
    handle_index, source_index = selected_pair
    observed = float(
        np.linalg.svd(
            effects[handle_index, source_index], compute_uv=False
        )[1]
    )
    groups = _boundary._commitment_block_groups(
        nonces, config.commitment_block_size
    )
    rng = np.random.default_rng(
        np.random.SeedSequence(
            [
                config.seed,
                int(salt),
                len(observation),
                config.handle_count,
                config.source_count,
                int(nonces[groups[0][0]]),
                int(nonces[groups[-1][-1]]),
            ]
        )
    )
    null_values = np.empty(V031_CALIBRATION_RANDOMIZATIONS, dtype=np.float64)
    for draw in range(V031_CALIBRATION_RANDOMIZATIONS):
        randomized = _boundary._rerandomized_handles(
            handles, nonces, config.commitment_block_size, rng
        )
        null_outcome, null_interactions = _boundary._residual_problem(
            observation, bank, randomized, next_observation, config
        )
        null_effects, _ = _boundary._operators(
            null_interactions, null_outcome, config
        )
        null_values[draw] = float(
            np.max(np.linalg.svd(null_effects, compute_uv=False)[..., 1])
        )
    threshold = _boundary._monte_carlo_threshold(
        null_values, V031_CALIBRATION_QUANTILE
    )
    p_value = float(
        (1 + np.count_nonzero(null_values >= observed))
        / (V031_CALIBRATION_RANDOMIZATIONS + 1)
    )
    return {
        "observed": observed,
        "threshold": float(threshold),
        "p_value": p_value,
        "reject": bool(observed > threshold),
        "lower_modes_preserved_in_null": False,
    }


def run_rank_calibration_world(seed: int) -> dict[str, Any]:
    """Run one predeclared development-only rank-one null world."""

    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
        raise ValueError("seed must be an integer")
    parsed_seed = int(seed)
    if parsed_seed not in V031_CALIBRATION_SEEDS:
        raise ValueError("seed is not in the v0.31 calibration cohort")
    values, metadata = _generate_rank_one_world(parsed_seed)
    proposal = tuple(value[:240] for value in values)
    confirmation_a = tuple(value[240:360] for value in values)
    confirmation_b = tuple(value[360:480] for value in values)
    config = _diagnostic_boundary_config()
    conditioned_pair = (metadata["target_handle"], metadata["target_source"])
    conditional_a = _conditional_fold_result(
        proposal,
        confirmation_a,
        config,
        selected_pair=conditioned_pair,
        salt=31_211,
    )
    conditional_b = _conditional_fold_result(
        proposal,
        confirmation_b,
        config,
        selected_pair=conditioned_pair,
        salt=31_213,
    )
    global_a = _global_sharp_null_fold_result(
        confirmation_a,
        config,
        selected_pair=conditioned_pair,
        salt=31_501,
    )
    global_b = _global_sharp_null_fold_result(
        confirmation_b,
        config,
        selected_pair=conditioned_pair,
        salt=31_503,
    )
    return {
        "schema": V031_CALIBRATION_SCHEMA,
        "seed": parsed_seed,
        "mode_two_config": asdict(V031_CALIBRATION_CONFIG),
        "online_learner_config": asdict(V031_FROZEN_CANDIDATE_CONFIG),
        **metadata,
        "conditioned_handle": int(conditioned_pair[0]),
        "conditioned_source": int(conditioned_pair[1]),
        "pair_conditioning": {
            "source": "evaluator_ground_truth_for_mode_two_diagnostic_only",
            "conditioned_pair_equals_target": True,
            "pair_passed_to_online_causal_self_boundary": False,
            "pair_discovery_claimed_by_diagnostic": False,
            "pair_discovery_assigned_to_candidate_assays": True,
        },
        "conditional_fold_a": conditional_a,
        "conditional_fold_b": conditional_b,
        "global_fold_a": global_a,
        "global_fold_b": global_b,
        "integrity": {
            "retained_rows": int(len(values[0])),
            "nonce_exact": bool(np.array_equal(values[4], np.arange(480))),
            "prequential_chain": bool(metadata["prequential_chain"]),
            "source_energy_error": float(metadata["source_energy_error"]),
            "equal_source_energy": bool(metadata["source_energy_error"] <= 1e-12),
            "structure_digest": metadata["structure_digest"],
            "trajectory_digest": metadata["trajectory_digest"],
            "target_handle": int(metadata["target_handle"]),
            "target_source": int(metadata["target_source"]),
            "target_rank": int(metadata["target_rank"]),
            "learner_seed": int(_online_learner_boundary_config().seed),
            "learner_rng_independent_of_world_seed": bool(
                _online_learner_boundary_config().seed != parsed_seed
            ),
            "world_seed_passed_to_model": False,
            "hidden_pair_passed_to_model": False,
            "hidden_rank_passed_to_model": False,
            "conditioned_pair_passed_to_online_model": False,
            "observed_history_held_fixed": True,
        },
    }


def null_preservation_receipt() -> dict[str, Any]:
    """Return a deterministic rank-one reassignment preservation audit."""

    config = _diagnostic_boundary_config()
    count = config.commitment_block_size
    observation = np.zeros((count, V031_OBSERVATION_DIM), dtype=np.float64)
    bank = np.zeros(
        (count, V031_SOURCE_COUNT, V031_PROCESS_DIM), dtype=np.float64
    )
    bank[:, 2, 0] = 1.0
    handles = np.zeros((count, V031_HANDLE_COUNT), dtype=np.float64)
    handles[count // 2 :, 1] = 1.0
    reassigned = handles.copy()
    reassigned[:, 1] = 1.0 - reassigned[:, 1]
    effect = np.zeros(
        (V031_PROCESS_DIM, V031_OBSERVATION_DIM), dtype=np.float64
    )
    effect[0, 0] = 2.0
    nuisance_columns = (
        1
        + V031_OBSERVATION_DIM
        + V031_SOURCE_COUNT * V031_PROCESS_DIM
        + V031_HANDLE_COUNT
    )
    nuisance_coefficient = np.zeros(
        (nuisance_columns, V031_OBSERVATION_DIM), dtype=np.float64
    )
    residual = np.zeros((count, V031_OBSERVATION_DIM), dtype=np.float64)
    observed = _boundary._null_preserving_outcome(
        observation,
        bank,
        handles,
        residual,
        effect,
        nuisance_coefficient,
        config,
        selected_pair=(1, 2),
    )
    conditional = _boundary._null_preserving_outcome(
        observation,
        bank,
        reassigned,
        residual,
        effect,
        nuisance_coefficient,
        config,
        selected_pair=(1, 2),
    )
    expected = reassigned[:, 1, None] * (bank[:, 2] @ effect)
    denominator = max(float(np.linalg.norm(expected)), 1e-12)
    reconstruction_error = float(np.linalg.norm(conditional - expected) / denominator)
    legacy_relative_error = float(np.linalg.norm(observed - expected) / denominator)
    gates = {
        "conditional_reconstruction_error_at_most_1e_12": bool(
            reconstruction_error <= 1e-12
        ),
        "conditional_effect_is_rank_one": bool(np.linalg.matrix_rank(effect) == 1),
        "conditional_lower_mode_response_is_nonzero": bool(
            np.linalg.norm(conditional) > 0.0
        ),
        "legacy_relative_counterfactual_error_at_least_one": bool(
            legacy_relative_error >= 1.0
        ),
    }
    return {
        "schema": "rrct.v031.null_preservation_receipt.v1",
        "rows": count,
        "selected_pair": [1, 2],
        "physical_effect_rank": int(np.linalg.matrix_rank(effect)),
        "conditional_relative_reconstruction_error": reconstruction_error,
        "legacy_relative_counterfactual_error": legacy_relative_error,
        "gates": gates,
        "all_gates_pass": bool(all(gates.values())),
    }


def _validate_world_record(record: Mapping[str, Any], expected_seed: int) -> None:
    if not isinstance(record, Mapping) or set(record) != _WORLD_RECORD_KEYS:
        raise ValueError("v0.31 calibration world record key schema mismatch")
    if record.get("schema") != V031_CALIBRATION_SCHEMA:
        raise ValueError("v0.31 calibration world schema mismatch")
    if _exact_int(record.get("seed"), "seed") != expected_seed:
        raise ValueError("v0.31 calibration world seed mismatch")
    if record.get("mode_two_config") != asdict(V031_CALIBRATION_CONFIG):
        raise ValueError("v0.31 calibration mode-two configuration mismatch")
    if record.get("online_learner_config") != asdict(
        V031_FROZEN_CANDIDATE_CONFIG
    ):
        raise ValueError("v0.31 calibration online learner configuration mismatch")
    if _exact_int(record.get("target_rank"), "target_rank") != 1:
        raise ValueError("v0.31 calibration target rank mismatch")
    target_handle = _exact_int(record.get("target_handle"), "target_handle")
    target_source = _exact_int(record.get("target_source"), "target_source")
    if not 0 <= target_handle < V031_HANDLE_COUNT:
        raise ValueError("v0.31 calibration target handle is out of range")
    if not 0 <= target_source < V031_SOURCE_COUNT:
        raise ValueError("v0.31 calibration target source is out of range")
    if _exact_int(
        record.get("conditioned_handle"), "conditioned_handle"
    ) != target_handle or _exact_int(
        record.get("conditioned_source"), "conditioned_source"
    ) != target_source:
        raise ValueError("v0.31 calibration conditioned pair mismatch")
    for name in ("structure_digest", "trajectory_digest"):
        if not _is_sha256(record.get(name)):
            raise ValueError(f"v0.31 calibration {name} is not a SHA-256 digest")
    source_energy_error = _exact_finite_number(
        record.get("source_energy_error"), "source_energy_error"
    )
    if source_energy_error < 0.0:
        raise ValueError("v0.31 calibration source energy error is invalid")
    _exact_bool(record.get("prequential_chain"), "prequential_chain")
    pair_conditioning = record.get("pair_conditioning")
    if (
        not isinstance(pair_conditioning, Mapping)
        or set(pair_conditioning) != _PAIR_CONDITIONING_KEYS
    ):
        raise ValueError("v0.31 calibration pair-conditioning key schema mismatch")
    expected_pair_conditioning = {
        "source": "evaluator_ground_truth_for_mode_two_diagnostic_only",
        "conditioned_pair_equals_target": True,
        "pair_passed_to_online_causal_self_boundary": False,
        "pair_discovery_claimed_by_diagnostic": False,
        "pair_discovery_assigned_to_candidate_assays": True,
    }
    if pair_conditioning != expected_pair_conditioning:
        raise ValueError("v0.31 calibration pair-conditioning receipt mismatch")
    for name in (
        "conditioned_pair_equals_target",
        "pair_passed_to_online_causal_self_boundary",
        "pair_discovery_claimed_by_diagnostic",
        "pair_discovery_assigned_to_candidate_assays",
    ):
        _exact_bool(pair_conditioning.get(name), f"pair_conditioning.{name}")
    integrity = record.get("integrity")
    if not isinstance(integrity, Mapping) or set(integrity) != _INTEGRITY_KEYS:
        raise ValueError("v0.31 calibration integrity receipt key schema mismatch")
    for name in (
        "retained_rows",
        "target_handle",
        "target_source",
        "target_rank",
        "learner_seed",
    ):
        _exact_int(integrity.get(name), f"integrity.{name}")
    for name in (
        "nonce_exact",
        "prequential_chain",
        "equal_source_energy",
        "learner_rng_independent_of_world_seed",
        "world_seed_passed_to_model",
        "hidden_pair_passed_to_model",
        "hidden_rank_passed_to_model",
        "conditioned_pair_passed_to_online_model",
        "observed_history_held_fixed",
    ):
        _exact_bool(integrity.get(name), f"integrity.{name}")
    _exact_finite_number(
        integrity.get("source_energy_error"), "integrity.source_energy_error"
    )
    for name in ("structure_digest", "trajectory_digest"):
        if not _is_sha256(integrity.get(name)):
            raise ValueError(
                f"v0.31 calibration integrity.{name} is not a SHA-256 digest"
            )
    agreement = {
        "prequential_chain": bool(record["prequential_chain"]),
        "source_energy_error": source_energy_error,
        "structure_digest": record["structure_digest"],
        "trajectory_digest": record["trajectory_digest"],
        "target_handle": target_handle,
        "target_source": target_source,
        "target_rank": 1,
    }
    for name, expected in agreement.items():
        if integrity.get(name) != expected:
            raise ValueError(
                f"v0.31 calibration top-level/integrity {name} mismatch"
            )
    if bool(integrity.get("equal_source_energy")) != bool(
        source_energy_error <= 1e-12
    ):
        raise ValueError("v0.31 calibration source-energy integrity mismatch")
    for name in (
        "conditional_fold_a",
        "conditional_fold_b",
        "global_fold_a",
        "global_fold_b",
    ):
        value = record.get(name)
        if not isinstance(value, Mapping) or set(value) != _FOLD_RECEIPT_KEYS:
            raise ValueError(
                f"v0.31 calibration {name} receipt key schema mismatch"
            )
        parsed_statistics = {}
        for statistic in ("observed", "threshold", "p_value"):
            parsed = _exact_finite_number(
                value.get(statistic), f"{name}.{statistic}"
            )
            parsed_statistics[statistic] = parsed
        observed = parsed_statistics["observed"]
        threshold = parsed_statistics["threshold"]
        p_value = parsed_statistics["p_value"]
        if observed < 0.0 or threshold < 0.0:
            raise ValueError(f"v0.31 calibration {name} statistic is negative")
        lattice_value = p_value * (V031_CALIBRATION_RANDOMIZATIONS + 1)
        lattice_integer = int(round(lattice_value))
        if (
            not 1 <= lattice_integer <= V031_CALIBRATION_RANDOMIZATIONS + 1
            or not np.isclose(
                lattice_value, lattice_integer, rtol=0.0, atol=1e-12
            )
        ):
            raise ValueError(
                f"v0.31 calibration {name} p-value is off the add-one lattice"
            )
        _exact_bool(value.get("reject"), f"{name}.reject")
        by_p_value = bool(p_value <= V031_CALIBRATION_ALPHA)
        by_threshold = bool(observed > threshold)
        if bool(value["reject"]) != by_p_value or by_p_value != by_threshold:
            raise ValueError(
                f"v0.31 calibration {name} rejection coherence mismatch"
            )
    for name in ("conditional_fold_a", "conditional_fold_b"):
        value = record[name]
        if _exact_bool(
            value.get("lower_modes_preserved_in_null"),
            f"{name}.lower_modes_preserved_in_null",
        ) is not True:
            raise ValueError(
                "conditional receipt does not record lower-mode preservation"
            )
    for name in ("global_fold_a", "global_fold_b"):
        value = record[name]
        if _exact_bool(
            value.get("lower_modes_preserved_in_null"),
            f"{name}.lower_modes_preserved_in_null",
        ) is not False:
            raise ValueError(
                "legacy global-null receipt does not record destroyed lower modes"
            )


def evaluate_rank_calibration_records(
    records: Sequence[Mapping[str, Any]],
    *,
    runtime_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Recompute every diagnostic gate from all 200 retained world records."""

    if len(records) != len(V031_CALIBRATION_SEEDS):
        raise ValueError("v0.31 calibration requires exactly 200 world records")
    for record, seed in zip(records, V031_CALIBRATION_SEEDS, strict=True):
        _validate_world_record(record, seed)
    if dict(runtime_receipt) != EXPECTED_RUNTIME_RECEIPT:
        raise ValueError("v0.31 calibration aggregate runtime receipt mismatch")

    all_folds_present = all(
        isinstance(record[name], Mapping)
        for record in records
        for name in (
            "conditional_fold_a",
            "conditional_fold_b",
            "global_fold_a",
            "global_fold_b",
        )
    )

    def rejects(name: str) -> int:
        return int(
            sum(
                float(record[name]["p_value"]) <= V031_CALIBRATION_ALPHA
                for record in records
            )
        )

    conditional_a = rejects("conditional_fold_a")
    conditional_b = rejects("conditional_fold_b")
    global_a = rejects("global_fold_a")
    global_b = rejects("global_fold_b")
    conditional_pooled = conditional_a + conditional_b
    global_pooled = global_a + global_b
    information_integrity = all(
        int(record["integrity"]["retained_rows"]) == 480
        and bool(record["integrity"]["nonce_exact"])
        and bool(record["integrity"]["prequential_chain"])
        and bool(record["integrity"]["equal_source_energy"])
        and int(record["integrity"]["learner_seed"])
        == V031_FROZEN_CANDIDATE_CONFIG.learner_seed
        and bool(record["integrity"]["learner_rng_independent_of_world_seed"])
        and not bool(record["integrity"]["world_seed_passed_to_model"])
        and not bool(record["integrity"]["hidden_pair_passed_to_model"])
        and not bool(record["integrity"]["hidden_rank_passed_to_model"])
        and not bool(
            record["integrity"]["conditioned_pair_passed_to_online_model"]
        )
        and bool(record["integrity"]["observed_history_held_fixed"])
        for record in records
    )
    pair_conditioning_integrity = all(
        int(record["conditioned_handle"]) == int(record["target_handle"])
        and int(record["conditioned_source"]) == int(record["target_source"])
        and record["pair_conditioning"]
        == {
            "source": "evaluator_ground_truth_for_mode_two_diagnostic_only",
            "conditioned_pair_equals_target": True,
            "pair_passed_to_online_causal_self_boundary": False,
            "pair_discovery_claimed_by_diagnostic": False,
            "pair_discovery_assigned_to_candidate_assays": True,
        }
        for record in records
    )
    preservation = null_preservation_receipt()
    gates = {
        "all_200_worlds_and_folds_retained": bool(all_folds_present),
        "pair_conditioning_is_evaluator_only_and_never_passed_online": bool(
            pair_conditioning_integrity
        ),
        "conditional_fold_a_rejections_between_2_and_20": bool(
            2 <= conditional_a <= 20
        ),
        "conditional_fold_b_rejections_between_2_and_20": bool(
            2 <= conditional_b <= 20
        ),
        "global_fold_a_rejections_at_most_1": bool(global_a <= 1),
        "global_fold_b_rejections_at_most_1": bool(global_b <= 1),
        "conditional_pooled_exceeds_global_by_at_least_5": bool(
            conditional_pooled >= global_pooled + 5
        ),
        "information_and_runtime_integrity": bool(information_integrity),
        "deterministic_lower_mode_preservation": bool(
            preservation["all_gates_pass"]
        ),
    }
    return {
        "schema": V031_CALIBRATION_SCHEMA,
        "status": "development_calibration_diagnostic",
        "seeds": list(V031_CALIBRATION_SEEDS),
        "retained_worlds": len(records),
        "runtime_receipt": dict(runtime_receipt),
        "counts": {
            "conditional_fold_a_rejections": conditional_a,
            "conditional_fold_b_rejections": conditional_b,
            "conditional_pooled_rejections": conditional_pooled,
            "global_fold_a_rejections": global_a,
            "global_fold_b_rejections": global_b,
            "global_pooled_rejections": global_pooled,
        },
        "null_preservation_receipt": preservation,
        "primary_gates": gates,
        "all_primary_gates_pass": bool(all(gates.values())),
        "world_records": [dict(record) for record in records],
        "interpretation": (
            "Development-only rank-one composite-null calibration and null-"
            "preservation diagnostic; not an exact dynamic test and not "
            "awareness or consciousness evidence."
        ),
    }


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def aggregate_rank_calibration_records(
    records: Sequence[Mapping[str, Any]],
    output: Path,
    *,
    runtime_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate, aggregate, retain, and hash the complete diagnostic cohort."""

    result = evaluate_rank_calibration_records(
        records, runtime_receipt=runtime_receipt
    )
    destination = Path(output)
    if destination.exists():
        raise FileExistsError(
            f"refusing existing v0.31 calibration output: {destination}"
        )
    destination.mkdir(parents=True)
    _write_json(destination / "v031_rank_calibration_summary.json", result)
    _write_json(
        destination / "v031_rank_calibration_runtime.json",
        dict(runtime_receipt),
    )

    def fold_value(record: Mapping[str, Any], name: str, field: str) -> Any:
        fold = record[name]
        return None if fold is None else fold[field]

    flat_rows = []
    for record in records:
        flat_rows.append(
            {
                "schema": record["schema"],
                "seed": record["seed"],
                "target_handle": record["target_handle"],
                "target_source": record["target_source"],
                "conditioned_handle": record["conditioned_handle"],
                "conditioned_source": record["conditioned_source"],
                "pair_conditioning_source": record["pair_conditioning"]["source"],
                "pair_passed_to_online_model": record["pair_conditioning"][
                    "pair_passed_to_online_causal_self_boundary"
                ],
                "conditional_fold_a_reject": fold_value(
                    record, "conditional_fold_a", "reject"
                ),
                "conditional_fold_a_p_value": fold_value(
                    record, "conditional_fold_a", "p_value"
                ),
                "conditional_fold_b_reject": fold_value(
                    record, "conditional_fold_b", "reject"
                ),
                "conditional_fold_b_p_value": fold_value(
                    record, "conditional_fold_b", "p_value"
                ),
                "global_fold_a_reject": fold_value(
                    record, "global_fold_a", "reject"
                ),
                "global_fold_a_p_value": fold_value(
                    record, "global_fold_a", "p_value"
                ),
                "global_fold_b_reject": fold_value(
                    record, "global_fold_b", "reject"
                ),
                "global_fold_b_p_value": fold_value(
                    record, "global_fold_b", "p_value"
                ),
                "trajectory_digest": record["trajectory_digest"],
                "structure_digest": record["structure_digest"],
            }
        )
    with (destination / "v031_rank_calibration_worlds.csv").open(
        "x", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=list(flat_rows[0]))
        writer.writeheader()
        writer.writerows(flat_rows)
    hashes = {}
    for name in (
        "v031_rank_calibration_summary.json",
        "v031_rank_calibration_runtime.json",
        "v031_rank_calibration_worlds.csv",
    ):
        hashes[name] = hashlib.sha256((destination / name).read_bytes()).hexdigest()
    _write_json(destination / "v031_rank_calibration_sha256.json", hashes)
    return result


__all__ = [
    "EXPECTED_RUNTIME_RECEIPT",
    "V031_CALIBRATION_CONFIG",
    "V031_CALIBRATION_SCHEMA",
    "V031_CALIBRATION_SEEDS",
    "aggregate_rank_calibration_records",
    "evaluate_rank_calibration_records",
    "null_preservation_receipt",
    "run_rank_calibration_world",
    "verify_rank_calibration_runtime",
]
