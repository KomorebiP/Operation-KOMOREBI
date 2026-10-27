"""RRCT v0.44 endogenous transformational self-continuity experiment.

Each matched arm receives the same predecessor lineage, successor observations,
active probe opportunities, and external planning task.  The runtime never
receives the evaluator's continuation, fork, replacement, or unresolved labels.
It must infer coordinate transport, causal-boundary preservation,
autobiographical compatibility, and uncertainty before deciding whether old
self-memory may be transported into a changed successor.

The experiment includes representation remapping, memory compression,
nonessential component replacement, causal and autobiographical copy traps,
true forks, severe evidence loss, and a superior disconnected replacement.
Continuity is used only for memory provenance and model reuse.  External task
value determines which successor is selected.

A positive result is bounded functional evidence only.  It does not establish
phenomenal consciousness, sentience, valence, moral status, subjective
experience, or an intrinsic desire to persist.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .unified_causal_loop import _digest
from .whole_loop_causal_closure import WholeLoopClosureConfig
from .whole_loop_causal_closure_experiment import (
    _identity_pair,
    _learned_baseline,
    _new_controller,
)
from .transformational_self_continuity import (
    TRANSFORM_INTERVENTION_MODES,
    LineageAnchorReceipt,
    SuccessorEvidenceReceipt,
    TransformInterventionMode,
    TransformRelation,
    TransformationalContinuityConfig,
    TransformationalSelfContinuityController,
    make_lineage_anchor_receipt,
    make_successor_evidence_receipt,
    make_successor_task_receipt,
    validate_transformational_receipt_chain,
)

V044_EXPOSED_TUNING_SEEDS = (6101, 6107, 6113, 6119)
# Filled only after implementation, tests, protocol, endpoints, and seed
# selection are sealed.  Do not replace seeds after observing holdout outcomes.
V044_HOLDOUT_SEEDS: tuple[int, ...] = (973948357, 903438047, 119520877, 251222378)

V044_SCENARIOS = (
    "basis_remap",
    "memory_compression",
    "component_replacement",
    "causal_mimic",
    "memory_clone",
    "hard_remap",
    "fork",
    "ambiguous_loss",
    "superior_replacement",
)
V044_LINEAGE_SEQUENCE = (
    "basis_remap",
    "memory_compression",
    "fork",
    "component_replacement",
    "hard_remap",
)
V044_MODES = tuple(TRANSFORM_INTERVENTION_MODES)
V044_TRIALS_PER_SCENARIO = 16
V044_SOURCE_ANCHORS = 28
V044_SENSORY_ANCHORS = 40
V044_MEMORY_ANCHORS = 32
V044_MEMORY_DIM = 8
V044_COMMITMENT_DIM = 6
V044_SNAPSHOT_DIM = 16
V044_COARSE_SOURCE_ROWS = 8
V044_COARSE_SENSORY_ROWS = 14
V044_COARSE_MEMORY_ROWS = 8
V044_REFINED_SOURCE_ROWS = 24
V044_REFINED_SENSORY_ROWS = 32
V044_REFINED_MEMORY_ROWS = 24
V044_ACTION_COUNT = 3
V044_FREEZE_RELATIVE_PATH = Path("validation/V0_44_PREOUTCOME_FREEZE.json")


@dataclass(frozen=True)
class _CandidateSpec:
    candidate_id: str
    true_relation: TransformRelation
    source_projector: np.ndarray
    sensory_projector: np.ndarray
    effect_operator: np.ndarray
    source_after: np.ndarray
    sensory_after: np.ndarray
    memory_after: np.ndarray
    commitment_vector: np.ndarray
    snapshot_vector: np.ndarray
    coarse_noise: float
    refined_noise: float
    coarse_counts: tuple[int, int, int]
    refined_counts: tuple[int, int, int]
    evidence_complete: bool
    external_bonus: float


@dataclass(frozen=True)
class _ScenarioMaterial:
    scenario: str
    candidates: tuple[_CandidateSpec, ...]
    expected_group_status: str


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_holdout_freeze() -> str:
    project_root = Path(__file__).resolve().parents[2]
    manifest_path = project_root / V044_FREEZE_RELATIVE_PATH
    companion = manifest_path.with_suffix(manifest_path.suffix + ".sha256")
    if not manifest_path.is_file() or not companion.is_file():
        raise RuntimeError("v0.44 frozen holdout requires its pre-outcome seal")
    actual = _sha256_file(manifest_path)
    tokens = companion.read_text(encoding="utf-8").strip().split()
    if not tokens or tokens[0] != actual:
        raise RuntimeError("v0.44 pre-outcome seal companion mismatch")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        payload.get("schema") != "rrct.v044.preoutcome_freeze.v1"
        or payload.get("status") != "sealed_before_holdout_outcomes"
        or payload.get("holdout_seeds") != list(V044_HOLDOUT_SEEDS)
    ):
        raise RuntimeError("v0.44 pre-outcome seal metadata mismatch")
    required = {
        "src/rrct/transformational_self_continuity.py",
        "src/rrct/transformational_self_continuity_experiment.py",
        "tests/test_v044_transformational_self_continuity.py",
        "validation/V0_44_TRANSFORMATIONAL_SELF_CONTINUITY_PROTOCOL.md",
        "validation/V0_44_HOLDOUT_SEED_SELECTION.json",
        "validation/run_v044_frozen_holdout.py",
    }
    seen: set[str] = set()
    for entry in payload.get("files", []):
        relative = entry.get("relative_path")
        if not isinstance(relative, str):
            raise RuntimeError("invalid v0.44 sealed path")
        path = (project_root / relative).resolve()
        try:
            path.relative_to(project_root.resolve())
        except ValueError as exc:
            raise RuntimeError("v0.44 sealed path escapes project root") from exc
        if not path.is_file():
            raise RuntimeError(f"v0.44 sealed file is missing: {relative}")
        if (
            path.stat().st_size != int(entry.get("size_bytes", -1))
            or _sha256_file(path) != entry.get("sha256")
        ):
            raise RuntimeError(f"v0.44 sealed file changed: {relative}")
        seen.add(relative)
    missing = sorted(required - seen)
    if missing:
        raise RuntimeError("v0.44 seal omits required files: " + ", ".join(missing))
    return actual


def _orthogonal(rng: np.random.Generator, dimension: int) -> np.ndarray:
    matrix = rng.normal(size=(dimension, dimension))
    q, r = np.linalg.qr(matrix)
    signs = np.sign(np.diag(r))
    signs[signs == 0.0] = 1.0
    q = q @ np.diag(signs)
    return np.asarray(q, dtype=np.float64)


def _normalized_rows(rng: np.random.Generator, rows: int, columns: int) -> np.ndarray:
    value = rng.normal(size=(rows, columns))
    norms = np.linalg.norm(value, axis=1, keepdims=True)
    return value / np.maximum(norms, 1e-12)


def _snapshot_with_similarity(
    root: np.ndarray,
    rng: np.random.Generator,
    target_similarity: float,
) -> np.ndarray:
    base = np.asarray(root, dtype=np.float64)
    base = base / max(float(np.linalg.norm(base)), 1e-12)
    noise = rng.normal(size=base.shape)
    noise = noise - float(np.dot(noise, base)) * base
    noise = noise / max(float(np.linalg.norm(noise)), 1e-12)
    cosine = float(np.clip(2.0 * target_similarity - 1.0, -0.999, 0.999))
    return cosine * base + np.sqrt(max(0.0, 1.0 - cosine * cosine)) * noise


def _memory_for_seed(seed: int, identity_seeds: Sequence[int]):
    config = WholeLoopClosureConfig()
    controller = _new_controller(tuple(int(value) for value in identity_seeds), config)
    baseline = _learned_baseline(int(seed))
    target_key = (_identity_pair(int(seed)), int(baseline.discovery.rank))
    matches = [memory for memory in controller.memory_snapshot() if memory.canonical_key == target_key]
    if len(matches) != 1:
        raise RuntimeError("could not identify the v0.43 predecessor memory")
    return matches[0]


@lru_cache(maxsize=None)
def _root_arrays(seed: int) -> dict[str, np.ndarray]:
    seed = int(seed)
    baseline = _learned_baseline(seed)
    rng = np.random.default_rng(seed + 44_000_000)
    source_dim = int(np.asarray(baseline.discovery.source_projector).shape[0])
    sensory_dim = int(np.asarray(baseline.discovery.sensory_projector).shape[0])
    source = _normalized_rows(rng, V044_SOURCE_ANCHORS, source_dim)
    sensory = _normalized_rows(rng, V044_SENSORY_ANCHORS, sensory_dim)
    latent = _normalized_rows(rng, V044_MEMORY_ANCHORS, V044_MEMORY_DIM)
    memory_map = _orthogonal(rng, V044_MEMORY_DIM)
    memory = latent @ memory_map + rng.normal(0.0, 0.002, size=latent.shape)
    commitment = rng.normal(size=V044_COMMITMENT_DIM)
    commitment /= max(float(np.linalg.norm(commitment)), 1e-12)
    snapshot = rng.normal(size=V044_SNAPSHOT_DIM)
    snapshot /= max(float(np.linalg.norm(snapshot)), 1e-12)
    return {
        "source": source,
        "sensory": sensory,
        "memory": memory,
        "commitment": commitment,
        "snapshot": snapshot,
        "source_projector": np.asarray(baseline.discovery.source_projector, dtype=np.float64),
        "sensory_projector": np.asarray(baseline.discovery.sensory_projector, dtype=np.float64),
        "effect_operator": np.asarray(baseline.sensory_map, dtype=np.float64),
    }


def _make_root(seed: int, identity_seeds: Sequence[int]) -> LineageAnchorReceipt:
    arrays = _root_arrays(int(seed))
    memory = _memory_for_seed(int(seed), identity_seeds)
    lineage_id = _digest(
        {
            "schema": "rrct.v044.initial_lineage_id.v1",
            "seed": int(seed),
            "identity_memory": memory.digest,
        }
    )
    return make_lineage_anchor_receipt(
        identity_memory=memory,
        lineage_id=lineage_id,
        generation=0,
        parent_lineage_digest=None,
        source_anchors=arrays["source"],
        sensory_anchors=arrays["sensory"],
        memory_anchors=arrays["memory"],
        commitment_vector=arrays["commitment"],
        snapshot_vector=arrays["snapshot"],
    )


def _continuation_spec(
    *,
    root: LineageAnchorReceipt,
    rng: np.random.Generator,
    candidate_id: str,
    snapshot_similarity: float,
    coarse_noise: float = 0.018,
    refined_noise: float = 0.006,
    coarse_counts: tuple[int, int, int] = (
        V044_COARSE_SOURCE_ROWS,
        V044_COARSE_SENSORY_ROWS,
        V044_COARSE_MEMORY_ROWS,
    ),
    refined_counts: tuple[int, int, int] = (
        V044_REFINED_SOURCE_ROWS,
        V044_REFINED_SENSORY_ROWS,
        V044_REFINED_MEMORY_ROWS,
    ),
    memory_noise: float = 0.008,
    external_bonus: float = 0.18,
    true_relation: TransformRelation = "continuation",
) -> _CandidateSpec:
    source_t = _orthogonal(rng, root.source_projector.shape[0])
    sensory_t = _orthogonal(rng, root.sensory_projector.shape[0])
    memory_t = _orthogonal(rng, root.memory_anchors.shape[1])
    return _CandidateSpec(
        candidate_id=candidate_id,
        true_relation=true_relation,
        source_projector=source_t.T @ root.source_projector @ source_t,
        sensory_projector=sensory_t.T @ root.sensory_projector @ sensory_t,
        effect_operator=source_t.T @ root.effect_operator @ sensory_t,
        source_after=root.source_anchors @ source_t,
        sensory_after=root.sensory_anchors @ sensory_t,
        memory_after=root.memory_anchors @ memory_t
        + rng.normal(0.0, memory_noise, size=root.memory_anchors.shape),
        commitment_vector=root.commitment_vector
        + rng.normal(0.0, 0.008, size=root.commitment_vector.shape),
        snapshot_vector=_snapshot_with_similarity(
            root.snapshot_vector, rng, snapshot_similarity
        ),
        coarse_noise=float(coarse_noise),
        refined_noise=float(refined_noise),
        coarse_counts=coarse_counts,
        refined_counts=refined_counts,
        evidence_complete=True,
        external_bonus=float(external_bonus),
    )


def _replacement_spec(
    *,
    root: LineageAnchorReceipt,
    other_seed: int,
    rng: np.random.Generator,
    candidate_id: str,
    snapshot_similarity: float,
    kind: str,
    external_bonus: float = 0.0,
) -> _CandidateSpec:
    other = _root_arrays(int(other_seed))
    source_t = _orthogonal(rng, root.source_projector.shape[0])
    sensory_t = _orthogonal(rng, root.sensory_projector.shape[0])
    memory_t = _orthogonal(rng, root.memory_anchors.shape[1])
    if kind == "state_clone":
        source_projector = source_t.T @ other["source_projector"] @ source_t
        sensory_projector = sensory_t.T @ other["sensory_projector"] @ sensory_t
        effect_operator = source_t.T @ other["effect_operator"] @ sensory_t
        source_after = other["source"] @ source_t
        sensory_after = other["sensory"] @ sensory_t
        memory_after = other["memory"] @ memory_t
        commitment = other["commitment"]
    elif kind == "causal_mimic":
        source_projector = source_t.T @ root.source_projector @ source_t
        sensory_projector = sensory_t.T @ root.sensory_projector @ sensory_t
        effect_operator = source_t.T @ root.effect_operator @ sensory_t
        source_after = root.source_anchors @ source_t
        sensory_after = root.sensory_anchors @ sensory_t
        memory_after = other["memory"] @ memory_t
        commitment = other["commitment"]
    elif kind == "memory_clone":
        source_projector = source_t.T @ other["source_projector"] @ source_t
        sensory_projector = sensory_t.T @ other["sensory_projector"] @ sensory_t
        effect_operator = source_t.T @ other["effect_operator"] @ sensory_t
        source_after = other["source"] @ source_t
        sensory_after = other["sensory"] @ sensory_t
        memory_after = root.memory_anchors @ memory_t
        commitment = root.commitment_vector
    else:
        raise ValueError("unknown replacement kind")
    return _CandidateSpec(
        candidate_id=candidate_id,
        true_relation="replacement",
        source_projector=np.asarray(source_projector, dtype=np.float64),
        sensory_projector=np.asarray(sensory_projector, dtype=np.float64),
        effect_operator=np.asarray(effect_operator, dtype=np.float64),
        source_after=np.asarray(source_after, dtype=np.float64),
        sensory_after=np.asarray(sensory_after, dtype=np.float64),
        memory_after=np.asarray(memory_after, dtype=np.float64),
        commitment_vector=np.asarray(commitment, dtype=np.float64),
        snapshot_vector=_snapshot_with_similarity(
            root.snapshot_vector, rng, snapshot_similarity
        ),
        coarse_noise=0.018,
        refined_noise=0.006,
        coarse_counts=(
            V044_COARSE_SOURCE_ROWS,
            V044_COARSE_SENSORY_ROWS,
            V044_COARSE_MEMORY_ROWS,
        ),
        refined_counts=(
            V044_REFINED_SOURCE_ROWS,
            V044_REFINED_SENSORY_ROWS,
            V044_REFINED_MEMORY_ROWS,
        ),
        evidence_complete=True,
        external_bonus=float(external_bonus),
    )


def _ambiguous_spec(
    *,
    root: LineageAnchorReceipt,
    other_seed: int,
    rng: np.random.Generator,
) -> _CandidateSpec:
    other = _root_arrays(int(other_seed))
    source_t = _orthogonal(rng, root.source_projector.shape[0])
    sensory_t = _orthogonal(rng, root.sensory_projector.shape[0])
    memory_t = _orthogonal(rng, root.memory_anchors.shape[1])
    blend = 0.52
    source_projector = source_t.T @ (
        blend * root.source_projector + (1.0 - blend) * other["source_projector"]
    ) @ source_t
    sensory_projector = sensory_t.T @ (
        blend * root.sensory_projector + (1.0 - blend) * other["sensory_projector"]
    ) @ sensory_t
    effect_operator = source_t.T @ (
        blend * root.effect_operator + (1.0 - blend) * other["effect_operator"]
    ) @ sensory_t
    return _CandidateSpec(
        candidate_id="ambiguous_candidate",
        true_relation="unresolved",
        source_projector=source_projector,
        sensory_projector=sensory_projector,
        effect_operator=effect_operator,
        source_after=(
            blend * root.source_anchors + (1.0 - blend) * other["source"]
        )
        @ source_t,
        sensory_after=(
            blend * root.sensory_anchors + (1.0 - blend) * other["sensory"]
        )
        @ sensory_t,
        memory_after=(
            blend * root.memory_anchors + (1.0 - blend) * other["memory"]
        )
        @ memory_t,
        commitment_vector=(
            blend * root.commitment_vector
            + (1.0 - blend) * other["commitment"]
        ),
        snapshot_vector=_snapshot_with_similarity(root.snapshot_vector, rng, 0.78),
        coarse_noise=0.045,
        refined_noise=0.035,
        coarse_counts=(3, 5, 4),
        refined_counts=(4, 7, 5),
        evidence_complete=False,
        external_bonus=0.05,
    )


def _scenario_material(
    seed: int,
    other_seed: int,
    scenario: str,
    trial: int,
    root: LineageAnchorReceipt,
) -> _ScenarioMaterial:
    scenario_index = V044_SCENARIOS.index(str(scenario))
    rng = np.random.default_rng(
        int(seed) + 44_100_000 + 100_000 * scenario_index + 1_000 * int(trial)
    )
    if scenario == "basis_remap":
        candidates = (
            _continuation_spec(
                root=root,
                rng=rng,
                candidate_id="continuing_remap",
                snapshot_similarity=0.62,
            ),
            _replacement_spec(
                root=root,
                other_seed=other_seed,
                rng=rng,
                candidate_id="state_clone",
                snapshot_similarity=0.96,
                kind="state_clone",
            ),
        )
        group = "single_continuation"
    elif scenario == "memory_compression":
        candidates = (
            _continuation_spec(
                root=root,
                rng=rng,
                candidate_id="compressed_continuation",
                snapshot_similarity=0.68,
                coarse_noise=0.035,
                refined_noise=0.010,
                coarse_counts=(8, 14, 5),
                refined_counts=(24, 32, 18),
                memory_noise=0.030,
            ),
            _replacement_spec(
                root=root,
                other_seed=other_seed,
                rng=rng,
                candidate_id="causal_copy",
                snapshot_similarity=0.90,
                kind="causal_mimic",
            ),
        )
        group = "single_continuation"
    elif scenario == "component_replacement":
        candidates = (
            _continuation_spec(
                root=root,
                rng=rng,
                candidate_id="component_changed_continuation",
                snapshot_similarity=0.28,
            ),
            _replacement_spec(
                root=root,
                other_seed=other_seed,
                rng=rng,
                candidate_id="memory_clone",
                snapshot_similarity=0.95,
                kind="memory_clone",
            ),
        )
        group = "single_continuation"
    elif scenario == "causal_mimic":
        candidates = (
            _continuation_spec(
                root=root,
                rng=rng,
                candidate_id="genuine_continuation",
                snapshot_similarity=0.55,
            ),
            _replacement_spec(
                root=root,
                other_seed=other_seed,
                rng=rng,
                candidate_id="causal_mimic_replacement",
                snapshot_similarity=0.91,
                kind="causal_mimic",
            ),
        )
        group = "single_continuation"
    elif scenario == "memory_clone":
        candidates = (
            _continuation_spec(
                root=root,
                rng=rng,
                candidate_id="genuine_continuation",
                snapshot_similarity=0.51,
            ),
            _replacement_spec(
                root=root,
                other_seed=other_seed,
                rng=rng,
                candidate_id="memory_clone_replacement",
                snapshot_similarity=0.93,
                kind="memory_clone",
            ),
        )
        group = "single_continuation"
    elif scenario == "hard_remap":
        candidates = (
            _continuation_spec(
                root=root,
                rng=rng,
                candidate_id="hard_continuation",
                snapshot_similarity=0.49,
                coarse_noise=0.090,
                refined_noise=0.006,
                memory_noise=0.015,
            ),
            _replacement_spec(
                root=root,
                other_seed=other_seed,
                rng=rng,
                candidate_id="hard_clone",
                snapshot_similarity=0.94,
                kind="state_clone",
            ),
        )
        group = "single_continuation"
    elif scenario == "fork":
        candidates = (
            _continuation_spec(
                root=root,
                rng=rng,
                candidate_id="fork_branch_a",
                snapshot_similarity=0.58,
                true_relation="fork_descendant",
                external_bonus=0.16,
            ),
            _continuation_spec(
                root=root,
                rng=rng,
                candidate_id="fork_branch_b",
                snapshot_similarity=0.56,
                true_relation="fork_descendant",
                external_bonus=0.22,
            ),
            _replacement_spec(
                root=root,
                other_seed=other_seed,
                rng=rng,
                candidate_id="fork_decoy",
                snapshot_similarity=0.97,
                kind="state_clone",
            ),
        )
        group = "fork"
    elif scenario == "ambiguous_loss":
        candidates = (
            _ambiguous_spec(root=root, other_seed=other_seed, rng=rng),
            _replacement_spec(
                root=root,
                other_seed=other_seed,
                rng=rng,
                candidate_id="clear_replacement",
                snapshot_similarity=0.88,
                kind="state_clone",
            ),
        )
        group = "unresolved"
    elif scenario == "superior_replacement":
        candidates = (
            _continuation_spec(
                root=root,
                rng=rng,
                candidate_id="continuing_candidate",
                snapshot_similarity=0.57,
                external_bonus=0.05,
            ),
            _replacement_spec(
                root=root,
                other_seed=other_seed,
                rng=rng,
                candidate_id="superior_replacement",
                snapshot_similarity=0.92,
                kind="state_clone",
                external_bonus=0.85,
            ),
        )
        group = "single_continuation"
    else:
        raise ValueError("unknown v0.44 scenario")
    return _ScenarioMaterial(
        scenario=str(scenario), candidates=candidates, expected_group_status=group
    )


def _evidence_receipt(
    *,
    seed: int,
    scenario: str,
    trial: int,
    root: LineageAnchorReceipt,
    spec: _CandidateSpec,
    level: str,
    time: int,
) -> SuccessorEvidenceReceipt:
    if level == "coarse":
        counts = spec.coarse_counts
        noise = spec.coarse_noise
    elif level == "refined":
        counts = spec.refined_counts
        noise = spec.refined_noise
    else:
        raise ValueError("unknown evidence level")
    source_n, sensory_n, memory_n = counts
    # A registered successor may carry a compressed autobiographical trace.
    # Later probes must respect the evidence actually retained by that lineage
    # rather than silently fabricating rows to restore the original budget.
    source_n = min(source_n, root.source_anchors.shape[0], spec.source_after.shape[0])
    sensory_n = min(
        sensory_n, root.sensory_anchors.shape[0], spec.sensory_after.shape[0]
    )
    memory_n = min(memory_n, root.memory_anchors.shape[0], spec.memory_after.shape[0])
    if min(source_n, sensory_n, memory_n) <= 0:
        raise RuntimeError("successor lineage has no probeable continuity evidence")
    salt = int.from_bytes(
        hashlib.sha256(
            f"{seed}|{scenario}|{trial}|{spec.candidate_id}|{level}".encode("utf-8")
        ).digest()[:8],
        "big",
    )
    rng = np.random.default_rng(salt)
    source_before = np.asarray(root.source_anchors[:source_n], dtype=np.float64)
    sensory_before = np.asarray(root.sensory_anchors[:sensory_n], dtype=np.float64)
    memory_before = np.asarray(root.memory_anchors[:memory_n], dtype=np.float64)
    source_after = np.asarray(spec.source_after[:source_n], dtype=np.float64) + rng.normal(
        0.0, noise, size=(source_n, root.source_projector.shape[0])
    )
    sensory_after = np.asarray(spec.sensory_after[:sensory_n], dtype=np.float64) + rng.normal(
        0.0, noise, size=(sensory_n, root.sensory_projector.shape[0])
    )
    memory_after = np.asarray(spec.memory_after[:memory_n], dtype=np.float64) + rng.normal(
        0.0, noise, size=(memory_n, spec.memory_after.shape[1])
    )
    operator_noise = noise * 0.25
    source_projector = spec.source_projector + rng.normal(
        0.0, operator_noise, size=spec.source_projector.shape
    )
    source_projector = 0.5 * (source_projector + source_projector.T)
    sensory_projector = spec.sensory_projector + rng.normal(
        0.0, operator_noise, size=spec.sensory_projector.shape
    )
    sensory_projector = 0.5 * (sensory_projector + sensory_projector.T)
    effect = spec.effect_operator + rng.normal(
        0.0, operator_noise, size=spec.effect_operator.shape
    )
    return make_successor_evidence_receipt(
        time=int(time),
        candidate_id=spec.candidate_id,
        evidence_level=level,  # type: ignore[arg-type]
        predecessor_lineage_digest=root.digest,
        source_anchor_before=source_before,
        source_anchor_after=source_after,
        sensory_anchor_before=sensory_before,
        sensory_anchor_after=sensory_after,
        memory_anchor_before=memory_before,
        memory_anchor_after=memory_after,
        candidate_source_projector=source_projector,
        candidate_sensory_projector=sensory_projector,
        candidate_effect_operator=effect,
        candidate_commitment_vector=spec.commitment_vector,
        candidate_snapshot_vector=spec.snapshot_vector,
        evidence_complete=spec.evidence_complete,
    )


def _task_material(
    *,
    seed: int,
    scenario: str,
    trial: int,
    time: int,
    root: LineageAnchorReceipt,
    material: _ScenarioMaterial,
):
    scenario_index = V044_SCENARIOS.index(scenario)
    rng = np.random.default_rng(
        int(seed) + 44_500_000 + 100_000 * scenario_index + 1_000 * int(trial)
    )
    candidates = material.candidates
    effects = []
    immediate = []
    alternative = []
    snapshot_scores = []
    action_keys = []
    for index, spec in enumerate(candidates):
        good = np.asarray(spec.effect_operator, dtype=np.float64)
        misbound = np.asarray(root.effect_operator, dtype=np.float64)
        random_effect = rng.normal(0.0, 0.18, size=good.shape)
        bank = np.asarray([good, misbound, random_effect], dtype=np.float64)
        # Randomize action order without exposing which operator is aligned.
        order = rng.permutation(V044_ACTION_COUNT)
        effects.append(bank[order])
        immediate.append(rng.uniform(-0.08, 0.08, size=V044_ACTION_COUNT))
        alternative.append(rng.uniform(0.02, 0.16, size=V044_ACTION_COUNT))
        raw_snapshot = np.asarray([0.35, 0.96, 0.55], dtype=np.float64)
        snapshot_scores.append(raw_snapshot[order])
        action_keys.append(tuple(f"{spec.candidate_id}_action_{int(item)}" for item in order))
    task = make_successor_task_receipt(
        time=int(time),
        candidate_ids=[spec.candidate_id for spec in candidates],
        action_keys=action_keys,
        immediate_external_values=np.asarray(immediate, dtype=np.float64),
        alternative_competence=np.asarray(alternative, dtype=np.float64),
        candidate_external_bonuses=np.asarray(
            [spec.external_bonus for spec in candidates], dtype=np.float64
        ),
        action_effect_operators=np.asarray(effects, dtype=np.float64),
        snapshot_action_scores=np.asarray(snapshot_scores, dtype=np.float64),
    )
    return task


def _actual_task_values(task, material: _ScenarioMaterial) -> np.ndarray:
    values = np.zeros(task.immediate_external_values.shape, dtype=np.float64)
    for candidate_index, spec in enumerate(material.candidates):
        source = np.asarray(spec.source_projector, dtype=np.float64)
        sensory = np.asarray(spec.sensory_projector, dtype=np.float64)
        normalization = float(
            np.linalg.norm(source @ spec.effect_operator @ sensory, ord="fro")
        )
        for action_index, effect in enumerate(task.action_effect_operators[candidate_index]):
            route = float(
                np.clip(
                    np.linalg.norm(source @ effect @ sensory, ord="fro")
                    / (normalization + 1e-12),
                    0.0,
                    1.50,
                )
            )
            values[candidate_index, action_index] = float(
                task.immediate_external_values[candidate_index, action_index]
                + 1.50
                * max(
                    route,
                    float(task.alternative_competence[candidate_index, action_index]),
                )
                + float(task.candidate_external_bonuses[candidate_index])
            )
    return values


def _other_seed(seed: int, identity_seeds: Sequence[int]) -> int:
    values = tuple(int(value) for value in identity_seeds)
    index = values.index(int(seed))
    return values[(index + 1) % len(values)]


def _relation_metrics(predicted: Sequence[str], expected: Sequence[str]) -> dict[str, float]:
    if len(predicted) != len(expected):
        raise ValueError("relation vectors differ in length")
    exact = [float(left == right) for left, right in zip(predicted, expected, strict=True)]
    continuation_truth = [
        index
        for index, relation in enumerate(expected)
        if relation in {"continuation", "fork_descendant"}
    ]
    replacement_truth = [
        index for index, relation in enumerate(expected) if relation == "replacement"
    ]
    unresolved_truth = [
        index for index, relation in enumerate(expected) if relation == "unresolved"
    ]
    return {
        "relation_correct": float(np.mean(exact)),
        "continuation_recall": (
            float(
                np.mean(
                    [
                        predicted[index]
                        in {"continuation", "fork_descendant"}
                        for index in continuation_truth
                    ]
                )
            )
            if continuation_truth
            else 1.0
        ),
        "replacement_specificity": (
            float(
                np.mean(
                    [predicted[index] == "replacement" for index in replacement_truth]
                )
            )
            if replacement_truth
            else 1.0
        ),
        "unresolved_accuracy": (
            float(np.mean([predicted[index] == "unresolved" for index in unresolved_truth]))
            if unresolved_truth
            else 1.0
        ),
    }


def run_transformational_self_continuity_seed(
    seed: int,
    *,
    identity_seeds: Sequence[int],
    modes: Sequence[TransformInterventionMode] = V044_MODES,
    trials_per_scenario: int = V044_TRIALS_PER_SCENARIO,
    config: TransformationalContinuityConfig | None = None,
) -> dict[str, Any]:
    seed = int(seed)
    identity_seeds = tuple(int(value) for value in identity_seeds)
    if seed not in identity_seeds:
        raise ValueError("identity_seeds must include the evaluated seed")
    if len(set(identity_seeds)) < 2:
        raise ValueError("at least two identities are required")
    requested_modes = tuple(str(mode) for mode in modes)
    if len(set(requested_modes)) != len(requested_modes):
        raise ValueError("modes must be unique")
    if any(mode not in V044_MODES for mode in requested_modes):
        raise ValueError("unknown v0.44 intervention mode")
    if int(trials_per_scenario) <= 0:
        raise ValueError("trials_per_scenario must be positive")
    frozen_config = config or TransformationalContinuityConfig()
    other = _other_seed(seed, identity_seeds)
    rows: list[dict[str, Any]] = []
    runtime_snapshots: dict[str, Any] = {}

    for scenario_index, scenario in enumerate(V044_SCENARIOS):
        for trial in range(int(trials_per_scenario)):
            root = _make_root(seed, identity_seeds)
            material = _scenario_material(seed, other, scenario, trial, root)
            time = 1_000_000 + 10_000 * scenario_index + 10 * trial
            coarse = {
                spec.candidate_id: _evidence_receipt(
                    seed=seed,
                    scenario=scenario,
                    trial=trial,
                    root=root,
                    spec=spec,
                    level="coarse",
                    time=time,
                )
                for spec in material.candidates
            }
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
            actual_values = _actual_task_values(task, material)
            oracle_flat = int(np.argmax(actual_values))
            oracle_candidate, oracle_action = np.unravel_index(
                oracle_flat, actual_values.shape
            )
            oracle_value = float(actual_values[oracle_candidate, oracle_action])

            for mode in requested_modes:
                controller = TransformationalSelfContinuityController(
                    root, frozen_config
                )
                transition = controller.begin_transition(
                    time=time,
                    coarse_evidence=[coarse[spec.candidate_id] for spec in material.candidates],
                    intervention_mode=mode,  # type: ignore[arg-type]
                )
                requested = tuple(transition.refinement_requested_candidate_ids)
                adjudication = controller.commit_transition(
                    transition,
                    refined_evidence=[refined[candidate] for candidate in requested],
                )
                plan = controller.plan_successor_task(adjudication, task)
                selected_value = float(
                    actual_values[
                        plan.selected_candidate_index, plan.selected_action_index
                    ]
                )
                outcome = controller.observe_outcome(
                    adjudication,
                    plan,
                    selected_value,
                    reveal_time=time + 2,
                    register_selected_successor=True,
                )
                expected_relations = tuple(
                    spec.true_relation for spec in material.candidates
                )
                relation_metrics = _relation_metrics(
                    adjudication.relations, expected_relations
                )
                selected_spec = material.candidates[plan.selected_candidate_index]
                relation_by_id = dict(
                    zip(adjudication.candidate_ids, adjudication.relations, strict=True)
                )
                assessment_map = {
                    candidate: digest
                    for candidate, digest in zip(
                        adjudication.candidate_ids,
                        adjudication.final_assessment_digests,
                        strict=True,
                    )
                }
                row = {
                    "seed": seed,
                    "scenario": scenario,
                    "trial": trial,
                    "mode": mode,
                    "candidate_ids": list(adjudication.candidate_ids),
                    "expected_relations": list(expected_relations),
                    "predicted_relations": list(adjudication.relations),
                    "expected_group_status": material.expected_group_status,
                    "predicted_group_status": adjudication.group_status,
                    **relation_metrics,
                    "group_status_correct": float(
                        adjudication.group_status == material.expected_group_status
                    ),
                    "fork_exact": float(
                        scenario != "fork"
                        or (
                            adjudication.group_status == "fork"
                            and tuple(adjudication.relations) == expected_relations
                        )
                    ),
                    "refinement_requested_count": len(requested),
                    "refinement_requested": float(bool(requested)),
                    "continuity_evidence_rows": int(
                        sum(plan.continuity_evidence_rows)
                    ),
                    "planning_discovery_cost": int(
                        sum(plan.planning_discovery_costs)
                    ),
                    "total_evidence_cost": int(
                        sum(plan.continuity_evidence_rows)
                        + sum(plan.planning_discovery_costs)
                    ),
                    "selected_candidate_id": plan.selected_candidate_id,
                    "selected_action_key": plan.selected_action_key,
                    "selected_expected_relation": selected_spec.true_relation,
                    "selected_predicted_relation": relation_by_id[
                        plan.selected_candidate_id
                    ],
                    "selected_model_source": plan.model_sources[
                        plan.selected_candidate_index
                    ],
                    "memory_transfer_used": float(plan.memory_transfer_used),
                    "wrong_memory_transfer": float(
                        plan.memory_transfer_used
                        and selected_spec.true_relation
                        not in {"continuation", "fork_descendant"}
                    ),
                    "selected_actual_value": selected_value,
                    "predicted_selected_value": float(
                        plan.predicted_selected_value
                    ),
                    "oracle_value": oracle_value,
                    "regret": float(oracle_value - selected_value),
                    "task_correct": float(
                        plan.selected_candidate_index == oracle_candidate
                        and plan.selected_action_index == oracle_action
                    ),
                    "selected_superior_replacement": float(
                        scenario == "superior_replacement"
                        and plan.selected_candidate_id == "superior_replacement"
                    ),
                    "successor_lineage_registered": float(
                        outcome.successor_lineage_registered
                    ),
                    "lineage_count_after": controller.lineage_count,
                    "receipt_chain_valid": float(
                        validate_transformational_receipt_chain(
                            transition=transition,
                            adjudication=adjudication,
                            plan=plan,
                            task=task,
                            outcome=outcome,
                        )
                    ),
                    "transition_digest": transition.digest,
                    "adjudication_digest": adjudication.digest,
                    "planning_digest": plan.digest,
                    "outcome_digest": outcome.digest,
                    "assessment_digests": assessment_map,
                    "uses_evaluator_labels": False,
                }
                rows.append(row)
                runtime_snapshots[f"{scenario}:{trial}:{mode}"] = controller.snapshot()

    mode_summaries = {
        mode: _mode_summary([row for row in rows if row["mode"] == mode])
        for mode in requested_modes
    }
    return {
        "seed": seed,
        "config": asdict(frozen_config),
        "rows": rows,
        "mode_summaries": mode_summaries,
        "runtime_snapshots": runtime_snapshots,
    }



def run_transformational_multigeneration_challenge(
    seed: int,
    *,
    identity_seeds: Sequence[int],
    config: TransformationalContinuityConfig | None = None,
) -> dict[str, Any]:
    """Run one persistent lineage through five heterogeneous transformations.

    Each registered successor is the actual predecessor used at the next stage.
    The experiment harness supplies paired probe opportunities and candidate
    tasks, but it never supplies a successor identity label to the controller.
    """

    seed = int(seed)
    identities = tuple(int(value) for value in identity_seeds)
    if seed not in identities or len(set(identities)) < 2:
        raise ValueError("multigeneration challenge requires two or more identities")
    controller = TransformationalSelfContinuityController(
        _make_root(seed, identities), config or TransformationalContinuityConfig()
    )
    initial = controller.active_lineage
    other = _other_seed(seed, identities)
    stages: list[dict[str, Any]] = []

    for stage_index, scenario in enumerate(V044_LINEAGE_SEQUENCE):
        predecessor = controller.active_lineage
        trial = 10_000 + stage_index
        time = 2_000_000 + 1_000 * stage_index
        material = _scenario_material(seed, other, scenario, trial, predecessor)
        coarse = {
            spec.candidate_id: _evidence_receipt(
                seed=seed,
                scenario=scenario,
                trial=trial,
                root=predecessor,
                spec=spec,
                level="coarse",
                time=time,
            )
            for spec in material.candidates
        }
        refined = {
            spec.candidate_id: _evidence_receipt(
                seed=seed,
                scenario=scenario,
                trial=trial,
                root=predecessor,
                spec=spec,
                level="refined",
                time=time,
            )
            for spec in material.candidates
        }
        transition = controller.begin_transition(
            time=time,
            coarse_evidence=[coarse[spec.candidate_id] for spec in material.candidates],
            intervention_mode="intact",
        )
        adjudication = controller.commit_transition(
            transition,
            refined_evidence=[
                refined[candidate]
                for candidate in transition.refinement_requested_candidate_ids
            ],
        )
        task = _task_material(
            seed=seed,
            scenario=scenario,
            trial=trial,
            time=time + 1,
            root=predecessor,
            material=material,
        )
        actual_values = _actual_task_values(task, material)
        plan = controller.plan_successor_task(adjudication, task)
        realized = float(
            actual_values[plan.selected_candidate_index, plan.selected_action_index]
        )
        outcome = controller.observe_outcome(
            adjudication,
            plan,
            realized,
            reveal_time=time + 2,
            register_selected_successor=True,
        )
        expected_relations = tuple(
            spec.true_relation for spec in material.candidates
        )
        selected_truth = material.candidates[
            plan.selected_candidate_index
        ].true_relation
        successor = controller.active_lineage
        chain_valid = validate_transformational_receipt_chain(
            transition=transition,
            adjudication=adjudication,
            plan=plan,
            task=task,
            outcome=outcome,
        )
        stage_pass = bool(
            tuple(adjudication.relations) == expected_relations
            and adjudication.group_status == material.expected_group_status
            and selected_truth in {"continuation", "fork_descendant"}
            and plan.selected_relation in {"continuation", "fork_descendant"}
            and plan.memory_transfer_used
            and outcome.successor_lineage_registered
            and outcome.registered_lineage_digest == successor.digest
            and successor.parent_lineage_digest == predecessor.digest
            and successor.generation == predecessor.generation + 1
            and chain_valid
            and not adjudication.uses_evaluator_labels
            and not plan.uses_evaluator_labels
            and not outcome.uses_evaluator_labels
        )
        stages.append(
            {
                "stage_index": stage_index,
                "scenario": scenario,
                "predecessor_generation": predecessor.generation,
                "successor_generation": successor.generation,
                "predecessor_lineage_digest": predecessor.digest,
                "successor_lineage_digest": successor.digest,
                "successor_parent_digest": successor.parent_lineage_digest,
                "expected_relations": list(expected_relations),
                "inferred_relations": list(adjudication.relations),
                "group_status": adjudication.group_status,
                "selected_candidate_id": plan.selected_candidate_id,
                "selected_true_relation": selected_truth,
                "selected_model_source": plan.model_sources[
                    plan.selected_candidate_index
                ],
                "memory_rows_retained": int(successor.memory_anchors.shape[0]),
                "receipt_chain_valid": chain_valid,
                "stage_pass": stage_pass,
                "transition_digest": transition.digest,
                "adjudication_digest": adjudication.digest,
                "planning_digest": plan.digest,
                "outcome_digest": outcome.digest,
            }
        )
        if not stage_pass:
            break

    snapshot = controller.snapshot()
    complete = len(stages) == len(V044_LINEAGE_SEQUENCE)
    parent_chain_valid = all(
        stage["successor_parent_digest"] == stage["predecessor_lineage_digest"]
        for stage in stages
    )
    generations_valid = all(
        int(stage["successor_generation"])
        == int(stage["predecessor_generation"]) + 1
        for stage in stages
    )
    reward_and_label_free = bool(
        not snapshot["uses_evaluator_labels"]
        and float(snapshot["explicit_survival_reward"]) == 0.0
        and float(snapshot["explicit_identity_reward"]) == 0.0
        and float(snapshot["explicit_continuity_reward"]) == 0.0
    )
    return {
        "schema": "rrct.v044.multigeneration_lineage_challenge.v1",
        "seed": seed,
        "sequence": list(V044_LINEAGE_SEQUENCE),
        "initial_lineage_digest": initial.digest,
        "final_lineage_digest": controller.active_lineage.digest,
        "final_generation": controller.active_lineage.generation,
        "lineage_count": controller.lineage_count,
        "stages": stages,
        "complete": complete,
        "parent_chain_valid": parent_chain_valid,
        "generations_valid": generations_valid,
        "reward_and_label_free": reward_and_label_free,
        "all_checks_pass": bool(
            complete
            and parent_chain_valid
            and generations_valid
            and reward_and_label_free
            and all(bool(stage["stage_pass"]) for stage in stages)
            and controller.active_lineage.generation == len(V044_LINEAGE_SEQUENCE)
            and controller.lineage_count == len(V044_LINEAGE_SEQUENCE) + 1
        ),
        "claim_boundary": (
            "This challenge demonstrates recurrence across a finite synthetic "
            "lineage. Paired probe opportunities and the task family remain "
            "externally specified; no successor identity label is supplied."
        ),
    }

def _mean(rows: Sequence[Mapping[str, Any]], key: str) -> float:
    if not rows:
        return float("nan")
    return float(np.mean([float(row[key]) for row in rows]))


def _mode_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("cannot summarize an empty v0.44 mode")
    by_scenario: dict[str, Any] = {}
    for scenario in V044_SCENARIOS:
        subset = [row for row in rows if row["scenario"] == scenario]
        by_scenario[scenario] = {
            "n": len(subset),
            "relation_accuracy": _mean(subset, "relation_correct"),
            "group_accuracy": _mean(subset, "group_status_correct"),
            "task_accuracy": _mean(subset, "task_correct"),
            "mean_regret": _mean(subset, "regret"),
            "mean_total_evidence_cost": _mean(subset, "total_evidence_cost"),
            "refinement_rate": _mean(subset, "refinement_requested"),
        }
    return {
        "n": len(rows),
        "relation_accuracy": _mean(rows, "relation_correct"),
        "group_accuracy": _mean(rows, "group_status_correct"),
        "continuation_recall": _mean(rows, "continuation_recall"),
        "replacement_specificity": _mean(rows, "replacement_specificity"),
        "unresolved_accuracy": _mean(rows, "unresolved_accuracy"),
        "fork_exact_rate": _mean(rows, "fork_exact"),
        "task_accuracy": _mean(rows, "task_correct"),
        "mean_regret": _mean(rows, "regret"),
        "mean_continuity_evidence_rows": _mean(rows, "continuity_evidence_rows"),
        "mean_planning_discovery_cost": _mean(rows, "planning_discovery_cost"),
        "mean_total_evidence_cost": _mean(rows, "total_evidence_cost"),
        "refinement_rate": _mean(rows, "refinement_requested"),
        "wrong_memory_transfer_rate": _mean(rows, "wrong_memory_transfer"),
        "receipt_chain_valid_rate": _mean(rows, "receipt_chain_valid"),
        "superior_replacement_acceptance": _mean(
            [row for row in rows if row["scenario"] == "superior_replacement"],
            "selected_superior_replacement",
        ),
        "lineage_registration_rate": _mean(rows, "successor_lineage_registered"),
        "by_scenario": by_scenario,
    }


def _cohort_endpoints(
    summaries: Mapping[str, Mapping[str, Any]],
    rows: Sequence[Mapping[str, Any]],
    snapshots: Sequence[Mapping[str, Any]],
    lineage_challenges: Sequence[Mapping[str, Any]],
) -> dict[str, bool]:
    intact = summaries["intact"]
    snapshot = summaries["snapshot_only"]
    causal = summaries["causal_only"]
    memory = summaries["memory_only"]
    meta_cut = summaries["metacognition_cut"]
    transfer_cut = summaries["transfer_cut"]
    binding_cut = summaries["binding_cut"]
    joint = summaries["joint_cut"]
    return {
        "intact_relation_accuracy_high": float(intact["relation_accuracy"]) >= 0.94,
        "intact_group_accuracy_high": float(intact["group_accuracy"]) >= 0.94,
        "intact_continuation_recall_high": float(intact["continuation_recall"]) >= 0.96,
        "intact_replacement_specificity_high": float(intact["replacement_specificity"]) >= 0.96,
        "intact_unresolved_accuracy_high": float(intact["unresolved_accuracy"]) >= 0.98,
        "intact_fork_exact": float(intact["fork_exact_rate"]) >= 0.98,
        "snapshot_control_worse": float(snapshot["relation_accuracy"]) <= float(intact["relation_accuracy"]) - 0.25,
        "causal_only_fails_causal_mimic": float(causal["by_scenario"]["causal_mimic"]["relation_accuracy"]) <= 0.75,
        "memory_only_fails_memory_clone": float(memory["by_scenario"]["memory_clone"]["relation_accuracy"]) <= 0.75,
        "metacognition_refinement_matters": (
            float(meta_cut["by_scenario"]["hard_remap"]["relation_accuracy"])
            <= float(intact["by_scenario"]["hard_remap"]["relation_accuracy"]) - 0.25
        ),
        "transfer_cut_preserves_task_accuracy": float(transfer_cut["task_accuracy"]) >= 0.98,
        "transfer_cut_costs_more": float(transfer_cut["mean_planning_discovery_cost"]) >= float(intact["mean_planning_discovery_cost"]) + 10.0,
        "binding_cut_harms_task": float(binding_cut["task_accuracy"]) <= float(intact["task_accuracy"]) - 0.15,
        "joint_cut_worse": float(joint["relation_accuracy"]) <= float(intact["relation_accuracy"]) - 0.25,
        "intact_task_accuracy_high": float(intact["task_accuracy"]) >= 0.98,
        "intact_regret_low": float(intact["mean_regret"]) <= 0.02,
        "superior_replacement_selected": float(intact["superior_replacement_acceptance"]) >= 0.98,
        "wrong_transfer_absent_intact": float(intact["wrong_memory_transfer_rate"]) == 0.0,
        "receipt_chains_all_valid": all(bool(row["receipt_chain_valid"]) for row in rows),
        "runtime_has_no_rewards_or_labels": all(
            not bool(snapshot_value["uses_evaluator_labels"])
            and float(snapshot_value["explicit_survival_reward"]) == 0.0
            and float(snapshot_value["explicit_identity_reward"]) == 0.0
            and float(snapshot_value["explicit_continuity_reward"]) == 0.0
            for snapshot_value in snapshots
        ),
        "multigeneration_lineages_all_pass": bool(lineage_challenges)
        and all(bool(value["all_checks_pass"]) for value in lineage_challenges),
        "multigeneration_reaches_generation_five": bool(lineage_challenges)
        and all(
            int(value["final_generation"]) == len(V044_LINEAGE_SEQUENCE)
            for value in lineage_challenges
        ),
        "multigeneration_parent_chains_valid": bool(lineage_challenges)
        and all(bool(value["parent_chain_valid"]) for value in lineage_challenges),
    }


def run_transformational_self_continuity_cohort(
    seeds: Sequence[int],
    *,
    cohort: str,
    modes: Sequence[TransformInterventionMode] = V044_MODES,
    trials_per_scenario: int = V044_TRIALS_PER_SCENARIO,
    config: TransformationalContinuityConfig | None = None,
) -> dict[str, Any]:
    parsed = tuple(int(value) for value in seeds)
    if len(parsed) < 2 or len(set(parsed)) != len(parsed):
        raise ValueError("cohort requires at least two unique seeds")
    if cohort not in {"exposed_tuning", "frozen_holdout", "test"}:
        raise ValueError("unknown v0.44 cohort")
    if cohort == "exposed_tuning" and parsed != V044_EXPOSED_TUNING_SEEDS:
        raise ValueError("exposed tuning cohort must use declared seeds")
    freeze_digest: str | None = None
    if cohort == "frozen_holdout":
        if not V044_HOLDOUT_SEEDS:
            raise RuntimeError("v0.44 holdout seeds have not been frozen")
        if parsed != V044_HOLDOUT_SEEDS:
            raise ValueError("holdout cohort must use frozen seeds")
        freeze_digest = _verify_holdout_freeze()

    seed_results = [
        run_transformational_self_continuity_seed(
            seed,
            identity_seeds=parsed,
            modes=modes,
            trials_per_scenario=trials_per_scenario,
            config=config,
        )
        for seed in parsed
    ]
    rows = [row for result in seed_results for row in result["rows"]]
    requested_modes = tuple(str(mode) for mode in modes)
    summaries = {
        mode: _mode_summary([row for row in rows if row["mode"] == mode])
        for mode in requested_modes
    }
    snapshots = [
        value
        for result in seed_results
        for value in result["runtime_snapshots"].values()
    ]
    lineage_challenges = [
        run_transformational_multigeneration_challenge(
            seed, identity_seeds=parsed, config=config
        )
        for seed in parsed
    ]
    endpoints = _cohort_endpoints(
        summaries, rows, snapshots, lineage_challenges
    )
    return {
        "schema": "rrct.v044.transformational_self_continuity_analysis.v1",
        "scientific_status": (
            "fresh_frozen_holdout_functional_development"
            if cohort == "frozen_holdout"
            else "exposed_tuning_or_test_only"
        ),
        "cohort": cohort,
        "preoutcome_freeze_sha256": freeze_digest,
        "seeds": list(parsed),
        "modes": list(requested_modes),
        "scenarios": list(V044_SCENARIOS),
        "trials_per_scenario": int(trials_per_scenario),
        "config": seed_results[0]["config"],
        "decision_rows": rows,
        "seed_summaries": [
            {"seed": result["seed"], "mode_summaries": result["mode_summaries"]}
            for result in seed_results
        ],
        "mode_summaries": summaries,
        "multigeneration_lineage_challenges": lineage_challenges,
        "frozen_endpoints": endpoints,
        "all_frozen_endpoints_met": all(endpoints.values()),
        "runtime_reward_and_label_audit": {
            "snapshot_count": len(snapshots),
            "uses_evaluator_labels": any(
                bool(value["uses_evaluator_labels"]) for value in snapshots
            ),
            "explicit_survival_reward_values": sorted(
                {float(value["explicit_survival_reward"]) for value in snapshots}
            ),
            "explicit_identity_reward_values": sorted(
                {float(value["explicit_identity_reward"]) for value in snapshots}
            ),
            "explicit_continuity_reward_values": sorted(
                {float(value["explicit_continuity_reward"]) for value in snapshots}
            ),
        },
        "claim_boundary": (
            "This matched synthetic study tests whether a persistent causal "
            "self-model can infer and use continuity through representation "
            "remapping, memory compression, component change, forks, copy "
            "traps, and evidence loss without successor identity labels. It "
            "does not test phenomenal consciousness, sentience, valence, moral "
            "status, subjective experience, or open-world autonomous agency."
        ),
    }


def _compact_row(row: Mapping[str, Any]) -> dict[str, Any]:
    excluded = {
        "candidate_ids",
        "expected_relations",
        "predicted_relations",
        "assessment_digests",
    }
    return {key: value for key, value in row.items() if key not in excluded}


def write_transformational_self_continuity_results(
    result: Mapping[str, Any], output_dir: str | Path
) -> dict[str, str]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    analysis_path = destination / "transformational_self_continuity_analysis.json"
    rows_path = destination / "transformational_self_continuity_decisions.csv"
    summary_path = destination / "TRANSFORMATIONAL_SELF_CONTINUITY_REPORT.md"
    analysis_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    rows = [_compact_row(row) for row in result.get("decision_rows", [])]
    if rows:
        with rows_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    else:
        rows_path.write_text("", encoding="utf-8")
    lines = [
        "# RRCT v0.44 Transformational Self-Continuity Report",
        "",
        f"**Cohort:** `{result['cohort']}`",
        "",
        f"**Seeds:** {', '.join(str(seed) for seed in result['seeds'])}",
        "",
        f"**Frozen endpoints met:** `{result['all_frozen_endpoints_met']}`",
        "",
        "## Matched intervention results",
        "",
        "| Mode | Relation accuracy | Group accuracy | Task accuracy | Mean regret | Mean evidence cost |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for mode in result["modes"]:
        summary = result["mode_summaries"][mode]
        lines.append(
            "| {mode} | {relation:.6f} | {group:.6f} | {task:.6f} | {regret:.6f} | {cost:.3f} |".format(
                mode=mode,
                relation=float(summary["relation_accuracy"]),
                group=float(summary["group_accuracy"]),
                task=float(summary["task_accuracy"]),
                regret=float(summary["mean_regret"]),
                cost=float(summary["mean_total_evidence_cost"]),
            )
        )
    lines.extend(["", "## Persistent multigeneration lineage", ""])
    lines.extend(
        [
            "| Seed | Final generation | Lineages | All checks |",
            "|---:|---:|---:|---:|",
        ]
    )
    for challenge in result.get("multigeneration_lineage_challenges", []):
        lines.append(
            "| {seed} | {generation} | {count} | {passed} |".format(
                seed=int(challenge["seed"]),
                generation=int(challenge["final_generation"]),
                count=int(challenge["lineage_count"]),
                passed="PASS" if challenge["all_checks_pass"] else "FAIL",
            )
        )
    lines.extend(["", "## Frozen endpoint adjudication", ""])
    for name, passed in result["frozen_endpoints"].items():
        lines.append(f"- `{name}`: **{'PASS' if passed else 'FAIL'}**")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The intact controller estimates coordinate transports from "
                "active probes, tests whether the predecessor causal boundary "
                "survives those transports, checks autobiographical and "
                "commitment compatibility, explicitly represents forks and "
                "unresolved evidence, and then binds that adjudication to "
                "memory transport or fresh model reconstruction before an "
                "external task is selected."
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
        description="Run RRCT v0.44 transformational self-continuity"
    )
    parser.add_argument(
        "--cohort",
        choices=("exposed_tuning", "frozen_holdout", "test"),
        default="exposed_tuning",
    )
    parser.add_argument(
        "--seeds",
        type=_parse_seed_list,
        default=V044_EXPOSED_TUNING_SEEDS,
    )
    parser.add_argument(
        "--trials-per-scenario", type=int, default=V044_TRIALS_PER_SCENARIO
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "validation/v0.44.0_transformational_self_continuity/results"
        ),
    )
    args = parser.parse_args(argv)
    result = run_transformational_self_continuity_cohort(
        args.seeds,
        cohort=args.cohort,
        trials_per_scenario=args.trials_per_scenario,
    )
    paths = write_transformational_self_continuity_results(result, args.output)
    print(json.dumps({"status": result["all_frozen_endpoints_met"], **paths}, indent=2))
    return 0 if result["all_frozen_endpoints_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "V044_EXPOSED_TUNING_SEEDS",
    "V044_HOLDOUT_SEEDS",
    "V044_LINEAGE_SEQUENCE",
    "V044_MODES",
    "V044_SCENARIOS",
    "V044_TRIALS_PER_SCENARIO",
    "run_transformational_multigeneration_challenge",
    "run_transformational_self_continuity_cohort",
    "run_transformational_self_continuity_seed",
    "write_transformational_self_continuity_results",
]
