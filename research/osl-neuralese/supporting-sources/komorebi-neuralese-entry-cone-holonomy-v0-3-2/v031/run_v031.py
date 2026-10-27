#!/usr/bin/env python3
"""Run the one frozen Neuralese v0.3.1 diagnostic profile.

Author: Komorebi P.

There are no scientific command-line switches.  The global execution freeze,
fresh episode serialization, exact word bank, inherited lineage result, source
files, and checkpoint bytes are validated before a learned endpoint is opened.
The registered output path is created atomically and is never overwritten.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import platform
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# This declaration is intentionally duplicated from ``freeze_v031.py``.  The
# registered runner must authenticate its own bytes and every other frozen
# input before importing NumPy or any local scientific module; importing the
# freeze validator first would defeat that boundary.
_BOOTSTRAP_SCHEMA = "komorebi.neuralese.entry_cone_holonomy.execution_freeze.v1"
_BOOTSTRAP_STATUS = "FROZEN_BEFORE_FRESH_LEARNED_ENDPOINT_EXECUTION"
_BOOTSTRAP_REQUIRED_FILES = frozenset(
    {
        "DESIGN_DISCLOSURE.json",
        "EXECUTION_FREEZE.json",
        "checkpoint_io.py",
        "checkpoints/projective_terminal_seed0.pt",
        "checkpoints/projective_terminal_seed1.pt",
        "core.py",
        "results/LINEAGE_REGRESSION.json",
        "v031/__init__.py",
        "v031/V031_FROZEN_INPUTS.json",
        "v031/V031_MATCHED_WORD_BANK.json",
        "v031/V031_PREFREEZE_VALIDATION.json",
        "v031/V031_PREREGISTRATION.json",
        "v031/V031_RESEARCH_SPEC.md",
        "v031/requirements.txt",
        "v031/entry_recurrence_probe.py",
        "v031/freeze_v031.py",
        "v031/generate_v031_inputs.py",
        "v031/generate_word_bank.py",
        "v031/holonomy_spectroscopy.py",
        "v031/matched_controls.py",
        "v031/run_v031.py",
        "v031/test_entry_recurrence_probe.py",
        "v031/test_holonomy_spectroscopy.py",
        "v031/test_matched_controls.py",
        "v031/test_v031_contract.py",
        "v031/test_v031_engine.py",
        "v031/v031_engine.py",
    }
)
EXPECTED_PYTHON_IMPLEMENTATION = "CPython"
EXPECTED_PYTHON_VERSION = "3.12.13"
EXPECTED_NUMPY_VERSION = "2.3.5"
sys.dont_write_bytecode = True
_BOOTSTRAP_AUTHENTICATED = False


def _bootstrap_duplicate_rejector(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate JSON key in execution freeze: {key}")
        output[key] = value
    return output


def _bootstrap_file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bootstrap_reject_executable_bytecode() -> None:
    """Reject caches that could be imported instead of frozen source bytes."""

    pyc_files = sorted(
        str(path.relative_to(ROOT)) for path in ROOT.rglob("*.pyc") if path.is_file()
    )
    cache_directories = sorted(
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("__pycache__")
        if path.is_dir()
    )
    if pyc_files or cache_directories:
        raise RuntimeError(
            "executable Python bytecode/cache is forbidden for the registered run: "
            f"pyc={pyc_files}, cache_dirs={cache_directories}"
        )


def _bootstrap_validate_frozen_bytes() -> dict[str, str]:
    """Authenticate the complete frozen byte set using only the stdlib."""

    freeze_path = HERE / "V031_EXECUTION_FREEZE.json"
    with freeze_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle, object_pairs_hook=_bootstrap_duplicate_rejector)
    if not isinstance(value, dict):
        raise ValueError("execution freeze root must be an object")
    if (
        value.get("schema") != _BOOTSTRAP_SCHEMA
        or value.get("version") != "0.3.1"
        or value.get("author") != "Komorebi P."
        or value.get("status") != _BOOTSTRAP_STATUS
    ):
        raise ValueError("execution freeze identity or status mismatch")
    files = value.get("files")
    if not isinstance(files, dict) or set(files) != _BOOTSTRAP_REQUIRED_FILES:
        raise ValueError("execution freeze has a nonregistered byte map")
    profile = value.get("registered_profile")
    if not isinstance(profile, dict):
        raise ValueError("execution freeze has no registered profile")
    if profile.get("registered_result") != (
        "results/V031_ENTRY_CONE_HOLONOMY_RESULTS.json"
    ) or profile.get("registered_run_started") != "results/V031_RUN_STARTED.json":
        raise ValueError("execution freeze output-ledger profile mismatch")
    if profile.get("runtime_contract") != {
        "python_implementation": EXPECTED_PYTHON_IMPLEMENTATION,
        "python_version": EXPECTED_PYTHON_VERSION,
        "numpy_version": EXPECTED_NUMPY_VERSION,
    }:
        raise ValueError("execution freeze runtime contract mismatch")
    validated: dict[str, str] = {}
    for relative, expected in files.items():
        if not isinstance(relative, str) or not isinstance(expected, str):
            raise ValueError("execution-freeze digest map is malformed")
        candidate = (ROOT / relative).resolve()
        try:
            candidate.relative_to(ROOT.resolve())
        except ValueError as error:
            raise ValueError(f"unsafe frozen path: {relative}") from error
        if not candidate.is_file():
            raise FileNotFoundError(f"frozen input is missing: {relative}")
        observed = _bootstrap_file_sha256(candidate)
        if observed != expected:
            raise ValueError(f"frozen-byte digest mismatch: {relative}")
        validated[relative] = observed
    return validated


# A CLI invocation crosses the one-time learned-endpoint boundary.  Do this
# before importing NumPy, checkpoint I/O, or any local scientific code.
if __name__ == "__main__":
    _bootstrap_reject_executable_bytecode()
    _bootstrap_validate_frozen_bytes()
    _BOOTSTRAP_AUTHENTICATED = True

if (
    platform.python_implementation() != EXPECTED_PYTHON_IMPLEMENTATION
    or platform.python_version() != EXPECTED_PYTHON_VERSION
):
    raise RuntimeError(
        "registered runtime requires "
        f"{EXPECTED_PYTHON_IMPLEMENTATION} {EXPECTED_PYTHON_VERSION}; observed "
        f"{platform.python_implementation()} {platform.python_version()}"
    )

import numpy as np

if np.__version__ != EXPECTED_NUMPY_VERSION:
    raise RuntimeError(
        f"registered runtime requires NumPy {EXPECTED_NUMPY_VERSION}; "
        f"observed {np.__version__}"
    )


for directory in (ROOT, HERE):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import checkpoint_io  # noqa: E402
import core  # noqa: E402
import entry_recurrence_probe as entry  # noqa: E402
import freeze_v031 as freeze  # noqa: E402
import holonomy_spectroscopy as holonomy  # noqa: E402
import matched_controls as matched  # noqa: E402
import v031_engine as engine  # noqa: E402


VERSION = "0.3.1"
AUTHOR = "Komorebi P."
MAXIMUM_SUFFIX_HORIZON = 8
MAXIMUM_HISTORY_DEPTH = 8
ROBUST_CLEARANCE = 1e-10
RAY_TOLERANCE = 1e-10
RESULT_PATH = ROOT / "results" / "V031_ENTRY_CONE_HOLONOMY_RESULTS.json"
INVALID_ATTEMPT_PATH = ROOT / "results" / "V031_INVALID_ATTEMPT.json"
RUN_STARTED_PATH = ROOT / "results" / "V031_RUN_STARTED.json"
CHECKPOINT_DIGESTS = {
    0: "b2d16d640dddc4f2f2ed69a4211f0d9948c71c3655901484238fa8ae11c1f702",
    1: "a52dd3def596553c2880dfd00516bd1bb7492d1cbfab1634b570f27c1737d2d7",
}
RELATIONS: dict[str, tuple[int, ...]] = {
    "f2": (1, 1),
    "r4": (0, 0, 0, 0),
    "frfr": (1, 0, 1, 0),
    "rfrf": (0, 1, 0, 1),
}
REPEAT_GRIDS = {
    "f2": tuple(range(33)),
    "r4": tuple(range(17)),
    "frfr": tuple(range(17)),
    "rfrf": tuple(range(17)),
}


@dataclass(frozen=True)
class EpisodeContext:
    checkpoint_seed: int
    checkpoint_sha256: str
    episode_seed: int
    episode_index: int
    weights: Any
    tables: np.ndarray
    slot_maps: np.ndarray
    canonical_to_slot: np.ndarray
    canonical_codes: np.ndarray
    canonical_maps: np.ndarray
    suffix_bank: engine.SuffixFacetBank
    base_states: np.ndarray
    base_semantic: np.ndarray
    base_locators: tuple[dict[str, Any], ...]
    baseline_states_by_endpoint: tuple[np.ndarray, ...]
    baseline_semantic_by_endpoint: tuple[np.ndarray, ...]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _duplicate_rejector(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def load_json(path: Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle, object_pairs_hook=_duplicate_rejector)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def json_safe(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return json_safe(value.tolist())
    if isinstance(value, np.generic):
        return json_safe(value.item())
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, float):
        if not np.isfinite(value):
            raise ValueError("nonfinite float cannot enter the registered JSON result")
        return float(value)
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise TypeError(f"unsupported JSON value: {type(value).__name__}")


def atomic_create_json(path: Path, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(f"refusing to overwrite registered output: {target}")
    temporary = target.with_name(f".{target.name}.tmp-{os.getpid()}")
    if temporary.exists():
        raise FileExistsError(f"refusing to reuse temporary output: {temporary}")
    payload = json.dumps(json_safe(value), indent=2, sort_keys=True, allow_nan=False) + "\n"
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def _refuse_existing_execution_artifacts() -> None:
    for path in (RUN_STARTED_PATH, INVALID_ATTEMPT_PATH, RESULT_PATH):
        if path.exists():
            raise FileExistsError(
                f"refusing learned-endpoint execution because an execution "
                f"artifact already exists: {path}"
            )


def _create_run_started_ledger(
    freeze_validation: Mapping[str, Any]
) -> dict[str, Any]:
    """Irreversibly mark the boundary immediately before checkpoint loading."""

    atomic_create_json(
        RUN_STARTED_PATH,
        {
            "schema": "komorebi.neuralese.entry_cone_holonomy.run_started.v1",
            "version": VERSION,
            "author": AUTHOR,
            "status": "CREATED_BEFORE_LEARNED_CHECKPOINT_LOADING",
            "utc": utc_now(),
            "execution_freeze_sha256": freeze_validation["freeze_sha256"],
            "registered_result": str(RESULT_PATH),
            "registered_invalid_attempt": str(INVALID_ATTEMPT_PATH),
            "runtime_contract": {
                "python_implementation": platform.python_implementation(),
                "python_version": platform.python_version(),
                "numpy_version": np.__version__,
            },
        },
    )
    return {
        "passed": True,
        "path": str(RUN_STARTED_PATH),
        "sha256": _bootstrap_file_sha256(RUN_STARTED_PATH),
        "status": "CREATED_BEFORE_LEARNED_CHECKPOINT_LOADING",
    }


def progress(message: str) -> None:
    print(f"[{utc_now()}] {message}", flush=True)


def _validate_runtime_contract() -> dict[str, Any]:
    observed = {
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
    }
    expected = {
        "python_implementation": EXPECTED_PYTHON_IMPLEMENTATION,
        "python_version": EXPECTED_PYTHON_VERSION,
        "numpy_version": EXPECTED_NUMPY_VERSION,
    }
    if observed != expected:
        raise RuntimeError(
            f"registered runtime contract mismatch: {observed!r} != {expected!r}"
        )
    return {"passed": True, "expected": expected, "observed": observed}


def _validate_module_locations() -> None:
    expected = {
        checkpoint_io: ROOT,
        core: ROOT,
        entry: HERE,
        freeze: HERE,
        holonomy: HERE,
        matched: HERE,
        engine: HERE,
    }
    for module, parent in expected.items():
        if Path(module.__file__).resolve().parent != parent.resolve():
            raise ImportError(f"module collision for {module.__name__}")


def _episode_arrays(record: Mapping[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    tables = np.asarray(record["tables"], dtype=np.float64)
    maps_raw = np.asarray(record["slot_maps"])
    mapping_raw = np.asarray(record["canonical_to_slot"])
    if not np.issubdtype(maps_raw.dtype, np.integer) or not np.issubdtype(
        mapping_raw.dtype, np.integer
    ):
        raise ValueError("serialized maps must have integer dtypes")
    maps = maps_raw.astype(np.int64, copy=False)
    mapping = mapping_raw.astype(np.int64, copy=False)
    if tables.shape != (2, 8, 8) or maps.shape != (2, 8) or mapping.shape != (2,):
        raise ValueError("serialized episode shapes changed")
    if set(mapping.tolist()) != {0, 1}:
        raise ValueError("canonical_to_slot is not a permutation")
    if any(not np.array_equal(np.sort(row), np.arange(8)) for row in maps):
        raise ValueError("serialized semantic map is not a permutation")
    if not np.array_equal(tables, np.eye(8)[maps]):
        raise ValueError("serialized table and semantic map disagree")
    return tables, maps, mapping


def _build_base_transversal(
    weights: Any,
    codes: np.ndarray,
    maps: np.ndarray,
    input_payload: Mapping[str, Any],
) -> tuple[
    np.ndarray,
    np.ndarray,
    tuple[dict[str, Any], ...],
    tuple[np.ndarray, ...],
    tuple[np.ndarray, ...],
]:
    words = input_payload["base_transversal"]["words"]
    anchors = weights.state_embedding.astype(np.float64)
    base_states: list[np.ndarray] = []
    base_semantic: list[np.ndarray] = []
    locators: list[dict[str, Any]] = []
    for endpoint_index, endpoint_name in enumerate(matched.ENDPOINT_NAMES):
        word = tuple(map(int, words[endpoint_name]))
        if not word:
            raise ValueError("base transversal must not reuse an entry anchor")
        if matched.endpoint_index(word) != endpoint_index:
            raise ValueError("base-transversal endpoint index changed")
        states = holonomy.apply_word_ray(codes, anchors, word)
        labels = holonomy.semantic_word_action(
            maps, np.arange(8, dtype=np.int64), word
        )
        base_states.append(states)
        base_semantic.append(labels)
        for start in range(8):
            locators.append(
                {
                    "base_endpoint_index": endpoint_index,
                    "base_endpoint_name": endpoint_name,
                    "base_word": list(word),
                    "visible_start": start,
                }
            )
    states_all = np.concatenate(base_states, axis=0)
    semantic_all = np.concatenate(base_semantic, axis=0)
    if states_all.shape != (64, 8) or semantic_all.shape != (64,):
        raise ArithmeticError("base-transversal count changed")

    baseline_states: list[np.ndarray] = []
    baseline_semantic: list[np.ndarray] = []
    for endpoint_index, representative in enumerate(
        matched.ENDPOINT_REPRESENTATIVE_WORDS
    ):
        endpoint_states = holonomy.apply_word_ray(codes, states_all, representative)
        endpoint_semantic = holonomy.semantic_word_action(
            maps, semantic_all, representative
        )
        if matched.endpoint_index(representative) != endpoint_index:
            raise ArithmeticError("endpoint representative order changed")
        baseline_states.append(endpoint_states)
        baseline_semantic.append(endpoint_semantic)
    return (
        states_all,
        semantic_all,
        tuple(locators),
        tuple(baseline_states),
        tuple(baseline_semantic),
    )


def build_contexts(
    checkpoints: Mapping[int, Any], input_payload: Mapping[str, Any]
) -> list[EpisodeContext]:
    contexts: list[EpisodeContext] = []
    for seed in (0, 1):
        checkpoint = checkpoints[seed]
        source = input_payload["checkpoints"][str(seed)]
        for record in source["episodes"]:
            episode_index = int(record["episode_index"])
            tables, slot_maps, mapping = _episode_arrays(record)
            slot_codes = core.encode_tables(
                checkpoint.weights, tables[None, ...], np.float64
            )[0]
            codes = slot_codes[mapping]
            maps = slot_maps[mapping]
            if codes.shape != (2, 8, 8) or not np.isfinite(codes).all():
                raise ArithmeticError("learned episode operator is invalid")
            suffix_bank = engine.build_suffix_facet_bank(
                codes, maps, checkpoint.weights.decoder, MAXIMUM_SUFFIX_HORIZON
            )
            (
                base_states,
                base_semantic,
                base_locators,
                baselines,
                baseline_semantic,
            ) = _build_base_transversal(
                checkpoint.weights, codes, maps, input_payload
            )
            contexts.append(
                EpisodeContext(
                    checkpoint_seed=seed,
                    checkpoint_sha256=checkpoint.sha256,
                    episode_seed=int(source["episode_seed"]),
                    episode_index=episode_index,
                    weights=checkpoint.weights,
                    tables=tables,
                    slot_maps=slot_maps,
                    canonical_to_slot=mapping,
                    canonical_codes=codes,
                    canonical_maps=maps,
                    suffix_bank=suffix_bank,
                    base_states=base_states,
                    base_semantic=base_semantic,
                    base_locators=base_locators,
                    baseline_states_by_endpoint=baselines,
                    baseline_semantic_by_endpoint=baseline_semantic,
                )
            )
            progress(
                f"encoded checkpoint {seed}, fresh episode {episode_index}; "
                f"minimum pulled-back facet norm={suffix_bank.minimum_pulled_back_facet_norm:.6g}"
            )
    if len(contexts) != 16:
        raise ArithmeticError("fresh context count changed")
    return contexts


def compact_audit(summary: Mapping[str, Any]) -> dict[str, Any]:
    fields = (
        "case_count",
        "maximum_suffix_horizon",
        "suffix_count_per_case",
        "decision_count",
        "strict_correct_count",
        "strict_error_count",
        "all_cases_survive",
        "failure_case_count",
        "first_failure_histogram",
        "reveal_case_count",
        "first_reveal_histogram",
        "minimum_target_margin",
        "minimum_angular_clearance",
        "robust_clearance_above_1e_minus_10",
        "minimum_target_margin_witness",
        "minimum_angular_clearance_witness",
        "prediction_sha256",
        "strict_mask_sha256",
        "recursive_suffix_consistency",
    )
    return {field: summary[field] for field in fields}


def _first_event_histogram(mask: np.ndarray, bank: engine.SuffixFacetBank) -> dict[str, int]:
    histogram = {str(depth): 0 for depth in range(bank.maximum_horizon + 1)}
    histogram["none"] = 0
    for row in np.asarray(mask, dtype=bool):
        locations = np.flatnonzero(row)
        if locations.size:
            histogram[str(int(bank.depths[int(locations[0])]))] += 1
        else:
            histogram["none"] += 1
    return histogram


def _eligible_relation_audit(
    audit: engine.AuditResult,
    eligible_cases: np.ndarray,
    bank: engine.SuffixFacetBank,
) -> dict[str, Any]:
    """Summarize a relation only over H8-valid pre-insertion base cases."""

    eligible = np.asarray(eligible_cases, dtype=bool)
    if eligible.ndim != 1 or eligible.size != audit.strict.shape[0]:
        raise ValueError("relation eligibility mask has the wrong shape")
    strict = audit.strict[eligible]
    margins = audit.target_margins[eligible]
    clearances = audit.angular_clearances[eligible]
    reveals = None if audit.reveals is None else audit.reveals[eligible]
    failure_mask = ~strict
    eligible_count = int(np.sum(eligible))
    if eligible_count:
        failure_case_count = int(np.sum(np.any(failure_mask, axis=1)))
        minimum_margin: float | None = float(np.min(margins))
        minimum_clearance: float | None = float(np.min(clearances))
    else:
        failure_case_count = 0
        minimum_margin = None
        minimum_clearance = None
    if reveals is None:
        reveal_case_count = None
        reveal_histogram = None
    else:
        reveal_case_count = int(np.sum(np.any(reveals, axis=1)))
        reveal_histogram = _first_event_histogram(reveals, bank)
    return {
        "eligible_case_count": eligible_count,
        "excluded_case_count": int(eligible.size - eligible_count),
        "failure_case_count": failure_case_count,
        "reveal_case_count": reveal_case_count,
        "first_failure_histogram": _first_event_histogram(failure_mask, bank),
        "first_reveal_histogram": reveal_histogram,
        "minimum_target_margin": minimum_margin,
        "minimum_angular_clearance": minimum_clearance,
    }


def _replicated_exit_cells(
    event_index: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return relation/repeat cells with exits in all four seed/half strata."""

    required = {(0, "first"), (0, "second"), (1, "first"), (1, "second")}
    strata: dict[tuple[str, int], set[tuple[int, str]]] = {}
    for event in event_index:
        cell = (str(event["relation"]), int(event["repeat_count"]))
        strata.setdefault(cell, set()).add(
            (int(event["checkpoint_seed"]), str(event["episode_half"]))
        )
    return [
        {
            "relation": relation,
            "repeat_count": repeat_count,
            "inserted_token_budget": repeat_count * len(RELATIONS[relation]),
            "checkpoint_episode_half_strata": [
                {"checkpoint_seed": seed, "episode_half": half}
                for seed, half in sorted(observed)
            ],
        }
        for (relation, repeat_count), observed in sorted(strata.items())
        if observed == required
    ]


def run_entry_module(
    checkpoints: Mapping[int, Any],
    contexts: Sequence[EpisodeContext],
    input_payload: Mapping[str, Any],
) -> dict[str, Any]:
    context_index = {
        (context.checkpoint_seed, context.episode_index): context
        for context in contexts
    }
    seed_records: dict[str, Any] = {}
    decoy_episode_records: list[dict[str, Any]] = []
    for seed in (0, 1):
        source = input_payload["checkpoints"][str(seed)]
        batch = SimpleNamespace(
            tables=np.asarray([item["tables"] for item in source["episodes"]], dtype=np.float64),
            maps=np.asarray([item["slot_maps"] for item in source["episodes"]], dtype=np.int64),
            canonical_to_slot=np.asarray(
                [item["canonical_to_slot"] for item in source["episodes"]],
                dtype=np.int64,
            ),
        )
        episode_records: list[dict[str, Any]] = []
        for episode_index in range(8):
            record = entry.evaluate_episode(
                checkpoints[seed].weights,
                batch,
                episode_index,
                core,
                MAXIMUM_SUFFIX_HORIZON,
            )
            episode_records.append(record)
            context = context_index[(seed, episode_index)]
            native, incoming, codes, maps = entry.incoming_representatives(
                checkpoints[seed].weights,
                batch.tables[episode_index],
                batch.maps[episode_index],
                batch.canonical_to_slot[episode_index],
                core,
            )
            del native
            q_dagger = (np.arange(8, dtype=np.int64) + 1) % 8
            declared_q = np.arange(8, dtype=np.int64)
            route_records: list[dict[str, Any]] = []
            for route, name in enumerate(("incoming_R", "incoming_F")):
                decoy_states = incoming[route, q_dagger]
                locators = [
                    {
                        "declared_semantic": int(q),
                        "actual_decoy_semantic": int(q_dagger[q]),
                        "incoming_route": name,
                    }
                    for q in range(8)
                ]
                audit = engine.audit_states(
                    context.suffix_bank,
                    codes,
                    maps,
                    checkpoints[seed].weights.decoder,
                    decoy_states,
                    q_dagger,
                    case_locators=locators,
                )
                declared_targets = context.suffix_bank.semantic_actions[:, declared_q].T
                declared_match_count = int(np.sum(audit.predictions == declared_targets))
                route_records.append(
                    {
                        "route": name,
                        "declared_semantic_rule": "q",
                        "actual_decoy_semantic_rule": "(q+1) mod 8",
                        "true_decoy_target_match_count": int(
                            np.sum(audit.predictions == audit.targets)
                        ),
                        "declared_q_target_match_count": declared_match_count,
                        "follows_decoy_and_never_declared_q": bool(
                            audit.summary["all_cases_survive"]
                            and declared_match_count == 0
                        ),
                        "audit": compact_audit(audit.summary),
                    }
                )
            decoy_episode_records.append(
                {
                    "checkpoint_seed": seed,
                    "episode_seed": context.episode_seed,
                    "episode_index": episode_index,
                    "routes": route_records,
                }
            )
        seed_records[str(seed)] = {
            "checkpoint_seed": seed,
            "checkpoint_sha256": checkpoints[seed].sha256,
            "episode_seed": int(source["episode_seed"]),
            "episodes": episode_records,
        }
        progress(f"entry module completed checkpoint {seed}")

    aggregate = entry.aggregate_results(seed_records, MAXIMUM_SUFFIX_HORIZON)
    decoy_routes = [
        route for episode in decoy_episode_records for route in episode["routes"]
    ]
    decoy_decisions = sum(route["audit"]["decision_count"] for route in decoy_routes)
    if decoy_decisions != 2 * 8 * 511 * 16:
        raise ArithmeticError("entry decoy decision count changed")
    integrity_gates = {
        "E0_source_input_and_numeric_integrity": True,
    }
    diagnostic_predicates = {
        "E1_anchor_defect_confined_to_registered_empty_suffix": bool(
            aggregate["gates"]["I0_known_seed0_defect_confined_to_empty_suffix"]
        ),
        "E2_both_uniform_reanchoring_routes_repair_without_regression": bool(
            aggregate["gates"]["R0_uniform_R_reanchor_repairs_without_hard_regression"]
            and aggregate["gates"]["F0_uniform_F_reanchor_repairs_without_hard_regression"]
        ),
        "E3_incoming_routes_share_hard_continuation_signatures": bool(
            aggregate["gates"]["P0_incoming_routes_have_identical_hard_signatures"]
        ),
        "E4_wrong_semantic_decoys_redirect_specifically": bool(
            all(route["follows_decoy_and_never_declared_q"] for route in decoy_routes)
        ),
    }
    return {
        "design": {
            "suffix_horizon": 8,
            "suffix_count_per_state": 511,
            "native_and_incoming_decision_count": 196224,
            "decoy_decision_count": decoy_decisions,
            "total_decision_count": 196224 + decoy_decisions,
        },
        "seeds": seed_records,
        "decoys": decoy_episode_records,
        "aggregate": aggregate,
        "integrity_gates": integrity_gates,
        "diagnostic_predicates": diagnostic_predicates,
    }


def run_cone_module(contexts: Sequence[EpisodeContext]) -> dict[str, Any]:
    episode_records: list[dict[str, Any]] = []
    all_terminal_cells: list[dict[str, Any]] = []
    recursive_passes: list[bool] = []
    for context in contexts:
        levels, semantics = engine.build_history_levels(
            context.canonical_codes,
            context.canonical_maps,
            context.weights.state_embedding,
            MAXIMUM_HISTORY_DEPTH,
        )
        cells: list[dict[str, Any]] = []
        history_state_count = 0
        for history_depth in range(1, MAXIMUM_HISTORY_DEPTH + 1):
            locators = engine.history_case_locators(history_depth)
            audit = engine.audit_states(
                context.suffix_bank,
                context.canonical_codes,
                context.canonical_maps,
                context.weights.decoder,
                levels[history_depth],
                semantics[history_depth],
                case_locators=locators,
            )
            recursive_passes.append(
                bool(audit.summary["recursive_suffix_consistency"]["passed"])
            )
            history_state_count += levels[history_depth].shape[0]
            for horizon in range(MAXIMUM_SUFFIX_HORIZON + 1):
                cell = engine.summarize_audit_horizon(
                    audit, context.suffix_bank, horizon, locators
                )
                cell["L"] = history_depth
                cell["all_states_strictly_safe"] = bool(
                    cell["safe_case_count"] == cell["case_count"]
                )
                cells.append(cell)
                if horizon == MAXIMUM_SUFFIX_HORIZON:
                    all_terminal_cells.append(
                        {
                            "checkpoint_seed": context.checkpoint_seed,
                            "episode_index": context.episode_index,
                            **cell,
                        }
                    )
            del audit
        logical_decisions = sum(
            cell["decision_count"]
            for cell in cells
            if cell["H"] == MAXIMUM_SUFFIX_HORIZON
        )
        if history_state_count != 4080 or logical_decisions != 2_084_880:
            raise ArithmeticError("registered cone domain count changed")
        terminal = [cell for cell in cells if cell["H"] == 8]
        episode_records.append(
            {
                "checkpoint_seed": context.checkpoint_seed,
                "episode_seed": context.episode_seed,
                "episode_index": context.episode_index,
                "history_state_count": history_state_count,
                "logical_decision_count": logical_decisions,
                "minimum_pulled_back_facet_norm": (
                    context.suffix_bank.minimum_pulled_back_facet_norm
                ),
                "all_registered_states_strictly_safe": bool(
                    all(cell["all_states_strictly_safe"] for cell in terminal)
                ),
                "minimum_angular_clearance": min(
                    cell["minimum_angular_clearance"] for cell in terminal
                ),
                "cells": cells,
            }
        )
        progress(
            f"cone module completed checkpoint {context.checkpoint_seed}, "
            f"episode {context.episode_index}"
        )
        del levels, semantics
        gc.collect()

    weakest = min(
        all_terminal_cells, key=lambda cell: cell["minimum_angular_clearance"]
    )
    total_decisions = sum(record["logical_decision_count"] for record in episode_records)
    if total_decisions != 33_358_080:
        raise ArithmeticError("registered total cone decision count changed")
    integrity_gates = {
        "K1_direct_and_recursive_suffix_audits_agree": bool(all(recursive_passes)),
    }
    diagnostic_predicates = {
        "K0_all_observed_recurrent_states_survive_H8": bool(
            all(record["all_registered_states_strictly_safe"] for record in episode_records)
        ),
        "K2_all_angular_clearances_exceed_1e_minus_10": bool(
            weakest["minimum_angular_clearance"] > ROBUST_CLEARANCE
        ),
    }
    return {
        "design": {
            "history_depths": list(range(1, 9)),
            "suffix_horizons": list(range(9)),
            "history_state_count": 4080 * 16,
            "logical_decision_count": total_decisions,
        },
        "episodes": episode_records,
        "aggregate": {
            "global_minimum_angular_clearance": weakest[
                "minimum_angular_clearance"
            ],
            "global_weakest_facet": {
                "checkpoint_seed": weakest["checkpoint_seed"],
                "episode_index": weakest["episode_index"],
                **weakest["minimum_angular_clearance_witness"],
            },
        },
        "integrity_gates": integrity_gates,
        "diagnostic_predicates": diagnostic_predicates,
    }


def _relation_primitive_record(
    context: EpisodeContext, relation: str, word: tuple[int, ...]
) -> tuple[np.ndarray, dict[str, Any]]:
    action = holonomy.semantic_word_action(
        context.canonical_maps, np.arange(8, dtype=np.int64), word
    )
    if not np.array_equal(action, np.arange(8)):
        raise ArithmeticError(f"registered relation {relation} is not semantic identity")
    product_matrix = holonomy.word_product(context.canonical_codes, word)
    frobenius = float(np.linalg.norm(product_matrix, ord="fro"))
    if frobenius <= 0.0 or not np.isfinite(frobenius):
        raise ArithmeticError("relation product has no finite positive matrix ray")
    return product_matrix, {
        "relation": relation,
        "word": list(word),
        "identity_semantic_action": True,
        "raw_product_frobenius_norm": frobenius,
        "positive_rescaled_product": (product_matrix / frobenius).tolist(),
        "nearest_positive_scalar_identity": holonomy.nearest_positive_scalar_identity(
            product_matrix
        ),
        "eigenspectrum": holonomy.eigenspectrum(product_matrix),
    }


def run_relation_module(contexts: Sequence[EpisodeContext]) -> dict[str, Any]:
    episode_records: list[dict[str, Any]] = []
    event_index: list[dict[str, Any]] = []
    maximum_unit_l2 = 0.0
    maximum_angle = 0.0
    baseline_integrity: list[bool] = []
    eligible_case_counts: list[int] = []
    for context in contexts:
        base_audit = engine.audit_states(
            context.suffix_bank,
            context.canonical_codes,
            context.canonical_maps,
            context.weights.decoder,
            context.base_states,
            context.base_semantic,
            case_locators=context.base_locators,
        )
        eligible_cases = np.all(base_audit.strict, axis=1)
        all_cases_eligible = bool(np.all(eligible_cases))
        baseline_integrity.append(all_cases_eligible)
        eligible_case_counts.append(int(np.sum(eligible_cases)))
        relations: list[dict[str, Any]] = []
        primitive_products: dict[str, np.ndarray] = {}
        for relation, word in RELATIONS.items():
            product_matrix, primitive = _relation_primitive_record(
                context, relation, word
            )
            primitive_products[relation] = product_matrix
            repeats: list[dict[str, Any]] = []
            for repeat_count in REPEAT_GRIDS[relation]:
                comparison = holonomy.compare_generator_and_block_execution(
                    context.canonical_codes,
                    context.base_states,
                    word,
                    repeat_count,
                )
                maximum_unit_l2 = max(
                    maximum_unit_l2, comparison["maximum_unit_l2"]
                )
                maximum_angle = max(
                    maximum_angle, comparison["maximum_positive_ray_angle"]
                )
                loop_states = comparison["generator_state"]
                audit = engine.audit_states(
                    context.suffix_bank,
                    context.canonical_codes,
                    context.canonical_maps,
                    context.weights.decoder,
                    loop_states,
                    context.base_semantic,
                    baseline_states=context.base_states,
                    case_locators=context.base_locators,
                )
                geometry = holonomy.positive_ray_geometry(
                    loop_states, context.base_states
                )
                power = holonomy.positive_rescaled_matrix_power(
                    product_matrix, repeat_count
                )
                compact = compact_audit(audit.summary)
                eligible_audit = _eligible_relation_audit(
                    audit, eligible_cases, context.suffix_bank
                )
                repeats.append(
                    {
                        "repeat_count": repeat_count,
                        "inserted_token_budget": repeat_count * len(word),
                        "all_base_cases_eligible": all_cases_eligible,
                        "eligible_baseline_case_count": int(
                            eligible_audit["eligible_case_count"]
                        ),
                        "generator_vs_grouped_maximum_unit_l2": comparison[
                            "maximum_unit_l2"
                        ],
                        "generator_vs_grouped_maximum_positive_ray_angle": comparison[
                            "maximum_positive_ray_angle"
                        ],
                        "loop_vs_baseline_maximum_positive_ray_angle": float(
                            np.max(geometry["angle"])
                        ),
                        "loop_vs_baseline_mean_positive_ray_angle": float(
                            np.mean(geometry["angle"])
                        ),
                        "audit": compact,
                        "eligible_case_audit": eligible_audit,
                        "repeated_composite": {
                            "nearest_positive_scalar_identity": (
                                holonomy.nearest_positive_scalar_identity(power)
                            ),
                            "eigenspectrum": holonomy.eigenspectrum(power),
                        },
                    }
                )
                if (
                    repeat_count > 0
                    and eligible_audit["eligible_case_count"] > 0
                    and eligible_audit["failure_case_count"] > 0
                ):
                    event_index.append(
                        {
                            "checkpoint_seed": context.checkpoint_seed,
                            "episode_index": context.episode_index,
                            "episode_half": "first" if context.episode_index < 4 else "second",
                            "relation": relation,
                            "repeat_count": repeat_count,
                            "inserted_token_budget": repeat_count * len(word),
                            "eligible_baseline_case_count": eligible_audit[
                                "eligible_case_count"
                            ],
                            "excluded_baseline_case_count": eligible_audit[
                                "excluded_case_count"
                            ],
                            "failure_case_count": eligible_audit[
                                "failure_case_count"
                            ],
                            "reveal_case_count": eligible_audit[
                                "reveal_case_count"
                            ],
                            "first_failure_histogram": eligible_audit[
                                "first_failure_histogram"
                            ],
                            "first_reveal_histogram": eligible_audit[
                                "first_reveal_histogram"
                            ],
                        }
                    )
            relations.append({"primitive": primitive, "repeats": repeats})
            progress(
                f"relation {relation} completed checkpoint {context.checkpoint_seed}, "
                f"episode {context.episode_index}"
            )
        frfr_poly = np.poly(primitive_products["frfr"])
        rfrf_poly = np.poly(primitive_products["rfrf"])
        coefficient_scale = float(
            max(np.max(np.abs(frfr_poly)), np.max(np.abs(rfrf_poly)))
        )
        common_matrix_scale = float(
            max(
                np.linalg.norm(primitive_products["frfr"], ord="fro"),
                np.linalg.norm(primitive_products["rfrf"], ord="fro"),
            )
        )
        if coefficient_scale <= 0.0 or common_matrix_scale <= 0.0:
            raise ArithmeticError("frfr/rfrf comparison scale is not positive")
        scaled_frfr_poly = np.poly(
            primitive_products["frfr"] / common_matrix_scale
        )
        scaled_rfrf_poly = np.poly(
            primitive_products["rfrf"] / common_matrix_scale
        )
        episode_records.append(
            {
                "checkpoint_seed": context.checkpoint_seed,
                "episode_seed": context.episode_seed,
                "episode_index": context.episode_index,
                "baseline_eligibility": compact_audit(base_audit.summary),
                "frfr_rfrf_characteristic_polynomial_max_abs_difference": float(
                    np.max(np.abs(frfr_poly - rfrf_poly))
                ),
                "frfr_rfrf_characteristic_polynomial_relative_max_difference": float(
                    np.max(np.abs(frfr_poly - rfrf_poly)) / coefficient_scale
                ),
                "frfr_rfrf_common_frobenius_scaled_characteristic_polynomial_max_abs_difference": float(
                    np.max(np.abs(scaled_frfr_poly - scaled_rfrf_poly))
                ),
                "frfr_rfrf_common_frobenius_scale": common_matrix_scale,
                "relations": relations,
            }
        )
        gc.collect()

    relation_configuration_count = sum(
        len(record["repeats"])
        for episode in episode_records
        for record in episode["relations"]
    )
    if relation_configuration_count != 16 * 84:
        raise ArithmeticError("registered relation configuration count changed")
    delayed = any(
        any(
            int(depth) > 0 and count > 0
            for depth, count in (event["first_reveal_histogram"] or {}).items()
            if depth != "none"
        )
        for event in event_index
    )
    exit_seeds = {event["checkpoint_seed"] for event in event_index}
    exit_halves = {event["episode_half"] for event in event_index}
    any_exit = bool(event_index)
    total_eligible_cases = sum(eligible_case_counts)
    replicated_exit_cells = _replicated_exit_cells(event_index)
    integrity_gates = {
        "P0_grouped_products_reproduce_stepwise_rays": bool(
            maximum_unit_l2 <= RAY_TOLERANCE and maximum_angle <= RAY_TOLERANCE
        ),
        "B0_all_base_transversal_cases_are_H8_eligible": bool(
            all(baseline_integrity)
        ),
    }
    raw_diagnostic_predicates = {
        "H0_no_registered_long_path_cone_exit": bool(
            total_eligible_cases > 0 and not any_exit
        ),
        "H1_at_least_one_fresh_cone_exit_by_64_tokens": any_exit,
        "H2_same_relation_repeat_exit_in_all_checkpoint_half_strata": bool(
            replicated_exit_cells
        ),
        "H3_at_least_one_delayed_hard_reveal": bool(delayed),
    }
    relation_predicates_valid = bool(integrity_gates[
        "B0_all_base_transversal_cases_are_H8_eligible"
    ])
    diagnostic_predicates = _condition_diagnostic_predicates(
        raw_diagnostic_predicates, relation_predicates_valid
    )
    return {
        "design": {
            "relations": {name: list(word) for name, word in RELATIONS.items()},
            "repeat_grids": {name: list(grid) for name, grid in REPEAT_GRIDS.items()},
            "base_cases_per_episode": 64,
            "suffix_count_per_case": 511,
            "relation_configuration_count": relation_configuration_count,
            "logical_decision_count": relation_configuration_count * 64 * 511,
        },
        "episodes": episode_records,
        "exit_event_index": event_index,
        "aggregate": {
            "maximum_generator_vs_grouped_unit_l2": maximum_unit_l2,
            "maximum_generator_vs_grouped_positive_ray_angle": maximum_angle,
            "fresh_exit_configuration_count": len(event_index),
            "eligible_base_case_count": total_eligible_cases,
            "registered_base_case_count": 16 * 64,
            "checkpoint_seeds_with_exit": sorted(exit_seeds),
            "episode_halves_with_exit": sorted(exit_halves),
            "H2_qualifying_relation_repeat_cells": replicated_exit_cells,
        },
        "diagnostic_validity": {
            "condition": "B0_all_base_transversal_cases_are_H8_eligible",
            "valid": relation_predicates_valid,
            "invalid_value_encoding": None,
        },
        "integrity_gates": integrity_gates,
        "raw_diagnostic_predicates": raw_diagnostic_predicates,
        "diagnostic_predicates": diagnostic_predicates,
    }


def _condition_id(relation: str, budget: int, role: str, endpoint: str) -> str:
    return f"{relation}:B{budget}:{role}:{endpoint}"


def _word_id(word: tuple[int, ...]) -> str:
    payload = json.dumps(list(word), separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()[:20]


def matched_condition_index(bank: Mapping[str, Any]) -> list[dict[str, Any]]:
    conditions: list[dict[str, Any]] = []
    for record in bank["records"]:
        relation = str(record["relation"])
        budget = int(record["budget"])
        reference = tuple(map(int, record["reference_word"]))
        conditions.append(
            {
                "condition_id": _condition_id(relation, budget, "reference", "e"),
                "relation": relation,
                "budget": budget,
                "role": "reference",
                "endpoint_index": 0,
                "endpoint_name": "e",
                "word_id": _word_id(reference),
                "word": list(reference),
                "reference_features": record["reference_features"],
            }
        )
        for control in record["exact_length_controls"]:
            word = tuple(map(int, control["word"]))
            endpoint_name = str(control["target_endpoint_name"])
            conditions.append(
                {
                    "condition_id": _condition_id(
                        relation, budget, "control", endpoint_name
                    ),
                    "relation": relation,
                    "budget": budget,
                    "role": "control",
                    "endpoint_index": int(control["target_endpoint_index"]),
                    "endpoint_name": endpoint_name,
                    "word_id": _word_id(word),
                    "word": list(word),
                    "matching": control["matching"],
                    "features": control["features"],
                }
            )
    if len(conditions) != 60 or len({item["condition_id"] for item in conditions}) != 60:
        raise ArithmeticError("matched condition index count changed")
    return conditions


def _combine_audit_units(units: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if not units:
        raise ValueError("cannot combine an empty audit unit list")
    failure_count = sum(int(unit["failure_case_count"]) for unit in units)
    reveal_count = sum(int(unit["reveal_case_count"] or 0) for unit in units)
    minimum_margin = min(float(unit["minimum_target_margin"]) for unit in units)
    minimum_clearance = min(float(unit["minimum_angular_clearance"]) for unit in units)
    return {
        "episode_count": len(units),
        "case_count": sum(int(unit["case_count"]) for unit in units),
        "decision_count": sum(int(unit["decision_count"]) for unit in units),
        "strict_error_count": sum(int(unit["strict_error_count"]) for unit in units),
        "failure_case_count": failure_count,
        "reveal_case_count": reveal_count,
        "minimum_target_margin": minimum_margin,
        "minimum_angular_clearance": minimum_clearance,
        "severity": [failure_count, reveal_count, -minimum_margin],
    }


def _severity(record: Mapping[str, Any]) -> tuple[float, float, float]:
    return tuple(map(float, record["severity"]))  # type: ignore[return-value]


def _condition_diagnostic_predicates(
    raw_predicates: Mapping[str, bool], precondition_valid: bool
) -> dict[str, bool | None]:
    return {
        str(name): bool(value) if precondition_valid else None
        for name, value in raw_predicates.items()
    }


def run_matched_module(
    contexts: Sequence[EpisodeContext], bank: Mapping[str, Any]
) -> dict[str, Any]:
    conditions = matched_condition_index(bank)
    condition_lookup = {item["condition_id"]: item for item in conditions}
    units: dict[tuple[int, str], list[dict[str, Any]]] = {}
    pair_units: dict[tuple[int, str, int], list[dict[str, Any]]] = {}
    episode_records: list[dict[str, Any]] = []
    all_baselines_eligible = True
    for context in contexts:
        relevant_endpoints = (0, 2, 5, 7)
        baseline_records: dict[str, Any] = {}
        for endpoint in relevant_endpoints:
            baseline_audit = engine.audit_states(
                context.suffix_bank,
                context.canonical_codes,
                context.canonical_maps,
                context.weights.decoder,
                context.baseline_states_by_endpoint[endpoint],
                context.baseline_semantic_by_endpoint[endpoint],
                case_locators=context.base_locators,
            )
            baseline_records[str(endpoint)] = compact_audit(baseline_audit.summary)
            all_baselines_eligible = bool(
                all_baselines_eligible and baseline_audit.summary["all_cases_survive"]
            )

        cache: dict[tuple[int, ...], tuple[engine.AuditResult, np.ndarray, int, dict[str, Any]]] = {}
        path_results: dict[str, Any] = {}
        aliases: list[dict[str, str]] = []
        for condition in conditions:
            word = tuple(map(int, condition["word"]))
            endpoint = int(condition["endpoint_index"])
            if word not in cache:
                if matched.endpoint_index(word) != endpoint:
                    raise ArithmeticError("matched word endpoint changed")
                states = holonomy.apply_word_ray(
                    context.canonical_codes, context.base_states, word
                )
                labels = holonomy.semantic_word_action(
                    context.canonical_maps, context.base_semantic, word
                )
                if not np.array_equal(
                    labels, context.baseline_semantic_by_endpoint[endpoint]
                ):
                    raise ArithmeticError("long path and shallow baseline semantics disagree")
                audit = engine.audit_states(
                    context.suffix_bank,
                    context.canonical_codes,
                    context.canonical_maps,
                    context.weights.decoder,
                    states,
                    labels,
                    baseline_states=context.baseline_states_by_endpoint[endpoint],
                    case_locators=context.base_locators,
                )
                geometry = holonomy.positive_ray_geometry(
                    states, context.baseline_states_by_endpoint[endpoint]
                )
                geometric = {
                    "maximum_positive_ray_angle": float(np.max(geometry["angle"])),
                    "mean_positive_ray_angle": float(np.mean(geometry["angle"])),
                    "maximum_unit_l2": float(np.max(geometry["unit_l2"])),
                }
                cache[word] = (audit, states, endpoint, geometric)
                word_identifier = _word_id(word)
                existing = path_results.get(word_identifier)
                if existing is not None and existing["word"] != list(word):
                    raise ArithmeticError("truncated word identifier collision")
                path_results[word_identifier] = {
                    "word": list(word),
                    "length": len(word),
                    "endpoint_index": endpoint,
                    "endpoint_name": matched.ENDPOINT_NAMES[endpoint],
                    "same_endpoint_shallow_baseline_geometry": geometric,
                    "audit": compact_audit(audit.summary),
                }
            audit, _states, cached_endpoint, _geometry = cache[word]
            if cached_endpoint != endpoint:
                raise ArithmeticError("word cache endpoint mismatch")
            compact = compact_audit(audit.summary)
            units.setdefault(
                (context.checkpoint_seed, str(condition["condition_id"])), []
            ).append(compact)
            aliases.append(
                {
                    "condition_id": str(condition["condition_id"]),
                    "word_id": str(condition["word_id"]),
                }
            )

        direct_pairs: list[dict[str, Any]] = []
        for relation in RELATIONS:
            for budget in (16, 32, 64):
                reference_id = _condition_id(relation, budget, "reference", "e")
                identity_id = _condition_id(relation, budget, "control", "e")
                reference_word = tuple(condition_lookup[reference_id]["word"])
                identity_word = tuple(condition_lookup[identity_id]["word"])
                reference_audit, reference_states, _, _ = cache[reference_word]
                identity_audit, identity_states, _, _ = cache[identity_word]
                different = reference_audit.predictions != identity_audit.predictions
                geometry = holonomy.positive_ray_geometry(
                    reference_states, identity_states
                )
                pair = {
                    "relation": relation,
                    "budget": budget,
                    "reference_condition_id": reference_id,
                    "identity_control_condition_id": identity_id,
                    "hard_signature_equal": bool(not np.any(different)),
                    "hard_decision_difference_count": int(np.sum(different)),
                    "hard_signature_different_case_count": int(
                        np.sum(np.any(different, axis=1))
                    ),
                    "first_difference_histogram": _first_event_histogram(
                        different, context.suffix_bank
                    ),
                    "maximum_positive_ray_angle": float(np.max(geometry["angle"])),
                    "mean_positive_ray_angle": float(np.mean(geometry["angle"])),
                    "difference_mask_sha256": hashlib.sha256(
                        different.tobytes(order="C")
                    ).hexdigest(),
                }
                direct_pairs.append(pair)
                pair_units.setdefault(
                    (context.checkpoint_seed, relation, budget), []
                ).append(pair)
        episode_records.append(
            {
                "checkpoint_seed": context.checkpoint_seed,
                "episode_seed": context.episode_seed,
                "episode_index": context.episode_index,
                "baseline_eligibility_by_endpoint": baseline_records,
                "unique_word_count": len(cache),
                "path_results": path_results,
                "condition_aliases": aliases,
                "direct_reference_vs_identity_control": direct_pairs,
            }
        )
        progress(
            f"matched controls completed checkpoint {context.checkpoint_seed}, "
            f"episode {context.episode_index}; {len(cache)} unique words"
        )
        del cache
        gc.collect()

    checkpoint_cells: list[dict[str, Any]] = []
    combined: dict[tuple[int, str], dict[str, Any]] = {
        key: _combine_audit_units(value) for key, value in units.items()
    }
    cell_flags: dict[tuple[int, str, int], dict[str, bool]] = {}
    for seed in (0, 1):
        for relation in RELATIONS:
            for budget in (16, 32, 64):
                reference_id = _condition_id(relation, budget, "reference", "e")
                identity_id = _condition_id(relation, budget, "control", "e")
                nonidentity_ids = [
                    _condition_id(relation, budget, "control", endpoint)
                    for endpoint in ("R2", "FR", "FR3")
                ]
                reference = combined[(seed, reference_id)]
                identity = combined[(seed, identity_id)]
                nonidentity = {
                    condition_id: combined[(seed, condition_id)]
                    for condition_id in nonidentity_ids
                }
                pair_rows = pair_units[(seed, relation, budget)]
                pair_difference_count = sum(
                    int(row["hard_decision_difference_count"]) for row in pair_rows
                )
                flags = {
                    "identity_paths_hard_differ": pair_difference_count > 0,
                    "reference_more_severe_than_identity_control": (
                        _severity(reference) > _severity(identity)
                    ),
                    "identity_control_more_severe_than_reference": (
                        _severity(identity) > _severity(reference)
                    ),
                    "some_nonidentity_control_more_severe_than_reference": any(
                        _severity(value) > _severity(reference)
                        for value in nonidentity.values()
                    ),
                    "reference_more_severe_than_all_nonidentity_controls": all(
                        _severity(reference) > _severity(value)
                        for value in nonidentity.values()
                    ),
                }
                cell_flags[(seed, relation, budget)] = flags
                checkpoint_cells.append(
                    {
                        "checkpoint_seed": seed,
                        "relation": relation,
                        "budget": budget,
                        "reference": reference,
                        "identity_control": identity,
                        "nonidentity_controls": nonidentity,
                        "direct_reference_vs_identity_decision_difference_count": (
                            pair_difference_count
                        ),
                        "raw_flags": flags,
                    }
                )

    block_keys = [(relation, budget) for relation in RELATIONS for budget in (16, 32, 64)]
    x0_cells: list[dict[str, Any]] = []
    x1_cells: list[dict[str, Any]] = []
    x2_cells: list[dict[str, Any]] = []
    x3_cells: list[dict[str, Any]] = []
    for relation, budget in block_keys:
        # X0 requires the same nonidentity endpoint to be worse in both seeds.
        same_endpoint_generic = False
        for endpoint in ("R2", "FR", "FR3"):
            control_id = _condition_id(relation, budget, "control", endpoint)
            reference_id = _condition_id(relation, budget, "reference", "e")
            if all(
                _severity(combined[(seed, control_id)])
                > _severity(combined[(seed, reference_id)])
                for seed in (0, 1)
            ):
                same_endpoint_generic = True
        if same_endpoint_generic:
            x0_cells.append({"relation": relation, "budget": budget})
        if all(
            cell_flags[(seed, relation, budget)]["identity_paths_hard_differ"]
            for seed in (0, 1)
        ):
            x1_cells.append({"relation": relation, "budget": budget})
        if all(
            cell_flags[(seed, relation, budget)][
                "reference_more_severe_than_identity_control"
            ]
            for seed in (0, 1)
        ):
            x2_cells.append({"relation": relation, "budget": budget})
        if all(
            cell_flags[(seed, relation, budget)][
                "reference_more_severe_than_all_nonidentity_controls"
            ]
            for seed in (0, 1)
        ):
            x3_cells.append({"relation": relation, "budget": budget})

    logical_decisions = 16 * 60 * 64 * 511
    direct_comparisons = 16 * 12 * 64 * 511
    m0_valid = bool(all_baselines_eligible)
    m1_valid = bool(
        len(conditions) == 60
        and all(record["unique_word_count"] == 54 for record in episode_records)
    )
    classification_valid = bool(m0_valid and m1_valid)
    for cell in checkpoint_cells:
        cell["classification_valid_under_M0_and_M1"] = classification_valid
    integrity_gates = {
        "M0_all_same_endpoint_shallow_baselines_are_H8_eligible": m0_valid,
        "M1_exact_12_plus_48_bank_executed": m1_valid,
    }
    raw_diagnostic_predicates = {
        "X0_replicated_nonidentity_control_excess": bool(x0_cells),
        "X1_finite_pair_identity_path_hard_signature_difference": bool(x1_cells),
        "X2_finite_pair_relator_reference_severity_dominance": bool(x2_cells),
        "X3_reference_over_all_nonidentity_controls_dominance": bool(x3_cells),
        "X4_mixed_finite_comparison_pattern": bool(
            x0_cells and (x2_cells or x3_cells)
        ),
    }
    diagnostic_predicates = _condition_diagnostic_predicates(
        raw_diagnostic_predicates, classification_valid
    )
    raw_classification_cells = {
        "X0": x0_cells,
        "X1": x1_cells,
        "X2": x2_cells,
        "X3": x3_cells,
    }
    return {
        "design": {
            "reference_count": 12,
            "exact_length_control_count": 48,
            "condition_count": 60,
            "distinct_word_count": 54,
            "reused_condition_alias_count": 6,
            "directed_reference_identity_comparison_count": 12,
            "unique_unordered_reference_identity_pair_count": 9,
            "parity_sandwich_materialized": False,
            "base_cases_per_episode": 64,
            "suffix_count_per_case": 511,
            "logical_path_decision_count": logical_decisions,
            "direct_identity_pair_decision_comparison_count": direct_comparisons,
            "severity_order": [
                "failure_case_count",
                "reveal_case_count",
                "negative_minimum_target_margin",
            ],
        },
        "condition_index": conditions,
        "episodes": episode_records,
        "checkpoint_cells": checkpoint_cells,
        "classification_validity": {
            "condition": (
                "M0_all_same_endpoint_shallow_baselines_are_H8_eligible and "
                "M1_exact_12_plus_48_bank_executed"
            ),
            "valid": classification_valid,
            "invalid_value_encoding": None,
        },
        "raw_classification_cells": raw_classification_cells,
        "classification_cells": (
            raw_classification_cells if classification_valid else None
        ),
        "integrity_gates": integrity_gates,
        "raw_diagnostic_predicates": raw_diagnostic_predicates,
        "diagnostic_predicates": diagnostic_predicates,
    }


def _validate_lineage() -> dict[str, Any]:
    path = ROOT / "results" / "LINEAGE_REGRESSION.json"
    value = load_json(path)
    if not bool(value.get("passed")):
        raise ValueError("inherited v0.2.1 lineage regression did not pass")
    for seed in ("0", "1"):
        record = value.get("seeds", {}).get(seed, {})
        if (
            int(record.get("decision_count", -1)) != 61_440
            or float(record.get("semantic_continuation_accuracy", -1.0)) != 1.0
            or int(record.get("maximum_split_multiplicity", -1)) != 1
            or int(record.get("maximum_merge_multiplicity", -1)) != 1
            or not bool(record.get("passed"))
        ):
            raise ValueError(f"lineage regression mismatch for checkpoint {seed}")
    return {
        "passed": True,
        "path": str(path),
        "sha256": checkpoint_io.file_sha256(path),
    }


def run_registered() -> dict[str, Any]:
    if not _BOOTSTRAP_AUTHENTICATED:
        raise RuntimeError(
            "run_registered is available only through the authenticated "
            "direct CLI execution path"
        )
    started_wall = utc_now()
    started = time.perf_counter()
    _refuse_existing_execution_artifacts()
    runtime_validation = _validate_runtime_contract()
    _validate_module_locations()
    freeze_validation = freeze.validate_execution_freeze(
        HERE / "V031_EXECUTION_FREEZE.json", ROOT
    )
    prereg_validation = freeze.validate_preregistration(
        HERE / "V031_PREREGISTRATION.json"
    )
    frozen_input_validation = freeze.validate_frozen_inputs(
        HERE / "V031_FROZEN_INPUTS.json"
    )
    word_bank_validation = freeze.validate_matched_word_bank(
        HERE / "V031_MATCHED_WORD_BANK.json"
    )
    lineage_validation = _validate_lineage()
    input_payload = load_json(HERE / "V031_FROZEN_INPUTS.json")
    bank = load_json(HERE / "V031_MATCHED_WORD_BANK.json")
    progress("global freeze, fresh inputs, matched bank, and inherited lineage validated")

    if os.environ.get("KOMOREBI_V031_PREENDPOINT_STRUCTURAL_ONLY") == "1":
        raise RuntimeError(
            "learned checkpoint loading is forbidden under the preendpoint "
            "structural-only guard"
        )
    run_started_validation = _create_run_started_ledger(freeze_validation)
    progress("irreversible run-start ledger created before checkpoint loading")

    checkpoints: dict[int, Any] = {}
    for seed in (0, 1):
        path = ROOT / "checkpoints" / f"projective_terminal_seed{seed}.pt"
        checkpoint = checkpoint_io.load_checkpoint(path, CHECKPOINT_DIGESTS[seed])
        if int(checkpoint.metadata.get("config", {}).get("seed", -1)) != seed:
            raise ValueError(f"checkpoint metadata seed mismatch for seed {seed}")
        checkpoints[seed] = checkpoint
    progress("restricted checkpoint loading completed")

    contexts = build_contexts(checkpoints, input_payload)
    entry_results = run_entry_module(checkpoints, contexts, input_payload)
    progress("entry module complete")
    cone_results = run_cone_module(contexts)
    progress("finite observed-state cone module complete")
    relation_results = run_relation_module(contexts)
    progress("dense relation and spectroscopy module complete")
    matched_results = run_matched_module(contexts, bank)
    progress("matched-control module complete")

    integrity_gates = {
        "lineage_integrity": True,
        **entry_results["integrity_gates"],
        **cone_results["integrity_gates"],
        **relation_results["integrity_gates"],
        **matched_results["integrity_gates"],
    }
    diagnostic_predicates = {
        **entry_results["diagnostic_predicates"],
        **cone_results["diagnostic_predicates"],
        **relation_results["diagnostic_predicates"],
        **matched_results["diagnostic_predicates"],
    }
    entry_localized = bool(
        all(entry_results["integrity_gates"].values())
        and all(entry_results["diagnostic_predicates"].values())
    )
    cone_safe = bool(
        cone_results["integrity_gates"][
            "K1_direct_and_recursive_suffix_audits_agree"
        ]
        and cone_results["diagnostic_predicates"][
            "K0_all_observed_recurrent_states_survive_H8"
        ]
    )
    cone_robust = bool(
        cone_safe
        and cone_results["diagnostic_predicates"][
            "K2_all_angular_clearances_exceed_1e_minus_10"
        ]
    )
    relation_valid = bool(all(relation_results["integrity_gates"].values()))
    long_path_exit = bool(
        relation_valid
        and relation_results["diagnostic_predicates"][
            "H1_at_least_one_fresh_cone_exit_by_64_tokens"
        ]
    )
    preregistered_composites = {
        "entry_localized_finite": entry_localized,
        "finite_observed_cone_safe": cone_safe,
        "finite_observed_cone_robust": cone_robust,
        "registered_long_path_exit": long_path_exit,
        "registered_broadly_replicated_long_path_exit": bool(
            long_path_exit
            and relation_results["diagnostic_predicates"][
                "H2_same_relation_repeat_exit_in_all_checkpoint_half_strata"
            ]
        ),
        "registered_delayed_reveal": bool(
            long_path_exit
            and relation_results["diagnostic_predicates"][
                "H3_at_least_one_delayed_hard_reveal"
            ]
        ),
        "matched_panel_interpretable": bool(
            all(matched_results["integrity_gates"].values())
        ),
        "full_finite_factorization": bool(
            entry_localized and cone_safe and long_path_exit
        ),
    }
    elapsed = time.perf_counter() - started
    return {
        "schema": "komorebi.neuralese.entry_cone_holonomy.result.v1",
        "version": VERSION,
        "author": AUTHOR,
        "status": "REGISTERED_EXECUTION_COMPLETE",
        "scientific_class": "prospectively_frozen_adaptive_developmental_diagnostic",
        "integrity": {
            "runtime_contract": runtime_validation,
            "run_started_ledger": run_started_validation,
            "execution_freeze": freeze_validation,
            "preregistration": prereg_validation,
            "frozen_inputs": frozen_input_validation,
            "matched_word_bank": word_bank_validation,
            "lineage": lineage_validation,
            "checkpoint_sha256": {
                str(seed): checkpoints[seed].sha256 for seed in (0, 1)
            },
        },
        "entry": entry_results,
        "finite_observed_cones": cone_results,
        "relations": relation_results,
        "matched_controls": matched_results,
        "integrity_gates": integrity_gates,
        "diagnostic_predicates": diagnostic_predicates,
        "preregistered_composites": preregistered_composites,
        "claim_boundary": [
            "two frozen eight-state D4 systems only",
            "fresh coordinate episodes are not held-out task-family support",
            "finite observed-state cone membership is not ambient or infinite closure",
            "spectra describe ambient projective mechanisms, not a causal quotient certificate",
            "deterministic controls do not define a population of words or models",
            "long-path and matched conclusions use only the registered 64-case deterministic transversal per episode and suffixes through H=8",
            "old 930000/931000 relation spectroscopy and continuation outcomes are exploratory design context; fresh endpoints are adaptive-developmental and nonconfirmatory",
            "no causal-quotient minimality claim",
            "no global invariant metric or normally attracting fiber claim",
            "no spontaneous, universal, or architecture-independent Neuralese claim",
        ],
        "execution": {
            "started_utc": started_wall,
            "finished_utc": utc_now(),
            "elapsed_seconds": elapsed,
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "registered_output": str(RESULT_PATH),
            "run_started_ledger": str(RUN_STARTED_PATH),
            "alternate_profiles": "not accepted",
            "overwrite": "refused",
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    _refuse_existing_execution_artifacts()
    try:
        result = run_registered()
        atomic_create_json(RESULT_PATH, result)
    except Exception as error:
        attempt = {
            "schema": "komorebi.neuralese.entry_cone_holonomy.invalid_attempt.v1",
            "version": VERSION,
            "author": AUTHOR,
            "status": "ABORTED_FAIL_CLOSED",
            "utc": utc_now(),
            "error_type": type(error).__name__,
            "error": str(error),
            "registered_result_created": False,
        }
        if not INVALID_ATTEMPT_PATH.exists():
            atomic_create_json(INVALID_ATTEMPT_PATH, attempt)
        raise
    print(f"V031_RESULT={RESULT_PATH}")
    print(f"V031_RESULT_SHA256={checkpoint_io.file_sha256(RESULT_PATH)}")
    print(f"V031_ELAPSED_SECONDS={result['execution']['elapsed_seconds']:.6f}")
    for name, passed in result["integrity_gates"].items():
        print(f"{name}={'PASS' if passed else 'FAIL'}")
    for name, observed in result["diagnostic_predicates"].items():
        if observed is None:
            rendered = "INVALID_UNDER_REGISTERED_PRECONDITION"
        else:
            rendered = "TRUE" if observed else "FALSE"
        print(f"{name}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
