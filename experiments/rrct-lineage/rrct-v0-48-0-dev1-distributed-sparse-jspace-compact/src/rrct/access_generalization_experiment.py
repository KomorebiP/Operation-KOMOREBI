"""RRCT v0.38 access-decoder generalization experiment.

v0.37 established post-change structural closure but missed its frozen remap
reliability endpoint because the workspace access readout compressed each
attempted boundary identity into one moving centroid.  v0.38 changes only that
public access decoder.  The private boundary learner, drift quarantine,
action policy, transition rollout, world, schedule, controls, and endpoint
thresholds are inherited unchanged from v0.37.

The replacement is a bounded first-nearest exemplar memory.  Prediction is
made before the current attempted public pair is supplied as a self-supervised
label.  Thus the decoder remains evaluator-blind and prequential.  This module
wraps the complete v0.37 trace engine and adds decoder-specific provenance and
endpoints.

This is an exploratory engineering experiment.  It does not establish
phenomenal awareness, sentience, valence, personhood, or moral status.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import platform
import re
import sys
from datetime import datetime, timezone
from collections import deque
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from .agent import RRCTAgent
from .causal_boundary import (
    ACCESS_MEMORY_SNAPSHOT_SCHEMA,
    CausalBoundaryConfig,
)
from .post_change_closure_experiment import (
    V037_D1_CONFIG,
    V037ExperimentConfig,
    V037_MIN_CORRECT_TAIL_ACTIONS,
    run_post_change_closure_trace,
)
from .unified_causal_loop import UnifiedCausalLoopConfig
from .unified_causal_loop_experiment import (
    V036_ACTION_DIM,
    V036_AGENT_STREAM_TAG,
    V036_OBSERVATION_DIM,
    _DurableRowStream,
    _exclusive_json,
    _fsync_directory,
    _jsonl_row_bytes,
    _json_sha256,
    _jsonable,
    _stream_seed,
    _write_all,
)

V038_VERSION = "0.38.0.dev1"
V038_ROW_SCHEMA = "rrct.v038.access_generalization.row.v1"
V038_SUMMARY_SCHEMA = "rrct.v038.access_generalization.summary.v1"
V038_ACCESS_MODE = "fifo_memory"
V038_ACCESS_MEMORY_CAPACITY = 64
V038_ACCESS_NEIGHBORS = 1
V038_ACCESS_PROTOTYPE_LEARNING_RATE = 0.25
V038_MIN_REMAP_CORRECT_ACTIONS = 440
V038_MIN_RESTORE_CORRECT_ACTIONS = 440
V038_PILOT_SEEDS = (16342, 28953, 30658, 32829)
V038_FIRST_PILOT_SEED = V038_PILOT_SEEDS[0]
V038_ROWS_ARTIFACT = "v038_access_generalization_rows.jsonl"
V038_SUMMARY_ARTIFACT = "v038_access_generalization_summary.json"
V038_COHORT_ARTIFACT = "V0_38_COHORT_SUMMARY.json"
V038_PROJECT_ROOT = Path(__file__).resolve().parents[2]
V038_VALIDATION_ROOT = V038_PROJECT_ROOT / "validation"
V038_CAMPAIGN_ROOT = (
    V038_VALIDATION_ROOT / "v0.38_access_generalization_campaign"
)
V038_FREEZE_PATH = V038_VALIDATION_ROOT / "V0_38_PREOUTCOME_FREEZE.json"
V038_FREEZE_SHA256_PATH = (
    V038_VALIDATION_ROOT / "V0_38_PREOUTCOME_FREEZE.json.sha256"
)
V038_ATTEMPT_PATTERN = re.compile(r"^G1-P-\d{4}$")


def _agent_v038(
    boundary_config: CausalBoundaryConfig,
    run_seed: int,
) -> RRCTAgent:
    """Construct the selected access decoder before any agent state exists."""

    return RRCTAgent(
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
        causal_access_readout_mode=V038_ACCESS_MODE,
        causal_access_memory_capacity=V038_ACCESS_MEMORY_CAPACITY,
        causal_access_neighbors=V038_ACCESS_NEIGHBORS,
        causal_access_prototype_learning_rate=(
            V038_ACCESS_PROTOTYPE_LEARNING_RATE
        ),
    )


def _memory_summary(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    memories = snapshot.get("memories")
    if not isinstance(memories, (tuple, list)):
        raise RuntimeError("v0.38 access snapshot contains no memories")
    sizes = [int(len(np.asarray(memory))) for memory in memories]
    updates = np.asarray(snapshot.get("class_updates"), dtype=np.int64)
    return {
        "schema": snapshot.get("schema"),
        "strategy": snapshot.get("strategy"),
        "memory_capacity": int(snapshot.get("memory_capacity")),
        "neighbors": int(snapshot.get("neighbors")),
        "class_count": len(sizes),
        "class_memory_sizes": sizes,
        "maximum_class_memory_size": max(sizes, default=0),
        "nonempty_classes": int(sum(size > 0 for size in sizes)),
        "class_updates": updates.tolist(),
        "update_count": int(snapshot.get("update_count")),
        "snapshot_digest": snapshot.get("digest"),
    }


def _exact_public_action_count(tail: Mapping[str, Any]) -> int:
    """Recover the integer exact-public count from a v0.37 tail summary."""

    rows = int(tail["rows"])
    fraction = float(tail["action_public_exact_fraction"])
    count = int(round(rows * fraction))
    if count < 0 or count > rows:
        raise RuntimeError("exact public-action count is out of bounds")
    if not np.isclose(fraction, count / rows, rtol=0.0, atol=1e-12):
        raise RuntimeError("exact public-action fraction is not integer-valued")
    return count


def _wrap_v038_row(
    row: Mapping[str, Any],
    *,
    causal_access_updated: bool | None = None,
    causal_access_updates: int | None = None,
) -> dict[str, Any]:
    wrapped = copy.deepcopy(dict(row))
    engine_schema = wrapped.get("schema")
    engine_sha256 = _json_sha256(wrapped)
    update_count = (
        int(wrapped.get("causal_access_updates", 0))
        if causal_access_updates is None
        else int(causal_access_updates)
    )
    updated = (
        bool(wrapped.get("causal_access_updated", False))
        if causal_access_updated is None
        else bool(causal_access_updated)
    )
    if update_count < 0:
        raise ValueError("causal_access_updates must be nonnegative")
    wrapped["schema"] = V038_ROW_SCHEMA
    wrapped["v037_engine_schema"] = engine_schema
    wrapped["v037_engine_row_sha256"] = engine_sha256
    wrapped["causal_access_updated"] = updated
    wrapped["causal_access_updates"] = update_count
    wrapped["access_decoder"] = {
        "mode": V038_ACCESS_MODE,
        "memory_capacity": V038_ACCESS_MEMORY_CAPACITY,
        "neighbors": V038_ACCESS_NEIGHBORS,
        "prototype_learning_rate": V038_ACCESS_PROTOTYPE_LEARNING_RATE,
        "prediction_before_current_label": True,
        "evaluator_truth_visible": False,
    }
    wrapper_payload = {
        "engine_row_sha256": engine_sha256,
        "access_decoder": wrapped["access_decoder"],
        "causal_access_updated": updated,
        "causal_access_updates": update_count,
    }
    wrapped["v038_wrapper_digest"] = _json_sha256(wrapper_payload)
    wrapped["v038_wrapper_integrity"] = bool(
        wrapped.get("hard_integrity_valid", False)
        and engine_schema == "rrct.v037.post_change_closure.row.v1"
        and wrapped["access_decoder"]["prediction_before_current_label"]
        and not wrapped["access_decoder"]["evaluator_truth_visible"]
        and wrapped["causal_access_updates"] >= 0
    )
    return wrapped


def _build_v038_summary(
    seed: int,
    rows: Sequence[Mapping[str, Any]],
    v037_summary: Mapping[str, Any],
    access_snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    memory = _memory_summary(access_snapshot)
    remap_tail = v037_summary["post_change"]["remap"]["tail"]
    restore_tail = v037_summary["post_change"]["restore"]["tail"]
    disconnect_tail = v037_summary["post_change"]["disconnect"]["tail"]
    stable_tail = v037_summary["stable_tail"]
    shock_tail = v037_summary["world_shock_tail"]
    exact_counts = {
        "stable": _exact_public_action_count(stable_tail),
        "world_shock": _exact_public_action_count(shock_tail),
        "remap": _exact_public_action_count(remap_tail),
        "disconnect": _exact_public_action_count(disconnect_tail),
        "restore": _exact_public_action_count(restore_tail),
    }
    inherited = {
        str(name): bool(value)
        for name, value in v037_summary["endpoints"].items()
    }
    expected_class_count = 1 + 4 * 6
    class_sizes = [int(value) for value in memory["class_memory_sizes"]]
    class_updates = [int(value) for value in memory["class_updates"]]
    access_update_flags_raw = [
        row.get("causal_access_updated") for row in rows
    ]
    access_update_counts_raw = [
        row.get("causal_access_updates") for row in rows
    ]
    update_trace_fields_present = bool(
        rows
        and all(isinstance(value, bool) for value in access_update_flags_raw)
        and all(
            isinstance(value, int) and not isinstance(value, bool)
            for value in access_update_counts_raw
        )
    )
    if update_trace_fields_present:
        access_update_flags = [
            bool(value) for value in access_update_flags_raw
        ]
        access_update_counts = [
            int(value) for value in access_update_counts_raw
        ]
    else:
        access_update_flags = []
        access_update_counts = []
    initial_trace_update_count = (
        access_update_counts[0] - int(access_update_flags[0])
        if access_update_counts
        else 0
    )
    previous_update_count = initial_trace_update_count
    update_trace_stepwise_consistent = bool(
        update_trace_fields_present
        and initial_trace_update_count in (0, 1)
    )
    for updated, update_count in zip(
        access_update_flags,
        access_update_counts,
        strict=True,
    ):
        expected_update_count = previous_update_count + int(updated)
        if update_count != expected_update_count:
            update_trace_stepwise_consistent = False
        previous_update_count = update_count
    terminal_trace_update_count = (
        access_update_counts[-1] if access_update_counts else 0
    )
    updated_row_count = int(sum(access_update_flags))
    integrity = {
        "row_count_exact": len(rows) == int(V037_D1_CONFIG.total_steps),
        "all_wrappers_valid": all(
            bool(row.get("v038_wrapper_integrity")) for row in rows
        ),
        "all_inherited_hard_integrity": all(
            bool(row.get("hard_integrity_valid")) for row in rows
        ),
        "decoder_schema_exact": (
            memory["schema"] == ACCESS_MEMORY_SNAPSHOT_SCHEMA
        ),
        "decoder_strategy_exact": memory["strategy"] == "fifo",
        "decoder_capacity_exact": (
            memory["memory_capacity"] == V038_ACCESS_MEMORY_CAPACITY
        ),
        "decoder_neighbors_exact": (
            memory["neighbors"] == V038_ACCESS_NEIGHBORS
        ),
        "decoder_memory_bounded": (
            memory["maximum_class_memory_size"]
            <= V038_ACCESS_MEMORY_CAPACITY
        ),
        "decoder_class_count_exact": (
            memory["class_count"] == expected_class_count
            and len(class_sizes) == expected_class_count
            and len(class_updates) == expected_class_count
        ),
        "decoder_class_updates_nonnegative": all(
            value >= 0 for value in class_updates
        ),
        "decoder_memory_sizes_match_updates": bool(
            len(class_sizes) == len(class_updates)
            and all(
                size == min(updates, V038_ACCESS_MEMORY_CAPACITY)
                for size, updates in zip(
                    class_sizes, class_updates, strict=True
                )
            )
        ),
        "decoder_updates_internally_consistent": (
            memory["update_count"] > 0
            and sum(memory["class_updates"]) == memory["update_count"]
        ),
        "decoder_update_trace_fields_present": update_trace_fields_present,
        "decoder_update_trace_stepwise_consistent": (
            update_trace_stepwise_consistent
            and (
                initial_trace_update_count + updated_row_count
                == terminal_trace_update_count
            )
        ),
        "decoder_update_trace_terminal_matches_snapshot": (
            update_trace_fields_present
            and terminal_trace_update_count == memory["update_count"]
        ),
    }
    integrity_pass = bool(all(bool(value) for value in integrity.values()))
    endpoints = {
        "G01_integrity": integrity_pass,
        "G02_all_v037_closure_endpoints": bool(all(inherited.values())),
        "G03_remap_access_generalization": bool(
            exact_counts["remap"] >= V038_MIN_REMAP_CORRECT_ACTIONS
        ),
        "G04_restoration_access_generalization": bool(
            exact_counts["restore"] >= V038_MIN_RESTORE_CORRECT_ACTIONS
        ),
        "G05_no_stable_or_shock_regression": bool(
            exact_counts["stable"] >= V037_MIN_CORRECT_TAIL_ACTIONS
            and exact_counts["world_shock"]
            >= int(np.ceil(0.90 * int(shock_tail["rows"])))
        ),
        "G06_disconnect_null_specificity": bool(
            float(disconnect_tail["action_public_null_fraction"]) >= 0.90
            and float(disconnect_tail["action_gate_open_fraction"]) <= 0.10
            and exact_counts["disconnect"] >= V037_MIN_CORRECT_TAIL_ACTIONS
        ),
    }
    all_met = bool(all(endpoints.values()))
    return {
        "schema": V038_SUMMARY_SCHEMA,
        "version": V038_VERSION,
        "scientific_status": "exploratory_fresh_seed_pilot",
        "seed": int(seed),
        "access_decoder": {
            "mode": V038_ACCESS_MODE,
            "memory_capacity": V038_ACCESS_MEMORY_CAPACITY,
            "neighbors": V038_ACCESS_NEIGHBORS,
            "prototype_learning_rate": V038_ACCESS_PROTOTYPE_LEARNING_RATE,
            "prediction_before_current_label": True,
            "evaluator_truth_visible": False,
        },
        "access_memory_terminal": memory,
        "access_update_trace": {
            "rows": len(rows),
            "initial_update_count": initial_trace_update_count,
            "first_update_count": (
                access_update_counts[0] if access_update_counts else None
            ),
            "terminal_update_count": terminal_trace_update_count,
            "updated_rows": updated_row_count,
            "stepwise_consistent": update_trace_stepwise_consistent,
        },
        "exact_public_action_counts": exact_counts,
        "inherited_v037_endpoints": inherited,
        "v037_status": v037_summary["status"],
        "post_change": copy.deepcopy(v037_summary["post_change"]),
        "stable_tail": copy.deepcopy(stable_tail),
        "world_shock_tail": copy.deepcopy(shock_tail),
        "control_return_margins": copy.deepcopy(
            v037_summary["control_return_margins"]
        ),
        "rollout_audit": copy.deepcopy(v037_summary["rollout_audit"]),
        "integrity": integrity,
        "endpoints": endpoints,
        "all_endpoints_met": all_met,
        "earliest_failed_layer": next(
            (name for name, met in endpoints.items() if not met), None
        ),
        "status": (
            "V038_PILOT_ENDPOINTS_MET"
            if all_met
            else "V038_PILOT_ENDPOINTS_NOT_MET"
        ),
        "interpretation_boundary": (
            "Exploratory evidence for bounded prequential public-access "
            "generalization in the RRCT synthetic runtime; not evidence of "
            "phenomenal awareness, sentience, or valence."
        ),
    }


def run_access_generalization_trace(
    seed: int,
    *,
    experiment_config: V037ExperimentConfig = V037_D1_CONFIG,
    boundary_config: CausalBoundaryConfig | None = None,
    runtime_config: UnifiedCausalLoopConfig | None = None,
    sealed_row_sink: Callable[[Mapping[str, Any]], None] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the complete v0.37 world with only the access decoder replaced."""

    created_agents: list[RRCTAgent] = []
    wrapped_rows: list[dict[str, Any]] = []

    def factory(config: CausalBoundaryConfig, run_seed: int) -> RRCTAgent:
        agent = _agent_v038(config, run_seed)
        created_agents.append(agent)
        return agent

    def row_sink(row: Mapping[str, Any]) -> None:
        if len(created_agents) != 1 or created_agents[0].last_result is None:
            raise RuntimeError("v0.38 row arrived without live access telemetry")
        result = created_agents[0].last_result
        wrapped = _wrap_v038_row(
            row,
            causal_access_updated=result.causal_access_updated,
            causal_access_updates=result.causal_access_update_count,
        )
        wrapped_rows.append(wrapped)
        if sealed_row_sink is not None:
            sealed_row_sink(wrapped)

    _, v037_summary = run_post_change_closure_trace(
        int(seed),
        experiment_config=experiment_config,
        boundary_config=boundary_config,
        runtime_config=runtime_config,
        agent_factory=factory,
        sealed_row_sink=row_sink,
    )
    if len(created_agents) != 1:
        raise RuntimeError("v0.38 did not retain exactly one live agent")
    readout = created_agents[0]._causal_access_readout
    if readout is None:
        raise RuntimeError("v0.38 access readout disappeared")
    access_snapshot = readout.snapshot()
    summary = _build_v038_summary(
        int(seed), wrapped_rows, v037_summary, access_snapshot
    )
    return wrapped_rows, summary


def write_v038_evidence(
    rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    destination: Path,
) -> dict[str, str]:
    destination.mkdir(parents=True, exist_ok=False)
    rows_path = destination / V038_ROWS_ARTIFACT
    summary_path = destination / V038_SUMMARY_ARTIFACT
    digest = hashlib.sha256()
    with rows_path.open("wb") as handle:
        for row in rows:
            encoded = (
                json.dumps(
                    _jsonable(row),
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                )
                + "\n"
            ).encode("utf-8")
            handle.write(encoded)
            digest.update(encoded)
    summary_text = (
        json.dumps(
            _jsonable(summary),
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    )
    summary_path.write_text(summary_text, encoding="utf-8")
    hashes = {
        V038_ROWS_ARTIFACT: digest.hexdigest(),
        V038_SUMMARY_ARTIFACT: hashlib.sha256(
            summary_text.encode("utf-8")
        ).hexdigest(),
    }
    (destination / "artifact_sha256.json").write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return hashes


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_v038_preoutcome_freeze() -> dict[str, Any]:
    """Verify the immutable protocol, source tree, and source archive."""

    if not V038_FREEZE_PATH.is_file() or not V038_FREEZE_SHA256_PATH.is_file():
        raise RuntimeError("v0.38 pre-outcome freeze is absent")
    raw = V038_FREEZE_PATH.read_bytes()
    observed = hashlib.sha256(raw).hexdigest()
    companion = V038_FREEZE_SHA256_PATH.read_text(encoding="utf-8").split()
    if (
        len(companion) < 2
        or companion[0] != observed
        or companion[1] != V038_FREEZE_PATH.name
    ):
        raise RuntimeError("v0.38 freeze companion checksum mismatch")
    freeze = json.loads(raw)
    required = {
        "schema": "rrct.v038.preoutcome_freeze.v1",
        "version": V038_VERSION,
        "fresh_pilot_seeds": list(V038_PILOT_SEEDS),
        "access_decoder": {
            "mode": V038_ACCESS_MODE,
            "memory_capacity": V038_ACCESS_MEMORY_CAPACITY,
            "neighbors": V038_ACCESS_NEIGHBORS,
            "prototype_learning_rate": (
                V038_ACCESS_PROTOTYPE_LEARNING_RATE
            ),
        },
    }
    for key, value in required.items():
        if freeze.get(key) != value:
            raise RuntimeError(f"v0.38 freeze {key} mismatch")
    mapping = freeze.get("scientific_source_sha256")
    if not isinstance(mapping, dict) or not mapping:
        raise RuntimeError("v0.38 source manifest is absent")
    canonical_mapping = {
        str(path): str(digest) for path, digest in sorted(mapping.items())
    }
    if _json_sha256(canonical_mapping) != freeze.get(
        "scientific_source_set_sha256"
    ):
        raise RuntimeError("v0.38 source-manifest set digest mismatch")
    for relative, expected in canonical_mapping.items():
        path = V038_PROJECT_ROOT / relative
        if not path.is_file() or _sha256_file(path) != expected:
            raise RuntimeError(f"v0.38 frozen source mismatch: {relative}")
    archive = freeze.get("source_archive")
    if not isinstance(archive, dict):
        raise RuntimeError("v0.38 source archive record is absent")
    relative_archive = Path(str(archive.get("relative_path")))
    if relative_archive.is_absolute() or ".." in relative_archive.parts:
        raise RuntimeError("v0.38 source archive path is not project-relative")
    archive_path = (V038_PROJECT_ROOT / relative_archive).resolve()
    project_root = V038_PROJECT_ROOT.resolve()
    if not archive_path.is_relative_to(project_root):
        raise RuntimeError("v0.38 source archive escapes the project root")
    if (
        not archive_path.is_file()
        or _sha256_file(archive_path) != archive.get("sha256")
    ):
        raise RuntimeError("v0.38 pre-outcome source archive mismatch")
    if int(archive.get("member_count", -1)) != len(canonical_mapping):
        raise RuntimeError("v0.38 source archive member count mismatch")
    return {
        "freeze": freeze,
        "freeze_sha256": observed,
        "source_archive_path": archive_path,
    }


def _exclusive_copy(source: Path, destination: Path) -> str:
    descriptor = os.open(
        destination,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o644,
    )
    digest = hashlib.sha256()
    try:
        with source.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                _write_all(descriptor, chunk)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    _fsync_directory(destination.parent)
    return digest.hexdigest()


def _claim_v038_attempt(
    seed: int,
    attempt_id: str,
    freeze_sha256: str,
    campaign_root: Path,
) -> tuple[Path, Path, Path]:
    if int(seed) not in V038_PILOT_SEEDS:
        raise ValueError("seed is not in the frozen v0.38 pilot registry")
    if not V038_ATTEMPT_PATTERN.fullmatch(attempt_id):
        raise ValueError("attempt_id must match G1-P-####")
    campaign_root.mkdir(parents=True, exist_ok=True)
    claims = campaign_root / "claims"
    claims.mkdir(parents=True, exist_ok=True)
    attempt_claim = claims / f"attempt-{attempt_id}.json"
    seed_claim = claims / f"seed-{int(seed)}.json"
    output = campaign_root / f"{attempt_id}-seed-{int(seed)}"
    if output.exists():
        raise FileExistsError(f"v0.38 output already exists: {output}")
    claim = {
        "schema": "rrct.v038.campaign_claim.v1",
        "version": V038_VERSION,
        "attempt_id": attempt_id,
        "seed": int(seed),
        "freeze_sha256": freeze_sha256,
        "claimed_at_utc": datetime.now(timezone.utc).isoformat(),
        "state": "consumed_before_rng_construction",
    }
    _exclusive_json(attempt_claim, claim)
    try:
        _exclusive_json(seed_claim, claim)
    except Exception:
        raise RuntimeError(
            "v0.38 seed was already consumed; attempt claim remains recorded"
        )
    output.mkdir(parents=False, exist_ok=False)
    _fsync_directory(campaign_root)
    return output, attempt_claim, seed_claim


def run_claimed_v038_pilot(
    seed: int,
    attempt_id: str,
    *,
    campaign_root: Path | None = None,
    progress_every: int = 240,
) -> tuple[Path, dict[str, Any]]:
    """Claim and run one fresh seed with durable row-level evidence."""

    if (
        isinstance(progress_every, (bool, np.bool_))
        or not isinstance(progress_every, (int, np.integer))
        or int(progress_every) <= 0
    ):
        raise ValueError("progress_every must be a positive integer")

    verified = verify_v038_preoutcome_freeze()
    root = V038_CAMPAIGN_ROOT if campaign_root is None else Path(campaign_root)
    output, attempt_claim, seed_claim = _claim_v038_attempt(
        int(seed), attempt_id, verified["freeze_sha256"], root
    )
    archive_source: Path = verified["source_archive_path"]
    archive_copy = output / archive_source.name
    copied_sha256 = _exclusive_copy(archive_source, archive_copy)
    expected_archive_sha256 = verified["freeze"]["source_archive"]["sha256"]
    if copied_sha256 != expected_archive_sha256:
        raise RuntimeError("copied v0.38 source archive checksum mismatch")
    start_receipt = {
        "schema": "rrct.v038.start_receipt.v1",
        "version": V038_VERSION,
        "attempt_id": attempt_id,
        "seed": int(seed),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "freeze_sha256": verified["freeze_sha256"],
        "source_archive": archive_copy.name,
        "source_archive_sha256": copied_sha256,
        "expected_transition_count": int(V037_D1_CONFIG.total_steps),
        "attempt_claim": attempt_claim.relative_to(root).as_posix(),
        "attempt_claim_sha256": _sha256_file(attempt_claim),
        "seed_claim": seed_claim.relative_to(root).as_posix(),
        "seed_claim_sha256": _sha256_file(seed_claim),
        "row_fsync": True,
        "seed_claimed_before_rng_construction": True,
        "environment": {
            "python": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "executable": sys.executable,
            "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
            "openblas_num_threads": os.environ.get(
                "OPENBLAS_NUM_THREADS"
            ),
            "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
            "mkl_num_threads": os.environ.get("MKL_NUM_THREADS"),
        },
    }
    start_receipt_sha256 = _exclusive_json(
        output / "start_receipt.json", start_receipt
    )
    stream = _DurableRowStream(output / V038_ROWS_ARTIFACT)
    result_summary: dict[str, Any] | None = None
    try:
        counter = 0

        def sink(row: Mapping[str, Any]) -> None:
            nonlocal counter
            stream.append(row)
            counter += 1
            if (
                counter % int(progress_every) == 0
                or row.get("structural_event")
                in {"acquisition", "pair_revision", "revocation"}
            ):
                print(
                    " ".join(
                        [
                            f"row={counter}",
                            f"phase={row.get('phase')}",
                            f"offset={int(row.get('phase_offset', -1)) + 1}",
                            f"event={row.get('structural_event')}",
                            f"gate={row.get('action_gate_open_evaluator_only')}",
                        ]
                    ),
                    flush=True,
                )

        completed_rows, result_summary = run_access_generalization_trace(
            int(seed), sealed_row_sink=sink
        )
        stream.close()
        expected_rows_digest = hashlib.sha256()
        for row in completed_rows:
            expected_rows_digest.update(_jsonl_row_bytes(row))
        if stream.row_count != len(completed_rows):
            raise RuntimeError(
                "durable v0.38 row count does not match the completed trace"
            )
        if stream.row_count != int(V037_D1_CONFIG.total_steps):
            raise RuntimeError("v0.38 trace has an unexpected transition count")
        if stream.sha256 != expected_rows_digest.hexdigest():
            raise RuntimeError(
                "durable v0.38 row digest does not match the completed trace"
            )
        if _sha256_file(output / V038_ROWS_ARTIFACT) != stream.sha256:
            raise RuntimeError("durable v0.38 row stream changed after sealing")
        enriched = copy.deepcopy(result_summary)
        enriched["campaign"] = {
            "attempt_id": attempt_id,
            "freeze_sha256": verified["freeze_sha256"],
            "source_archive": archive_copy.name,
            "source_archive_sha256": copied_sha256,
            "rows_sha256": stream.sha256,
            "rows_count": stream.row_count,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        _exclusive_json(output / V038_SUMMARY_ARTIFACT, enriched)
        summary_sha256 = _sha256_file(output / V038_SUMMARY_ARTIFACT)
        finish = {
            "schema": "rrct.v038.finish_receipt.v1",
            "version": V038_VERSION,
            "attempt_id": attempt_id,
            "seed": int(seed),
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "freeze_sha256": verified["freeze_sha256"],
            "source_archive_sha256": copied_sha256,
            "rows_count": stream.row_count,
            "rows_sha256": stream.sha256,
            "summary_sha256": summary_sha256,
            "start_receipt_sha256": start_receipt_sha256,
            "endpoints_sha256": _json_sha256(enriched["endpoints"]),
            "status": enriched["status"],
            "all_endpoints_met": enriched["all_endpoints_met"],
        }
        _exclusive_json(output / "finish_receipt.json", finish)
        artifacts = {
            V038_ROWS_ARTIFACT: stream.sha256,
            V038_SUMMARY_ARTIFACT: summary_sha256,
            archive_copy.name: copied_sha256,
            "start_receipt.json": _sha256_file(
                output / "start_receipt.json"
            ),
            "finish_receipt.json": _sha256_file(
                output / "finish_receipt.json"
            ),
        }
        _exclusive_json(output / "artifact_sha256.json", artifacts)
        return output, enriched
    except Exception as error:
        try:
            stream.close()
        except Exception:
            pass
        failure = {
            "schema": "rrct.v038.failure_receipt.v1",
            "version": V038_VERSION,
            "attempt_id": attempt_id,
            "seed": int(seed),
            "failed_at_utc": datetime.now(timezone.utc).isoformat(),
            "exception_type": type(error).__name__,
            "exception_message": str(error),
            "rows_count": stream.row_count,
            "rows_sha256": stream.sha256,
        }
        try:
            _exclusive_json(output / "failure_receipt.json", failure)
        except Exception:
            pass
        raise


def _audit_v038_row_stream(path: Path) -> dict[str, Any]:
    """Recompute frozen endpoint counts directly from one sealed row stream."""

    expected_phase_counts = {
        "stable": int(V037_D1_CONFIG.stable_steps),
        "world_shock": int(V037_D1_CONFIG.world_shock_steps),
        "remap": int(V037_D1_CONFIG.remap_steps),
        "disconnect": int(V037_D1_CONFIG.disconnect_steps),
        "restore": int(V037_D1_CONFIG.restore_steps),
    }
    phase_counts = {phase: 0 for phase in expected_phase_counts}
    tail_size = int(V037_D1_CONFIG.recovery_tail_steps)
    tails: dict[str, deque[dict[str, Any]]] = {
        phase: deque(maxlen=min(tail_size, expected_count))
        for phase, expected_count in expected_phase_counts.items()
    }
    digest = hashlib.sha256()
    row_count = 0
    all_wrappers_valid = True
    all_hard_integrity_valid = True
    all_wrapper_digests_valid = True
    all_engine_row_digests_valid = True
    access_update_trace_stepwise_consistent = True
    initial_access_update_count: int | None = None
    previous_access_update_count = 0
    access_updated_rows = 0
    with path.open("rb") as handle:
        for raw_line in handle:
            digest.update(raw_line)
            if not raw_line.endswith(b"\n"):
                raise RuntimeError("v0.38 row stream has an unterminated row")
            try:
                row = json.loads(raw_line)
            except json.JSONDecodeError as error:
                raise RuntimeError(
                    f"v0.38 row {row_count} is not valid JSON"
                ) from error
            if not isinstance(row, dict):
                raise RuntimeError(f"v0.38 row {row_count} is not an object")
            if row.get("schema") != V038_ROW_SCHEMA:
                raise RuntimeError(f"v0.38 row {row_count} schema mismatch")
            if int(row.get("transition_index", -1)) != row_count:
                raise RuntimeError(
                    f"v0.38 transition order mismatch at row {row_count}"
                )
            engine_schema = row.get("v037_engine_schema")
            engine_digest = row.get("v037_engine_row_sha256")
            wrapper_digest = row.get("v038_wrapper_digest")
            if not all(
                isinstance(value, str) and len(value) == 64
                for value in (engine_digest, wrapper_digest)
            ):
                raise RuntimeError(
                    f"v0.38 row {row_count} has malformed wrapper digests"
                )
            engine_row = copy.deepcopy(row)
            for key in (
                "v037_engine_schema",
                "v037_engine_row_sha256",
                "causal_access_updated",
                "causal_access_updates",
                "access_decoder",
                "v038_wrapper_digest",
                "v038_wrapper_integrity",
            ):
                engine_row.pop(key, None)
            engine_row["schema"] = engine_schema
            observed_engine_digest = _json_sha256(engine_row)
            observed_wrapper_digest = _json_sha256(
                {
                    "engine_row_sha256": engine_digest,
                    "access_decoder": row.get("access_decoder"),
                    "causal_access_updated": bool(
                        row.get("causal_access_updated")
                    ),
                    "causal_access_updates": int(
                        row.get("causal_access_updates", -1)
                    ),
                }
            )
            all_engine_row_digests_valid = bool(
                all_engine_row_digests_valid
                and observed_engine_digest == engine_digest
            )
            all_wrapper_digests_valid = bool(
                all_wrapper_digests_valid
                and observed_wrapper_digest == wrapper_digest
            )
            access_updated = row.get("causal_access_updated")
            access_update_count = row.get("causal_access_updates")
            if not isinstance(access_updated, bool):
                raise RuntimeError(
                    f"v0.38 row {row_count} has a malformed access-update flag"
                )
            if not (
                isinstance(access_update_count, int)
                and not isinstance(access_update_count, bool)
                and access_update_count >= 0
            ):
                raise RuntimeError(
                    f"v0.38 row {row_count} has a malformed access-update count"
                )
            if initial_access_update_count is None:
                initial_access_update_count = (
                    access_update_count - int(access_updated)
                )
                access_update_trace_stepwise_consistent = bool(
                    access_update_trace_stepwise_consistent
                    and initial_access_update_count in (0, 1)
                )
                previous_access_update_count = initial_access_update_count
            expected_access_update_count = (
                previous_access_update_count + int(access_updated)
            )
            access_update_trace_stepwise_consistent = bool(
                access_update_trace_stepwise_consistent
                and access_update_count == expected_access_update_count
            )
            previous_access_update_count = access_update_count
            access_updated_rows += int(access_updated)
            phase = str(row.get("phase"))
            if phase not in phase_counts:
                raise RuntimeError(
                    f"v0.38 row {row_count} has an unknown phase {phase!r}"
                )
            phase_counts[phase] += 1
            all_wrappers_valid = bool(
                all_wrappers_valid and row.get("v038_wrapper_integrity")
            )
            all_hard_integrity_valid = bool(
                all_hard_integrity_valid and row.get("hard_integrity_valid")
            )
            tails[phase].append(
                {
                    "exact": bool(
                        row.get("action_public_exact_evaluator_only")
                    ),
                    "public_null": row.get("action_public_pair") is None,
                    "gate_open": bool(
                        row.get("action_gate_open_evaluator_only")
                    ),
                }
            )
            row_count += 1
    if row_count != int(V037_D1_CONFIG.total_steps):
        raise RuntimeError(
            f"v0.38 row-count failure: {row_count} != "
            f"{V037_D1_CONFIG.total_steps}"
        )
    if phase_counts != expected_phase_counts:
        raise RuntimeError(
            "v0.38 phase-count failure: "
            f"observed={phase_counts!r} expected={expected_phase_counts!r}"
        )
    if not all_wrapper_digests_valid or not all_engine_row_digests_valid:
        raise RuntimeError(
            "v0.38 completed stream contains a cryptographic binding failure"
        )
    access_update_trace_stepwise_consistent = bool(
        access_update_trace_stepwise_consistent
        and initial_access_update_count is not None
        and (
            initial_access_update_count + access_updated_rows
            == previous_access_update_count
        )
    )
    exact_counts = {
        phase: int(sum(row["exact"] for row in tail))
        for phase, tail in tails.items()
    }
    disconnect_tail = tails["disconnect"]
    disconnect_null_count = int(
        sum(row["public_null"] for row in disconnect_tail)
    )
    disconnect_null_fraction = (
        0.0
        if not disconnect_tail
        else float(disconnect_null_count / len(disconnect_tail))
    )
    disconnect_gate_open_count = int(
        sum(row["gate_open"] for row in disconnect_tail)
    )
    disconnect_gate_open_fraction = (
        0.0
        if not disconnect_tail
        else float(disconnect_gate_open_count / len(disconnect_tail))
    )
    recomputed_endpoints = {
        "G03_remap_access_generalization": bool(
            exact_counts["remap"] >= V038_MIN_REMAP_CORRECT_ACTIONS
        ),
        "G04_restoration_access_generalization": bool(
            exact_counts["restore"] >= V038_MIN_RESTORE_CORRECT_ACTIONS
        ),
        "G05_no_stable_or_shock_regression": bool(
            exact_counts["stable"] >= V037_MIN_CORRECT_TAIL_ACTIONS
            and exact_counts["world_shock"]
            >= int(np.ceil(0.90 * len(tails["world_shock"])))
        ),
        "G06_disconnect_null_specificity": bool(
            disconnect_null_fraction >= 0.90
            and disconnect_gate_open_fraction <= 0.10
            and exact_counts["disconnect"]
            >= V037_MIN_CORRECT_TAIL_ACTIONS
        ),
    }
    return {
        "row_count": row_count,
        "rows_sha256": digest.hexdigest(),
        "phase_counts": phase_counts,
        "tail_rows": {phase: len(tail) for phase, tail in tails.items()},
        "exact_public_action_counts": exact_counts,
        "disconnect_null_count": disconnect_null_count,
        "disconnect_null_fraction": disconnect_null_fraction,
        "disconnect_gate_open_count": disconnect_gate_open_count,
        "disconnect_gate_open_fraction": disconnect_gate_open_fraction,
        "all_wrappers_valid": all_wrappers_valid,
        "all_hard_integrity_valid": all_hard_integrity_valid,
        "all_wrapper_digests_valid": all_wrapper_digests_valid,
        "all_engine_row_digests_valid": all_engine_row_digests_valid,
        "access_update_trace_fields_present": True,
        "access_update_trace_stepwise_consistent": (
            access_update_trace_stepwise_consistent
        ),
        "initial_access_update_count": initial_access_update_count,
        "access_updated_rows": access_updated_rows,
        "terminal_access_update_count": previous_access_update_count,
        "recomputed_endpoints": recomputed_endpoints,
    }


def _build_v038_cohort_summary(
    summaries: Mapping[int, Mapping[str, Any]],
) -> dict[str, Any]:
    """Apply the frozen four-seed cohort rule to verified seed summaries."""

    expected = tuple(int(seed) for seed in V038_PILOT_SEEDS)
    present = tuple(sorted(int(seed) for seed in summaries))
    complete = set(present) == set(expected)
    ordered = [summaries[seed] for seed in expected if seed in summaries]
    remap = [
        int(summary["exact_public_action_counts"]["remap"])
        for summary in ordered
    ]
    restore = [
        int(summary["exact_public_action_counts"]["restore"])
        for summary in ordered
    ]
    all_endpoint_flags = [
        bool(summary["all_endpoints_met"]) for summary in ordered
    ]
    integrity_flags = [
        bool(summary["endpoints"]["G01_integrity"]) for summary in ordered
    ]
    median_remap = None if not remap else float(np.median(remap))
    median_restore = None if not restore else float(np.median(restore))
    criteria = {
        "all_four_fresh_seeds_present": complete,
        "integrity_on_all_four": bool(complete and all(integrity_flags)),
        "at_least_three_all_endpoint_passes": bool(
            complete and sum(all_endpoint_flags) >= 3
        ),
        "median_remap_at_least_440": bool(
            complete and median_remap is not None and median_remap >= 440.0
        ),
        "median_restore_at_least_440": bool(
            complete
            and median_restore is not None
            and median_restore >= 440.0
        ),
    }
    met = bool(all(criteria.values()))
    return {
        "schema": "rrct.v038.access_generalization.cohort.v1",
        "version": V038_VERSION,
        "scientific_status": "exploratory_four_seed_fresh_pilot_cohort",
        "expected_seeds": list(expected),
        "present_seeds": list(present),
        "missing_seeds": [seed for seed in expected if seed not in summaries],
        "per_seed": {
            str(seed): {
                "attempt_id": summaries[seed].get("campaign", {}).get(
                    "attempt_id"
                ),
                "status": summaries[seed]["status"],
                "all_endpoints_met": bool(
                    summaries[seed]["all_endpoints_met"]
                ),
                "endpoints": copy.deepcopy(summaries[seed]["endpoints"]),
                "remap_correct_actions": int(
                    summaries[seed]["exact_public_action_counts"]["remap"]
                ),
                "restore_correct_actions": int(
                    summaries[seed]["exact_public_action_counts"]["restore"]
                ),
            }
            for seed in present
        },
        "all_endpoint_pass_count": int(sum(all_endpoint_flags)),
        "median_remap_correct_actions": median_remap,
        "median_restore_correct_actions": median_restore,
        "criteria": criteria,
        "cohort_target_met": met,
        "status": (
            "V038_COHORT_TARGET_MET"
            if met
            else (
                "V038_COHORT_INCOMPLETE"
                if not complete
                else "V038_COHORT_TARGET_NOT_MET"
            )
        ),
    }


def aggregate_v038_campaign(
    campaign_root: Path = V038_CAMPAIGN_ROOT,
) -> dict[str, Any]:
    """Verify completed evidence directories and aggregate the frozen cohort."""

    verified = verify_v038_preoutcome_freeze()
    campaign_root = Path(campaign_root).resolve()
    archive_name = Path(verified["source_archive_path"]).name
    frozen_archive_sha = verified["freeze"]["source_archive"]["sha256"]
    summaries: dict[int, dict[str, Any]] = {}
    evidence_audit: dict[str, Any] = {}
    for seed in V038_PILOT_SEEDS:
        matches = sorted(
            path
            for path in campaign_root.glob(f"G1-P-*-seed-{seed}")
            if path.is_dir()
            and (path / V038_SUMMARY_ARTIFACT).is_file()
            and (path / "finish_receipt.json").is_file()
        )
        if len(matches) > 1:
            raise RuntimeError(
                f"multiple completed evidence directories for seed {seed}"
            )
        if not matches:
            continue
        directory = matches[0]
        artifacts = json.loads(
            (directory / "artifact_sha256.json").read_text(encoding="utf-8")
        )
        required_artifacts = {
            V038_ROWS_ARTIFACT,
            V038_SUMMARY_ARTIFACT,
            archive_name,
            "start_receipt.json",
            "finish_receipt.json",
        }
        if not isinstance(artifacts, dict) or not required_artifacts.issubset(
            artifacts
        ):
            missing = sorted(required_artifacts - set(artifacts or {}))
            raise RuntimeError(
                f"artifact manifest is incomplete for seed {seed}: {missing}"
            )
        artifact_checks = {
            name: bool(
                (directory / name).is_file()
                and _sha256_file(directory / name) == expected_hash
            )
            for name, expected_hash in artifacts.items()
        }
        if not all(artifact_checks.values()):
            failed = [name for name, valid in artifact_checks.items() if not valid]
            raise RuntimeError(
                f"artifact hash failure for seed {seed}: {', '.join(failed)}"
            )
        row_audit = _audit_v038_row_stream(
            directory / V038_ROWS_ARTIFACT
        )
        if row_audit["rows_sha256"] != artifacts[V038_ROWS_ARTIFACT]:
            raise RuntimeError(f"row digest mismatch for seed {seed}")
        summary = json.loads(
            (directory / V038_SUMMARY_ARTIFACT).read_text(encoding="utf-8")
        )
        if int(summary["seed"]) != int(seed):
            raise RuntimeError(f"summary seed mismatch for {seed}")
        campaign = summary.get("campaign")
        if not isinstance(campaign, dict):
            raise RuntimeError(f"campaign summary is absent for seed {seed}")
        attempt_id = str(campaign.get("attempt_id"))
        if not V038_ATTEMPT_PATTERN.fullmatch(attempt_id):
            raise RuntimeError(f"attempt identifier mismatch for seed {seed}")
        if campaign.get("source_archive_sha256") != frozen_archive_sha:
            raise RuntimeError(f"source archive mismatch for seed {seed}")
        if campaign.get("freeze_sha256") != verified["freeze_sha256"]:
            raise RuntimeError(f"freeze mismatch for seed {seed}")
        if int(campaign.get("rows_count", -1)) != row_audit["row_count"]:
            raise RuntimeError(f"campaign row-count mismatch for seed {seed}")
        if campaign.get("rows_sha256") != row_audit["rows_sha256"]:
            raise RuntimeError(f"campaign row-digest mismatch for seed {seed}")
        reported_counts = summary.get("exact_public_action_counts")
        if reported_counts != row_audit["exact_public_action_counts"]:
            raise RuntimeError(
                f"recomputed exact-action counts disagree for seed {seed}"
            )
        access_memory_terminal = summary.get("access_memory_terminal")
        if not isinstance(access_memory_terminal, dict):
            raise RuntimeError(
                f"terminal access-memory summary is absent for seed {seed}"
            )
        access_update_trace = summary.get("access_update_trace")
        expected_access_update_trace = {
            "rows": row_audit["row_count"],
            "initial_update_count": row_audit[
                "initial_access_update_count"
            ],
            "terminal_update_count": row_audit[
                "terminal_access_update_count"
            ],
            "updated_rows": row_audit["access_updated_rows"],
            "stepwise_consistent": row_audit[
                "access_update_trace_stepwise_consistent"
            ],
        }
        if not isinstance(access_update_trace, dict) or any(
            access_update_trace.get(key) != value
            for key, value in expected_access_update_trace.items()
        ):
            raise RuntimeError(
                f"access-update trajectory summary disagrees for seed {seed}"
            )
        expected_class_count = 1 + 4 * 6
        class_sizes = [
            int(value)
            for value in access_memory_terminal.get(
                "class_memory_sizes", []
            )
        ]
        class_updates = [
            int(value)
            for value in access_memory_terminal.get("class_updates", [])
        ]
        terminal_update_count = int(
            access_memory_terminal.get("update_count", -1)
        )
        expected_integrity = {
            "row_count_exact": (
                row_audit["row_count"]
                == int(V037_D1_CONFIG.total_steps)
            ),
            "all_wrappers_valid": bool(
                row_audit["all_wrappers_valid"]
            ),
            "all_inherited_hard_integrity": bool(
                row_audit["all_hard_integrity_valid"]
            ),
            "decoder_schema_exact": (
                access_memory_terminal.get("schema")
                == ACCESS_MEMORY_SNAPSHOT_SCHEMA
            ),
            "decoder_strategy_exact": (
                access_memory_terminal.get("strategy") == "fifo"
            ),
            "decoder_capacity_exact": (
                int(access_memory_terminal.get("memory_capacity", -1))
                == V038_ACCESS_MEMORY_CAPACITY
            ),
            "decoder_neighbors_exact": (
                int(access_memory_terminal.get("neighbors", -1))
                == V038_ACCESS_NEIGHBORS
            ),
            "decoder_memory_bounded": (
                int(
                    access_memory_terminal.get(
                        "maximum_class_memory_size", -1
                    )
                )
                <= V038_ACCESS_MEMORY_CAPACITY
            ),
            "decoder_class_count_exact": (
                int(access_memory_terminal.get("class_count", -1))
                == expected_class_count
                and len(class_sizes) == expected_class_count
                and len(class_updates) == expected_class_count
            ),
            "decoder_class_updates_nonnegative": all(
                value >= 0 for value in class_updates
            ),
            "decoder_memory_sizes_match_updates": bool(
                len(class_sizes) == len(class_updates)
                and all(
                    size == min(updates, V038_ACCESS_MEMORY_CAPACITY)
                    for size, updates in zip(
                        class_sizes,
                        class_updates,
                        strict=True,
                    )
                )
            ),
            "decoder_updates_internally_consistent": (
                terminal_update_count > 0
                and sum(class_updates) == terminal_update_count
            ),
            "decoder_update_trace_fields_present": bool(
                row_audit["access_update_trace_fields_present"]
            ),
            "decoder_update_trace_stepwise_consistent": bool(
                row_audit["access_update_trace_stepwise_consistent"]
            ),
            "decoder_update_trace_terminal_matches_snapshot": (
                terminal_update_count
                == int(row_audit["terminal_access_update_count"])
            ),
        }
        if summary.get("integrity") != expected_integrity:
            raise RuntimeError(
                f"recomputed integrity vector disagrees for seed {seed}"
            )
        recomputed_g01 = bool(all(expected_integrity.values()))
        if bool(summary.get("endpoints", {}).get("G01_integrity")) != recomputed_g01:
            raise RuntimeError(
                f"recomputed endpoint G01_integrity disagrees for seed {seed}"
            )
        for endpoint, recomputed in row_audit[
            "recomputed_endpoints"
        ].items():
            if bool(summary["endpoints"].get(endpoint)) != recomputed:
                raise RuntimeError(
                    f"recomputed endpoint {endpoint} disagrees for seed {seed}"
                )

        start = json.loads(
            (directory / "start_receipt.json").read_text(encoding="utf-8")
        )
        finish = json.loads(
            (directory / "finish_receipt.json").read_text(encoding="utf-8")
        )
        start_required = {
            "schema": "rrct.v038.start_receipt.v1",
            "version": V038_VERSION,
            "attempt_id": attempt_id,
            "seed": int(seed),
            "freeze_sha256": verified["freeze_sha256"],
            "source_archive": archive_name,
            "source_archive_sha256": frozen_archive_sha,
            "expected_transition_count": int(V037_D1_CONFIG.total_steps),
            "row_fsync": True,
            "seed_claimed_before_rng_construction": True,
        }
        for key, value in start_required.items():
            if start.get(key) != value:
                raise RuntimeError(
                    f"start receipt {key} mismatch for seed {seed}"
                )
        finish_required = {
            "schema": "rrct.v038.finish_receipt.v1",
            "version": V038_VERSION,
            "attempt_id": attempt_id,
            "seed": int(seed),
            "freeze_sha256": verified["freeze_sha256"],
            "source_archive_sha256": frozen_archive_sha,
            "rows_count": row_audit["row_count"],
            "rows_sha256": row_audit["rows_sha256"],
            "summary_sha256": artifacts[V038_SUMMARY_ARTIFACT],
            "start_receipt_sha256": artifacts["start_receipt.json"],
            "endpoints_sha256": _json_sha256(summary["endpoints"]),
            "status": summary["status"],
            "all_endpoints_met": bool(summary["all_endpoints_met"]),
        }
        for key, value in finish_required.items():
            if finish.get(key) != value:
                raise RuntimeError(
                    f"finish receipt {key} mismatch for seed {seed}"
                )

        claim_audit: dict[str, Any] = {}
        for kind in ("attempt", "seed"):
            relative = Path(str(start.get(f"{kind}_claim")))
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError(
                    f"{kind} claim path is unsafe for seed {seed}"
                )
            claim_path = (campaign_root / relative).resolve()
            if not claim_path.is_relative_to(campaign_root):
                raise RuntimeError(
                    f"{kind} claim escapes the campaign for seed {seed}"
                )
            expected_claim_sha = start.get(f"{kind}_claim_sha256")
            if (
                not claim_path.is_file()
                or _sha256_file(claim_path) != expected_claim_sha
            ):
                raise RuntimeError(
                    f"{kind} claim hash mismatch for seed {seed}"
                )
            claim = json.loads(claim_path.read_text(encoding="utf-8"))
            claim_required = {
                "schema": "rrct.v038.campaign_claim.v1",
                "version": V038_VERSION,
                "attempt_id": attempt_id,
                "seed": int(seed),
                "freeze_sha256": verified["freeze_sha256"],
                "state": "consumed_before_rng_construction",
            }
            for key, value in claim_required.items():
                if claim.get(key) != value:
                    raise RuntimeError(
                        f"{kind} claim {key} mismatch for seed {seed}"
                    )
            claim_audit[kind] = {
                "path": relative.as_posix(),
                "sha256": expected_claim_sha,
            }

        summaries[int(seed)] = summary
        try:
            directory_label = directory.relative_to(
                V038_PROJECT_ROOT.resolve()
            ).as_posix()
        except ValueError:
            directory_label = directory.as_posix()
        evidence_audit[str(seed)] = {
            "directory": directory_label,
            "row_audit": row_audit,
            "artifact_checks": artifact_checks,
            "claim_audit": claim_audit,
            "start_receipt_sha256": artifacts["start_receipt.json"],
            "finish_receipt_sha256": artifacts["finish_receipt.json"],
        }
    cohort = _build_v038_cohort_summary(summaries)
    cohort["freeze_sha256"] = verified["freeze_sha256"]
    cohort["source_archive_sha256"] = verified["freeze"]["source_archive"][
        "sha256"
    ]
    cohort["evidence_audit"] = evidence_audit
    return cohort


def _main() -> None:
    parser = argparse.ArgumentParser(
        description="RRCT v0.38 access-generalization experiment"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("verify-freeze")
    run_parser = subparsers.add_parser("run-pilot")
    run_parser.add_argument("--seed", type=int, required=True)
    run_parser.add_argument("--attempt-id", required=True)
    run_parser.add_argument("--campaign-root", type=Path)
    run_parser.add_argument("--progress-every", type=int, default=240)
    aggregate_parser = subparsers.add_parser("aggregate")
    aggregate_parser.add_argument(
        "--campaign-root", type=Path, default=V038_CAMPAIGN_ROOT
    )
    aggregate_parser.add_argument(
        "--output",
        type=Path,
        default=V038_VALIDATION_ROOT / V038_COHORT_ARTIFACT,
    )
    arguments = parser.parse_args()
    if arguments.command == "verify-freeze":
        verified = verify_v038_preoutcome_freeze()
        print(
            json.dumps(
                {
                    "status": "V038_FREEZE_VERIFIED",
                    "freeze_sha256": verified["freeze_sha256"],
                    "source_archive": str(verified["source_archive_path"]),
                },
                sort_keys=True,
            )
        )
        return
    if arguments.command == "aggregate":
        summary = aggregate_v038_campaign(arguments.campaign_root)
        _exclusive_json(arguments.output, summary)
        print(json.dumps(_jsonable(summary), indent=2, sort_keys=True))
        if not summary["cohort_target_met"]:
            raise SystemExit(2)
        return
    output, summary = run_claimed_v038_pilot(
        arguments.seed,
        arguments.attempt_id,
        campaign_root=(arguments.campaign_root or V038_CAMPAIGN_ROOT),
        progress_every=arguments.progress_every,
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "status": summary["status"],
                "endpoints": summary["endpoints"],
            },
            sort_keys=True,
        )
    )


__all__ = [
    "V038_ACCESS_MEMORY_CAPACITY",
    "V038_ACCESS_MODE",
    "V038_ACCESS_NEIGHBORS",
    "V038_PILOT_SEEDS",
    "aggregate_v038_campaign",
    "run_claimed_v038_pilot",
    "run_access_generalization_trace",
    "verify_v038_preoutcome_freeze",
    "write_v038_evidence",
]


if __name__ == "__main__":
    _main()
