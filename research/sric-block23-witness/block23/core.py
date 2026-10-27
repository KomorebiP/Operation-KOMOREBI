from __future__ import annotations

import dataclasses
import hashlib
import itertools
import json
import math
from typing import Any, Iterable, Mapping

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]

FAMILIES = (
    "identified",
    "answer_shortcut",
    "gauge_equivalent",
    "semantic_ambiguity",
    "partial_ontology",
    "destructive_loss",
)
SYSTEMS = ("source", "foreign")
PRE_CERTIFICATES = (
    "CANDIDATE_IDENTIFIED",
    "CANDIDATE_GAUGE_AMBIGUOUS",
    "CANDIDATE_PARTIAL",
    "NO_GO",
)
FINAL_CERTIFICATES = (
    "ONTOLOGY_IDENTIFIED",
    "ONTOLOGY_IDENTIFIED_UP_TO_GAUGE",
    "PARTIAL_ONTOLOGY",
    "ONTOLOGY_UNDERIDENTIFIED",
    "SEMANTIC_INFORMATION_LOSS",
)
METHODS = (
    "answer_only",
    "pca",
    "predictive",
    "intervention",
    "joint_minimal",
    "full_identity",
    "random",
)

K = 5
SEM_DIM = 4
NUIS_DIM = 12
STEP_DIM = SEM_DIM + NUIS_DIM
FLAT_DIM = K * STEP_DIM
N_INTERVENTIONS = 4
RIDGE = 1e-6

# Frozen finite-fixture thresholds. They are intentionally visible to the compiler,
# while hidden semantic coordinates and final family truth are not.
THRESHOLDS = {
    "future_r2": 0.82,
    "intervention_r2": 0.90,
    "answer_accuracy": 0.78,
    "twin_drift": 0.22,
    "collision_count": 48,
    "collision_gap": 0.75,
    "hidden_subspace_overlap": 0.90,
    "hidden_semantic_r2": 0.82,
    "gauge_invariant_r2": 0.82,
    "partial_coverage": 0.70,
}


@dataclasses.dataclass(frozen=True)
class EpisodeSpec:
    family: str
    seed: int
    split: str

    def validate(self) -> None:
        if self.family not in FAMILIES:
            raise ValueError(f"unknown family: {self.family}")
        if self.split not in {"preaudit", "final"}:
            raise ValueError(f"unknown split: {self.split}")


@dataclasses.dataclass
class VisibleSplit:
    trajectory: Array              # [n, K, STEP_DIM]
    twin_trajectory: Array         # same hidden semantic task, fresh nuisance
    intervention_trajectories: list[Array]
    future: Array                  # protected future consequences exposed to compiler
    intervention_effects: Array    # exposed consequence changes [n, U * p]
    answer: Array                  # binary external answer [n]
    context: NDArray[np.str_]


@dataclasses.dataclass
class VisibleSystem:
    name: str
    train: VisibleSplit
    calibration: VisibleSplit


@dataclasses.dataclass
class VisibleEpisode:
    episode_id: str
    split: str
    systems: dict[str, VisibleSystem]
    declared_interventions: tuple[str, ...]
    visible_contract: dict[str, Any]
    collision_bank: dict[str, Array] | None = None


@dataclasses.dataclass
class HiddenSystemAudit:
    name: str
    trajectory: Array
    twin_trajectory: Array
    intervention_trajectories: list[Array]
    z0: Array
    future: Array
    intervention_effects: Array
    answer: Array
    context: NDArray[np.str_]
    semantic_basis_flat: Array     # orthonormal basis in flattened observed coordinates
    first_step_semantic_decoder: Array  # [STEP_DIM, SEM_DIM], audit-only runtime decoder


@dataclasses.dataclass
class HiddenAudit:
    family: str
    systems: dict[str, HiddenSystemAudit]
    allowed_gauge_block: list[int]
    protected_coordinate_mask: Array
    alternative_semantic_maps: dict[str, Array]
    metadata: dict[str, Any]


@dataclasses.dataclass
class Episode:
    visible: VisibleEpisode
    hidden: HiddenAudit


@dataclasses.dataclass
class Projection:
    method: str
    rank: int
    matrices: dict[str, Array]      # system -> [FLAT_DIM, rank]
    diagnostics: dict[str, Any]


@dataclasses.dataclass
class CompiledOntology:
    pre_certificate: str
    projection: Projection | None
    selected_method: str | None
    selected_rank: int | None
    metrics_by_system: dict[str, dict[str, float]]
    candidate_table: list[dict[str, Any]]
    unresolved_blocks: list[list[int]]
    diagnostics: dict[str, Any]


def stable_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_json(obj: Any) -> str:
    return hashlib.sha256(stable_json(obj).encode("utf-8")).hexdigest()


def _orthogonal(rng: np.random.Generator, d: int) -> Array:
    q, r = np.linalg.qr(rng.normal(size=(d, d)))
    s = np.sign(np.diag(r))
    s[s == 0] = 1.0
    return q @ np.diag(s)


def _semantic_dynamics() -> list[Array]:
    mats: list[Array] = []
    for t in range(K):
        a = np.array(
            [
                [1.0 + 0.05 * t, 0.08 * t, 0.0, 0.0],
                [0.0, 0.92 + 0.03 * t, 0.06 * t, 0.0],
                [0.03 * t, 0.0, 0.86 + 0.04 * t, 0.05 * t],
                [0.0, 0.02 * t, 0.0, 0.80 + 0.05 * t],
            ],
            dtype=float,
        )
        mats.append(a)
    return mats


def _intervention_scales(family: str) -> Array:
    lam = np.array(
        [
            [1.30, 0.78, 1.05, 0.90],
            [0.82, 1.24, 0.92, 1.10],
            [1.08, 0.88, 1.28, 0.76],
            [0.74, 1.12, 0.84, 1.32],
        ],
        dtype=float,
    )
    if family in {"gauge_equivalent", "semantic_ambiguity"}:
        # The first two semantic directions have identical intervention signatures.
        shared = np.array([1.20, 0.84, 1.10, 0.76])
        lam[:, 0] = shared
        lam[:, 1] = shared
    if family == "partial_ontology":
        lam[:, 3] = 1.0
    return lam


def _sample_z(rng: np.random.Generator, n: int, family: str) -> Array:
    z = rng.exponential(scale=1.0, size=(n, SEM_DIM)) - 1.0
    if family in {"gauge_equivalent", "semantic_ambiguity"}:
        z[:, :2] = rng.normal(size=(n, 2))
    return z.astype(float)


def _future_features(z: Array, family: str) -> Array:
    if family in {"gauge_equivalent", "semantic_ambiguity"}:
        r2 = np.sum(z[:, :2] ** 2, axis=1, keepdims=True)
        return np.column_stack(
            [r2, z[:, 2], z[:, 3], z[:, 2] + 0.6 * z[:, 3], z[:, 2] * z[:, 3]]
        )
    f = np.column_stack(
        [
            z[:, 0] + 0.3 * z[:, 1],
            z[:, 1] - 0.25 * z[:, 2],
            z[:, 2] + 0.4 * z[:, 3],
            z[:, 0] - z[:, 3],
            z[:, 0] + z[:, 1] + z[:, 2] + z[:, 3],
        ]
    )
    if family == "partial_ontology":
        f = np.column_stack(
            [
                z[:, 0] + 0.3 * z[:, 1],
                z[:, 1] - 0.25 * z[:, 2],
                z[:, 2],
                z[:, 0] - z[:, 2],
                z[:, 0] + z[:, 1] + z[:, 2],
            ]
        )
    return f


def _answer(z: Array, family: str) -> Array:
    if family in {"gauge_equivalent", "semantic_ambiguity"}:
        score = np.sum(z[:, :2] ** 2, axis=1) + 0.45 * z[:, 2] - 0.35 * z[:, 3] - 1.25
    elif family == "answer_shortcut":
        score = 2.8 * z[:, 0] + 0.10 * z[:, 1] - 0.05 * z[:, 2]
    elif family == "partial_ontology":
        score = z[:, 0] + 0.7 * z[:, 1] - 0.5 * z[:, 2]
    else:
        score = z[:, 0] + 0.65 * z[:, 1] - 0.45 * z[:, 2] + 0.35 * z[:, 3]
    return (score > 0.0).astype(float)


def _make_system_gauges(root: int, system: str) -> list[Array]:
    offset = 2000 if system == "source" else 9000
    return [_orthogonal(np.random.default_rng(root + offset + 97 * t), STEP_DIM) for t in range(K)]


def _build_trajectory(
    z0: Array,
    family: str,
    gauges: list[Array],
    nuisance_seed: int,
    *,
    intervention_scale: Array | None = None,
    destructive: bool = False,
) -> tuple[Array, Array]:
    n = z0.shape[0]
    rng = np.random.default_rng(nuisance_seed)
    dynamics = _semantic_dynamics()
    trajectory = np.empty((n, K, STEP_DIM), dtype=float)
    semantic_basis_cols: list[Array] = []
    nuisance = rng.normal(scale=np.linspace(3.2, 1.4, NUIS_DIM), size=(n, NUIS_DIM))
    for t, (a, q) in enumerate(zip(dynamics, gauges)):
        zt = z0 @ a.T
        if intervention_scale is not None:
            zt = zt * intervention_scale[None, :]
        if destructive:
            # Erase protected semantic coordinate zero while retaining dimensionality.
            zt = zt.copy()
            zt[:, 0] = rng.normal(scale=0.02, size=n)
        if t > 0:
            nuisance = 0.62 * nuisance + rng.normal(
                scale=np.linspace(2.0, 0.9, NUIS_DIM), size=(n, NUIS_DIM)
            )
        raw = np.concatenate([zt, nuisance], axis=1)
        trajectory[:, t, :] = raw @ q.T
        sem_raw = np.zeros((STEP_DIM, SEM_DIM), dtype=float)
        sem_raw[:SEM_DIM] = a
        semantic_basis_cols.append(q @ sem_raw)
    flat_basis = np.vstack(semantic_basis_cols)
    flat_basis, _ = np.linalg.qr(flat_basis)
    return trajectory, flat_basis[:, :SEM_DIM]


def _poly2(x: Array) -> Array:
    x = np.asarray(x, dtype=float)
    cols = [np.ones((x.shape[0], 1)), x, x * x]
    if x.shape[1] <= 8:
        pair = [x[:, i : i + 1] * x[:, j : j + 1] for i in range(x.shape[1]) for j in range(i + 1, x.shape[1])]
        if pair:
            cols.append(np.hstack(pair))
    return np.hstack(cols)


def _fit_ridge(x: Array, y: Array, ridge: float = RIDGE) -> Array:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    return np.linalg.solve(x.T @ x + ridge * np.eye(x.shape[1]), x.T @ y)


def _predict_ridge(train_x: Array, train_y: Array, test_x: Array) -> Array:
    return test_x @ _fit_ridge(train_x, train_y)


def r2_score(y_true: Array, y_pred: Array) -> float:
    yt = np.asarray(y_true, float)
    yp = np.asarray(y_pred, float)
    sse = float(np.sum((yt - yp) ** 2))
    centered = yt - np.mean(yt, axis=0, keepdims=True)
    sst = float(np.sum(centered**2))
    return 1.0 - sse / max(sst, 1e-15)


def classification_accuracy(y_true: Array, score: Array) -> float:
    pred = (np.asarray(score).reshape(-1) >= 0.5).astype(float)
    return float(np.mean(pred == np.asarray(y_true).reshape(-1)))


def _intervention_effects(z: Array, family: str, lam: Array) -> Array:
    base = _future_features(z, family)
    effects = []
    for row in lam:
        effects.append(_future_features(z * row[None, :], family) - base)
    return np.hstack(effects)


def _build_visible_split(
    z: Array,
    family: str,
    gauges: list[Array],
    seed: int,
    context: str,
    destructive: bool,
) -> tuple[VisibleSplit, Array]:
    lam = _intervention_scales(family)
    traj, basis = _build_trajectory(z, family, gauges, seed + 1, destructive=destructive)
    twin, _ = _build_trajectory(z, family, gauges, seed + 2, destructive=destructive)
    ints = [
        _build_trajectory(
            z,
            family,
            gauges,
            seed + 1,
            intervention_scale=lam[u],
            destructive=destructive,
        )[0]
        for u in range(N_INTERVENTIONS)
    ]
    future = _future_features(z, family)
    int_eff = _intervention_effects(z, family, lam)
    answer = _answer(z, family)
    ctx = np.array([context] * len(z))
    return VisibleSplit(traj, twin, ints, future, int_eff, answer, ctx), basis


def _collision_bank(root: int, gauges: list[Array]) -> dict[str, Array]:
    rng = np.random.default_rng(root)
    n_pairs = 64
    z = _sample_z(rng, n_pairs, "identified")
    z2 = z.copy()
    z2[:, 0] = z[:, 0] + rng.choice([-1.0, 1.0], size=n_pairs) * rng.uniform(1.0, 2.0, size=n_pairs)
    # Both are rendered with semantic coordinate zero erased and identical nuisance seed.
    h1, _ = _build_trajectory(z, "destructive_loss", gauges, root + 5, destructive=True)
    h2 = h1.copy()
    # The compiler receives disagreement in externally protected future
    # consequences, not the hidden intermediate semantic coordinates z.
    # This preserves the Block 23 ontology-withholding contract while still
    # providing an exact information-loss witness.
    protected_consequences = np.concatenate(
        [_future_features(z, "identified"), _future_features(z2, "identified")],
        axis=0,
    )
    return {
        "observations": np.concatenate([h1.reshape(n_pairs, -1), h2.reshape(n_pairs, -1)], axis=0),
        "protected_consequences": protected_consequences,
    }


def build_episode(spec: EpisodeSpec) -> Episode:
    spec.validate()
    root = spec.seed + (0 if spec.split == "preaudit" else 1_000_000)
    systems: dict[str, VisibleSystem] = {}
    hidden_systems: dict[str, HiddenSystemAudit] = {}
    n_train, n_cal, n_final = (520, 320, 0) if spec.split == "preaudit" else (520, 320, 420)
    destructive = spec.family == "destructive_loss"

    for s_idx, system in enumerate(SYSTEMS):
        gauges = _make_system_gauges(root + 10_000 * s_idx, system)
        z_train = _sample_z(np.random.default_rng(root + 101 + 1000 * s_idx), n_train, spec.family)
        z_cal = _sample_z(np.random.default_rng(root + 201 + 1000 * s_idx), n_cal, spec.family)
        train, _ = _build_visible_split(z_train, spec.family, gauges, root + 301 + 1000 * s_idx, "supported", destructive)
        cal, _ = _build_visible_split(z_cal, spec.family, gauges, root + 401 + 1000 * s_idx, "supported", destructive)
        systems[system] = VisibleSystem(system, train, cal)

        if n_final:
            z_final = _sample_z(np.random.default_rng(root + 501 + 1000 * s_idx), n_final, spec.family)
            final, basis = _build_visible_split(z_final, spec.family, gauges, root + 601 + 1000 * s_idx, "supported", destructive)
            hidden_systems[system] = HiddenSystemAudit(
                system,
                final.trajectory,
                final.twin_trajectory,
                final.intervention_trajectories,
                z_final,
                final.future,
                final.intervention_effects,
                final.answer,
                final.context,
                basis,
                gauges[0][:, :SEM_DIM],
            )

    collision = None
    if destructive:
        collision = _collision_bank(root + 77_777, _make_system_gauges(root, "source"))

    visible = VisibleEpisode(
        episode_id=sha256_json({"seed": spec.seed, "split": spec.split, "salt": "block23-visible"})[:20],
        split=spec.split,
        systems=systems,
        declared_interventions=tuple(f"u{u}" for u in range(N_INTERVENTIONS)),
        visible_contract={
            "future_dimension": 5,
            "intervention_effect_dimension": 5 * N_INTERVENTIONS,
            "answer_dimension": 1,
            "gold_intermediate_semantics_visible": False,
            "final_hidden_witness_sealed": spec.split == "final",
            "collision_witness_uses_hidden_intermediate_coordinates": False,
            "collision_witness_uses_protected_future_consequences": destructive,
        },
        collision_bank=collision,
    )

    allowed_gauge = [0, 1] if spec.family == "gauge_equivalent" else []
    protected_mask = np.ones(SEM_DIM, dtype=float)
    if spec.family == "partial_ontology":
        protected_mask[3] = 0.0
    alternatives: dict[str, Array] = {}
    if spec.family in {"gauge_equivalent", "semantic_ambiguity"}:
        theta = math.pi / 3.0
        rot = np.eye(SEM_DIM)
        rot[:2, :2] = [[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]]
        alternatives["rotated_first_block"] = rot

    hidden = HiddenAudit(
        family=spec.family,
        systems=hidden_systems,
        allowed_gauge_block=allowed_gauge,
        protected_coordinate_mask=protected_mask,
        alternative_semantic_maps=alternatives,
        metadata={
            "root_seed": root,
            "seed": spec.seed,
            "split": spec.split,
            "semantic_dimension": SEM_DIM,
            "trajectory_steps": K,
            "step_dimension": STEP_DIM,
            "final_n_per_system": n_final,
        },
    )
    return Episode(visible, hidden)


def _flatten(split: VisibleSplit) -> Array:
    return split.trajectory.reshape(split.trajectory.shape[0], -1)


def _flatten_twin(split: VisibleSplit) -> Array:
    return split.twin_trajectory.reshape(split.twin_trajectory.shape[0], -1)


def _response_cov(split: VisibleSplit) -> Array:
    base = _flatten(split)
    cov = np.zeros((base.shape[1], base.shape[1]), dtype=float)
    for arr in split.intervention_trajectories:
        delta = arr.reshape(arr.shape[0], -1) - base
        cov += delta.T @ delta / max(delta.shape[0], 1)
    return cov


def _predictive_matrix(split: VisibleSplit, targets: Array) -> Array:
    x = _flatten(split)
    x = x - np.mean(x, axis=0, keepdims=True)
    y = targets - np.mean(targets, axis=0, keepdims=True)
    b = _fit_ridge(x, y)
    return b @ b.T


def _canonical_subspace_basis(w: Array, tol: float = 1e-11) -> Array:
    """Return a deterministic orthonormal basis for ``span(w)``.

    Eigenvectors and QR factors are defined only up to sign, and degenerate
    eigenspaces are defined up to an arbitrary orthogonal gauge.  Receipts must
    therefore commit to the subspace rather than a LAPACK-specific basis.  We
    form its orthogonal projector and deterministically Gram-Schmidt projected
    coordinate axes in index order.
    """
    w = np.asarray(w, dtype=float)
    q, _ = np.linalg.qr(w)
    projector = q @ q.T
    basis: list[Array] = []
    for idx in range(projector.shape[0]):
        v = projector[:, idx].copy()
        for b in basis:
            v -= b * float(np.dot(b, v))
        nrm = float(np.linalg.norm(v))
        if nrm <= tol:
            continue
        v /= nrm
        pivot = int(np.argmax(np.abs(v)))
        if v[pivot] < 0:
            v = -v
        basis.append(v)
        if len(basis) == w.shape[1]:
            break
    if len(basis) != w.shape[1]:
        raise RuntimeError("Could not construct canonical subspace basis")
    out = np.column_stack(basis)
    # One cleanup pass controls accumulated Gram-Schmidt error without changing
    # the deterministic coordinate-axis ordering.
    for j in range(out.shape[1]):
        for i in range(j):
            out[:, j] -= out[:, i] * float(np.dot(out[:, i], out[:, j]))
        out[:, j] /= max(float(np.linalg.norm(out[:, j])), tol)
        pivot = int(np.argmax(np.abs(out[:, j])))
        if out[pivot, j] < 0:
            out[:, j] *= -1.0
    return out


def _projection_from_matrix(m: Array, rank: int) -> Array:
    vals, vecs = np.linalg.eigh((m + m.T) / 2.0)
    order = np.argsort(vals, kind="stable")[::-1]
    return _canonical_subspace_basis(vecs[:, order[:rank]])


def _answer_targets(split: VisibleSplit) -> Array:
    return split.answer[:, None]


def fit_projection(visible: VisibleEpisode, method: str, rank: int, seed: int) -> Projection:
    if method not in METHODS:
        raise ValueError(method)
    matrices: dict[str, Array] = {}
    diagnostics: dict[str, Any] = {"seed": seed}
    for s_idx, (name, system) in enumerate(sorted(visible.systems.items())):
        tr = system.train
        x = _flatten(tr)
        if method == "answer_only":
            m = _predictive_matrix(tr, _answer_targets(tr))
        elif method == "pca":
            xc = x - np.mean(x, axis=0, keepdims=True)
            m = xc.T @ xc / len(xc)
        elif method == "predictive":
            m = _predictive_matrix(tr, tr.future)
        elif method == "intervention":
            m = _response_cov(tr) + _predictive_matrix(tr, tr.intervention_effects)
        elif method == "joint_minimal":
            joint = np.hstack([tr.future, tr.intervention_effects, tr.answer[:, None]])
            pm = _predictive_matrix(tr, joint)
            rc = _response_cov(tr)
            pm_scale = np.trace(pm) or 1.0
            rc_scale = np.trace(rc) or 1.0
            m = pm / pm_scale + rc / rc_scale
        elif method == "full_identity":
            matrices[name] = np.eye(FLAT_DIM)
            continue
        elif method == "random":
            rng = np.random.default_rng(seed + 1009 * s_idx)
            q, _ = np.linalg.qr(rng.normal(size=(FLAT_DIM, rank)))
            matrices[name] = _canonical_subspace_basis(q[:, :rank])
            continue
        else:  # pragma: no cover
            raise AssertionError(method)
        matrices[name] = _projection_from_matrix(m, rank)
    return Projection(method, FLAT_DIM if method == "full_identity" else rank, matrices, diagnostics)


def _quotient(split: VisibleSplit, w: Array, *, twin: bool = False) -> Array:
    x = _flatten_twin(split) if twin else _flatten(split)
    return x @ w


def evaluate_projection(visible: VisibleEpisode, projection: Projection) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for name, system in sorted(visible.systems.items()):
        w = projection.matrices[name]
        qtr = _quotient(system.train, w)
        qca = _quotient(system.calibration, w)
        qtwin = _quotient(system.calibration, w, twin=True)
        ptr = _poly2(qtr)
        pca = _poly2(qca)

        future_pred = _predict_ridge(ptr, system.train.future, pca)
        int_pred = _predict_ridge(ptr, system.train.intervention_effects, pca)
        ans_pred = _predict_ridge(ptr, system.train.answer[:, None], pca)
        future_r2 = r2_score(system.calibration.future, future_pred)
        intervention_r2 = r2_score(system.calibration.intervention_effects, int_pred)
        answer_acc = classification_accuracy(system.calibration.answer, ans_pred)

        scale = np.sqrt(np.mean(qca**2, axis=1))
        twin_delta = np.sqrt(np.mean((qca - qtwin) ** 2, axis=1))
        twin_drift = float(np.mean(twin_delta / np.maximum(scale, 1e-8)))
        out[name] = {
            "future_r2": float(future_r2),
            "intervention_r2": float(intervention_r2),
            "answer_accuracy": float(answer_acc),
            "twin_drift": twin_drift,
        }
    return out


def _passes_visible(metrics: Mapping[str, Mapping[str, float]]) -> bool:
    return all(
        m["future_r2"] >= THRESHOLDS["future_r2"]
        and m["intervention_r2"] >= THRESHOLDS["intervention_r2"]
        and m["answer_accuracy"] >= THRESHOLDS["answer_accuracy"]
        and m["twin_drift"] <= THRESHOLDS["twin_drift"]
        for m in metrics.values()
    )


def _discover_collisions(bank: Mapping[str, Array]) -> dict[str, float | int]:
    obs = np.asarray(bank["observations"], float)
    protected = np.asarray(bank["protected_consequences"], float)
    keys: dict[tuple[float, ...], list[int]] = {}
    for idx, row in enumerate(np.round(obs, 12)):
        keys.setdefault(tuple(row.tolist()), []).append(idx)
    gaps: list[float] = []
    for indices in keys.values():
        for i, j in itertools.combinations(indices, 2):
            gap = float(np.linalg.norm(protected[i] - protected[j]))
            if gap > 1e-9:
                gaps.append(gap)
    return {
        "collision_count": len(gaps),
        "minimum_protected_consequence_gap": float(min(gaps, default=0.0)),
        "mean_protected_consequence_gap": float(np.mean(gaps)) if gaps else 0.0,
    }


def _gauge_diagnostic(visible: VisibleEpisode, projection: Projection) -> dict[str, Any]:
    """Detect response directions that remain indistinguishable under all declared interventions.

    The diagnostic estimates the intervention action inside the frozen quotient and
    looks for repeated eigenvalues of a generic operator combination. A repeated
    joint signature identifies an invariant block but not a preferred basis inside
    that block.
    """
    multiplicities: dict[str, list[list[int]]] = {}
    minimum_gap = float("inf")
    operator_spectra: dict[str, list[float]] = {}
    weights = np.array([0.71, -0.37, 0.23, 0.53], dtype=float)
    for name, system in sorted(visible.systems.items()):
        w = projection.matrices[name]
        q0 = _quotient(system.train, w)
        q0c = q0 - np.mean(q0, axis=0, keepdims=True)
        ops: list[Array] = []
        for arr in system.train.intervention_trajectories:
            qi = arr.reshape(arr.shape[0], -1) @ w
            qic = qi - np.mean(qi, axis=0, keepdims=True)
            ops.append(_fit_ridge(q0c, qic))
        combo = sum(float(a) * op for a, op in zip(weights, ops))
        vals = np.sort(np.real_if_close(np.linalg.eigvals(combo)).real)[::-1]
        operator_spectra[name] = [float(v) for v in vals]
        scale = max(float(np.max(np.abs(vals))), 1e-12)
        clusters: list[list[int]] = []
        used: set[int] = set()
        for i in range(len(vals)):
            if i in used:
                continue
            block = [j for j in range(i, len(vals)) if abs(vals[j] - vals[i]) / scale < 0.004]
            used.update(block)
            if len(block) > 1:
                clusters.append(block)
        multiplicities[name] = clusters
        if len(vals) > 1:
            minimum_gap = min(minimum_gap, float(np.min(np.abs(np.diff(vals))) / scale))
    return {
        "multiplicities": multiplicities,
        "minimum_normalized_eigen_gap": minimum_gap,
        "generic_response_spectrum": operator_spectra,
    }


def compile_ontology(visible: VisibleEpisode, seed: int = 0) -> CompiledOntology:
    if visible.collision_bank is not None:
        collision = _discover_collisions(visible.collision_bank)
        if (
            collision["collision_count"] >= THRESHOLDS["collision_count"]
            and collision["minimum_protected_consequence_gap"] >= THRESHOLDS["collision_gap"]
        ):
            return CompiledOntology(
                "NO_GO",
                None,
                None,
                None,
                {},
                [],
                [],
                {"collision": collision, "reason": "visible observation collision with protected consequence disagreement"},
            )

    table: list[dict[str, Any]] = []
    valid: list[tuple[int, int, str, Projection, dict[str, dict[str, float]]]] = []
    method_priority = {m: i for i, m in enumerate(METHODS)}

    for method in METHODS:
        ranks: Iterable[int]
        if method == "full_identity":
            ranks = [FLAT_DIM]
        elif method == "answer_only":
            ranks = [1]
        else:
            ranks = range(1, 7)
        for rank in ranks:
            p = fit_projection(visible, method, rank, seed + 97 * (method_priority[method] + 1) + rank)
            metrics = evaluate_projection(visible, p)
            passed = _passes_visible(metrics)
            row = {
                "method": method,
                "rank": p.rank,
                "passed": passed,
                "worst_future_r2": min(m["future_r2"] for m in metrics.values()),
                "worst_intervention_r2": min(m["intervention_r2"] for m in metrics.values()),
                "worst_answer_accuracy": min(m["answer_accuracy"] for m in metrics.values()),
                "worst_twin_drift": max(m["twin_drift"] for m in metrics.values()),
            }
            table.append(row)
            if passed:
                valid.append((p.rank, method_priority[method], method, p, metrics))

    if not valid:
        return CompiledOntology(
            "NO_GO",
            None,
            None,
            None,
            {},
            table,
            [],
            {"reason": "no candidate quotient passed the visible predictive and interventional gates"},
        )

    # Minimum rank, then method priority. Full identity is retained only as an oversized control.
    valid.sort(key=lambda x: (x[0], x[1]))
    _, _, method, projection, metrics = valid[0]
    gauge = _gauge_diagnostic(visible, projection)
    unresolved: list[list[int]] = []
    for blocks in gauge["multiplicities"].values():
        for block in blocks:
            if block not in unresolved:
                unresolved.append(block)

    if unresolved:
        pre = "CANDIDATE_GAUGE_AMBIGUOUS"
    elif projection.rank < SEM_DIM:
        pre = "CANDIDATE_PARTIAL"
    else:
        pre = "CANDIDATE_IDENTIFIED"

    return CompiledOntology(
        pre,
        projection,
        method,
        projection.rank,
        metrics,
        table,
        unresolved,
        {"gauge_diagnostic": gauge},
    )


def _subspace_overlap(w: Array, basis: Array) -> float:
    qw, _ = np.linalg.qr(w)
    qb, _ = np.linalg.qr(basis)
    s = np.linalg.svd(qw.T @ qb, compute_uv=False)
    r = min(qw.shape[1], qb.shape[1])
    return float(np.mean(s[:r] ** 2))


def _align_semantics(q_train: Array, z_train: Array, q_test: Array) -> Array:
    # Post-seal audit-only readout. The compiler never sees z_train.
    return _poly2(q_test) @ _fit_ridge(_poly2(q_train), z_train)


def _gauge_invariant(z: Array) -> Array:
    return np.column_stack([np.sum(z[:, :2] ** 2, axis=1), z[:, 2], z[:, 3]])


def _runtime_patch_metrics(ep: Episode, compiled: CompiledOntology) -> dict[str, dict[str, float]]:
    """Audit-only causal patching through the synthetic runtime decoder.

    A donor quotient replaces only the selected latent packet. The protected
    future and intervention consequences are then recomputed from the patched
    recurrent state, not from the semantic probe used to construct the quotient.
    """
    if compiled.projection is None:
        return {}
    controls = {
        "selected": compiled.projection,
        "answer_only": fit_projection(ep.visible, "answer_only", 1, int(ep.hidden.metadata["seed"]) + 8801),
        "pca": fit_projection(ep.visible, "pca", compiled.projection.rank, int(ep.hidden.metadata["seed"]) + 8802),
        "random": fit_projection(ep.visible, "random", compiled.projection.rank, int(ep.hidden.metadata["seed"]) + 8803),
    }
    out: dict[str, dict[str, float]] = {}
    lam = _intervention_scales(ep.hidden.family)
    for system_name, hidden_system in sorted(ep.hidden.systems.items()):
        x = hidden_system.trajectory.reshape(len(hidden_system.z0), -1)
        donor = np.roll(np.arange(len(x)), 1)
        system_out: dict[str, float] = {}
        for control_name, projection in controls.items():
            w = projection.matrices[system_name]
            q = x @ w
            patched = x + (q[donor] - q) @ w.T
            first = patched[:, :STEP_DIM]
            z_patch = first @ hidden_system.first_step_semantic_decoder
            future_patch = _future_features(z_patch, ep.hidden.family)
            intervention_patch = _intervention_effects(z_patch, ep.hidden.family, lam)
            system_out[f"{control_name}_future_r2"] = r2_score(hidden_system.future[donor], future_patch)
            system_out[f"{control_name}_intervention_r2"] = r2_score(hidden_system.intervention_effects[donor], intervention_patch)
        out[system_name] = system_out
    return out


def audit_hidden(ep: Episode, compiled: CompiledOntology) -> dict[str, Any]:
    hidden = ep.hidden
    result: dict[str, Any] = {
        "family": hidden.family,
        "seed": int(hidden.metadata["seed"]),
        "split": str(hidden.metadata["split"]),
        "pre_certificate": compiled.pre_certificate,
        "selected_method": compiled.selected_method,
        "selected_rank": compiled.selected_rank,
    }
    if ep.visible.split != "final":
        return result

    if compiled.pre_certificate == "NO_GO":
        collision = compiled.diagnostics.get("collision")
        if hidden.family == "destructive_loss" and collision:
            result.update(
                {
                    "certificate": "SEMANTIC_INFORMATION_LOSS",
                    "collision_count": collision["collision_count"],
                    "minimum_protected_consequence_gap": collision["minimum_protected_consequence_gap"],
                }
            )
        else:
            result.update({"certificate": "ONTOLOGY_UNDERIDENTIFIED", "reason": compiled.diagnostics.get("reason")})
        return result

    assert compiled.projection is not None
    per_system: dict[str, dict[str, float]] = {}
    for name, ha in sorted(hidden.systems.items()):
        w = compiled.projection.matrices[name]
        x = ha.trajectory.reshape(len(ha.z0), -1)
        xt = ha.twin_trajectory.reshape(len(ha.z0), -1)
        q = x @ w
        qt = xt @ w
        split = len(q) // 2
        pred_z = _align_semantics(q[:split], ha.z0[:split], q[split:])
        semantic_r2 = r2_score(ha.z0[split:], pred_z)
        overlap = _subspace_overlap(w, ha.semantic_basis_flat)
        twin_drift = float(
            np.mean(
                np.sqrt(np.mean((q - qt) ** 2, axis=1))
                / np.maximum(np.sqrt(np.mean(q**2, axis=1)), 1e-8)
            )
        )
        inv_r2 = float("nan")
        if hidden.family in {"gauge_equivalent", "semantic_ambiguity"}:
            inv_train = _gauge_invariant(ha.z0[:split])
            inv_test = _gauge_invariant(ha.z0[split:])
            inv_pred = _poly2(q[split:]) @ _fit_ridge(_poly2(q[:split]), inv_train)
            inv_r2 = r2_score(inv_test, inv_pred)
        per_system[name] = {
            "hidden_semantic_r2": float(semantic_r2),
            "gauge_invariant_r2": float(inv_r2),
            "semantic_subspace_overlap": overlap,
            "final_twin_drift": twin_drift,
        }

    result["systems"] = per_system
    result["counterfactual_patch"] = _runtime_patch_metrics(ep, compiled)
    min_overlap = min(v["semantic_subspace_overlap"] for v in per_system.values())
    min_sem_r2 = min(v["hidden_semantic_r2"] for v in per_system.values())
    result["minimum_subspace_overlap"] = min_overlap
    result["minimum_hidden_semantic_r2"] = min_sem_r2

    if hidden.family == "gauge_equivalent":
        min_inv = min(v["gauge_invariant_r2"] for v in per_system.values())
        result["minimum_gauge_invariant_r2"] = min_inv
        result["certificate"] = (
            "ONTOLOGY_IDENTIFIED_UP_TO_GAUGE"
            if min_inv >= THRESHOLDS["gauge_invariant_r2"] and min_overlap >= THRESHOLDS["hidden_subspace_overlap"]
            else "ONTOLOGY_UNDERIDENTIFIED"
        )
    elif hidden.family == "semantic_ambiguity":
        # Two observationally equivalent orientations disagree on a protected named coordinate.
        rot = hidden.alternative_semantic_maps["rotated_first_block"]
        z = next(iter(hidden.systems.values())).z0
        disagreement = float(np.mean(np.abs(z[:, 0] - (z @ rot.T)[:, 0])))
        result["alternative_semantic_disagreement"] = disagreement
        result["certificate"] = "ONTOLOGY_UNDERIDENTIFIED"
    elif hidden.family == "partial_ontology":
        coverage = float(np.mean(hidden.protected_coordinate_mask))
        result["semantic_coverage"] = coverage
        result["certificate"] = (
            "PARTIAL_ONTOLOGY"
            if compiled.selected_rank is not None
            and compiled.selected_rank <= 3
            and coverage >= THRESHOLDS["partial_coverage"]
            and min_overlap >= 0.65
            else "ONTOLOGY_UNDERIDENTIFIED"
        )
    else:
        result["certificate"] = (
            "ONTOLOGY_IDENTIFIED"
            if min_sem_r2 >= THRESHOLDS["hidden_semantic_r2"]
            and min_overlap >= THRESHOLDS["hidden_subspace_overlap"]
            else "ONTOLOGY_UNDERIDENTIFIED"
        )

    return result


def expected_certificate(family: str) -> str:
    return {
        "identified": "ONTOLOGY_IDENTIFIED",
        "answer_shortcut": "ONTOLOGY_IDENTIFIED",
        "gauge_equivalent": "ONTOLOGY_IDENTIFIED_UP_TO_GAUGE",
        "semantic_ambiguity": "ONTOLOGY_UNDERIDENTIFIED",
        "partial_ontology": "PARTIAL_ONTOLOGY",
        "destructive_loss": "SEMANTIC_INFORMATION_LOSS",
    }[family]


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    correct = 0
    for r in records:
        cert = str(r["certificate"])
        counts[cert] = counts.get(cert, 0) + 1
        correct += int(cert == expected_certificate(str(r["family"])))
    numeric: dict[str, list[float]] = {
        "hidden_semantic_r2": [],
        "subspace_overlap": [],
        "gauge_invariant_r2": [],
        "alternative_disagreement": [],
    }
    for r in records:
        for m in r.get("systems", {}).values():
            if math.isfinite(m.get("hidden_semantic_r2", float("nan"))):
                numeric["hidden_semantic_r2"].append(float(m["hidden_semantic_r2"]))
            numeric["subspace_overlap"].append(float(m["semantic_subspace_overlap"]))
            if math.isfinite(m.get("gauge_invariant_r2", float("nan"))):
                numeric["gauge_invariant_r2"].append(float(m["gauge_invariant_r2"]))
        if "alternative_semantic_disagreement" in r:
            numeric["alternative_disagreement"].append(float(r["alternative_semantic_disagreement"]))
    return {
        "episodes": len(records),
        "correct_certificates": correct,
        "certificate_accuracy": correct / max(len(records), 1),
        "certificate_counts": counts,
        "minimum_hidden_semantic_r2": min(numeric["hidden_semantic_r2"], default=float("nan")),
        "minimum_subspace_overlap": min(numeric["subspace_overlap"], default=float("nan")),
        "minimum_gauge_invariant_r2": min(numeric["gauge_invariant_r2"], default=float("nan")),
        "minimum_alternative_disagreement": min(numeric["alternative_disagreement"], default=float("nan")),
    }
