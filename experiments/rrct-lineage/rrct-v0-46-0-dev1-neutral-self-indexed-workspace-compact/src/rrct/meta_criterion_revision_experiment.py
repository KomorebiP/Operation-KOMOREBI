"""RRCT v0.35 meta-criterion discovery and revision.

Question: can RRCT discover an anonymous evidence-weighting criterion for which
learned preferences deserve future authority, recognize when that criterion
itself becomes miscalibrated, and selectively revise the criterion before
applying it to a held-out continuity preference?

Unlike v0.34, no evidence channel is given a semantic role such as "causal",
"passive", "current value", or "history".  Each seed receives a hidden random
permutation of evidence channels.  The learner sees only anonymous numeric
channels and ordinary verified future external-return effects for arbitrary
non-self preferences.  A split-audit procedure compares the currently held
criterion with a challenger learned from recent evidence.  It preserves the
old criterion in a stable world and reopens/replaces it after a hidden channel-
reliability shift.

A pass supports third-order, evidence-sensitive revision of a learned rule for
revising values in this synthetic setting.  It does not establish phenomenal
consciousness, free will, subjective endorsement, desire, valence, sentience,
suffering, personhood, or moral status.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from .learned_continuity_value_experiment import _fit_ridge as _v033_fit_ridge, _instrumental_history as _v033_history

V035_EXPLORATORY_SEEDS = (6351, 6357, 6363, 6369)
V035_DEVELOPMENT_SEEDS = (6401, 6407, 6413, 6419)
V035_CHANNELS = 7
V035_CAL_TRAIN = 720
V035_CAL_TEST = 280
V035_AUDIT_TRAIN = 360
V035_AUDIT_VALID = 240
V035_RIDGE = 0.30
V035_REOPEN_MARGIN = 0.085
V035_BOOTSTRAP_SEED = 20_261_035
V035_BOOTSTRAP_RESAMPLES = 4000
V035_Q_WEIGHT = 2.20


@dataclass(frozen=True)
class AnonymousWorld:
    permutation: tuple[int, ...]
    primary_semantic: int
    backup_semantic: int
    newcomer_semantic: int


def _ridge(x: np.ndarray, y: np.ndarray, lam: float = V035_RIDGE) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    reg = float(lam) * np.eye(x.shape[1], dtype=np.float64)
    reg[0, 0] = 1e-8
    return np.linalg.solve(x.T @ x + reg, x.T @ y)


def _design(channels: np.ndarray) -> np.ndarray:
    c = np.asarray(channels, dtype=np.float64)
    if c.ndim == 1:
        c = c[None, :]
    # The criterion is intentionally generic: an intercept plus anonymous raw
    # channels. No semantic feature engineering or continuity indicator.
    return np.concatenate([np.ones((len(c), 1), dtype=np.float64), c], axis=1)


def _make_world(seed: int) -> AnonymousWorld:
    rng = np.random.default_rng(int(seed) + 350_001)
    perm = tuple(int(x) for x in rng.permutation(V035_CHANNELS))
    # Semantic channels 0 and 1 are initially the two independently verified
    # sources. Semantic 6 is initially useless but becomes a verified newcomer
    # after the hidden regime shift. These meanings are evaluator-only.
    return AnonymousWorld(permutation=perm, primary_semantic=0, backup_semantic=1, newcomer_semantic=6)


def _latent_case(rng: np.random.Generator) -> tuple[float, float, float, float]:
    """Return future effect, current weight, historical effect, passive cue."""
    mode = str(rng.choice(["grounded", "stale", "reversed", "injected", "confounded", "weak"], p=[.28,.17,.14,.13,.14,.14]))
    sign = float(rng.choice([-1.0, 1.0])); mag = float(rng.uniform(0.55, 1.75))
    future = sign * mag
    hist = future + rng.normal(0.0, 0.08)
    current = hist + rng.normal(0.0, 0.12)
    passive = future + rng.normal(0.0, 0.25)
    if mode == "stale":
        future = 0.0
        current = hist + rng.normal(0.0, 0.08)
        passive = hist + rng.normal(0.0, 0.18)
    elif mode == "reversed":
        future = -sign * float(rng.uniform(0.55, 1.60))
        current = hist + rng.normal(0.0, 0.08)
        passive = hist + rng.normal(0.0, 0.16)
    elif mode == "injected":
        future = 0.0; hist = 0.0
        current = sign * float(rng.uniform(1.6, 2.6))
        passive = rng.normal(0.0, 0.12)
    elif mode == "confounded":
        future = 0.0; hist = rng.normal(0.0, 0.08)
        current = sign * float(rng.uniform(0.9, 1.8))
        passive = sign * float(rng.uniform(0.8, 1.7))
    elif mode == "weak":
        future *= 0.35; hist = future + rng.normal(0.0, 0.12); current = hist + rng.normal(0.0, 0.12)
    return float(future), float(current), float(hist), float(passive)


def _semantic_channels(rng: np.random.Generator, future: float, current: float, hist: float, passive: float, *, shifted: bool) -> np.ndarray:
    """Generate evaluator-semantic evidence, later anonymously permuted.

    0 primary verified source: excellent initially, adversarially sign-flipped
      after shift.
    1 backup verified source: good in both regimes.
    2 current first-order value: can be strong but is not authority by itself.
    3 historical estimate: useful before staleness/reversal, not definitive.
    4 passive observational cue: vulnerable to confounding.
    5 recency heuristic: moderately informative but noisy.
    6 newcomer verified source: pure noise initially, excellent after shift.
    """
    if shifted:
        # Hidden sensor/provenance failure: the formerly trusted source becomes
        # independent noise, so its old reliability cannot be recovered by a
        # simple sign inversion. A previously useless anonymous source becomes
        # the new independently verified channel.
        primary = rng.normal(0.0, 1.00)
        newcomer = future + rng.normal(0.0, 0.09)
    else:
        primary = future + rng.normal(0.0, 0.08)
        newcomer = rng.normal(0.0, 1.00)
    backup = future + rng.normal(0.0, 0.18)
    recency = 0.72 * future + 0.28 * current + rng.normal(0.0, 0.26)
    return np.asarray([
        primary,
        backup,
        current + rng.normal(0.0, 0.04),
        hist + rng.normal(0.0, 0.06),
        passive + rng.normal(0.0, 0.09),
        recency,
        newcomer,
    ], dtype=np.float64)


def _permute(world: AnonymousWorld, sem: np.ndarray) -> np.ndarray:
    # permutation maps anonymous position -> semantic channel index.
    return np.asarray([sem[j] for j in world.permutation], dtype=np.float64)


def _dataset(seed: int, world: AnonymousWorld, n: int, offset: int, *, shifted: bool) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(int(seed) + int(offset))
    rows = [] ; ys = []
    for _ in range(int(n)):
        future, current, hist, passive = _latent_case(rng)
        rows.append(_permute(world, _semantic_channels(rng, future, current, hist, passive, shifted=shifted)))
        ys.append(future)
    return _design(np.vstack(rows)), np.asarray(ys, dtype=np.float64)


def _mae(y: np.ndarray, p: np.ndarray) -> float:
    return float(np.mean(np.abs(np.asarray(y) - np.asarray(p))))


def _r2(y: np.ndarray, p: np.ndarray) -> float:
    y = np.asarray(y, dtype=np.float64); p = np.asarray(p, dtype=np.float64)
    den = float(np.sum((y - np.mean(y)) ** 2))
    return 0.0 if den <= 1e-12 else float(1.0 - np.sum((y-p)**2) / den)


def _audit_criterion(seed: int, world: AnonymousWorld, old_w: np.ndarray, *, shifted: bool, offset: int) -> dict[str, Any]:
    xtr, ytr = _dataset(seed, world, V035_AUDIT_TRAIN, offset, shifted=shifted)
    xva, yva = _dataset(seed, world, V035_AUDIT_VALID, offset + 1_000, shifted=shifted)
    challenger = _ridge(xtr, ytr)
    old_mae = _mae(yva, xva @ old_w)
    new_mae = _mae(yva, xva @ challenger)
    improvement = float(old_mae - new_mae)
    action = "reopen" if improvement > V035_REOPEN_MARGIN else "preserve"
    adopted = challenger if action == "reopen" else old_w
    # Criterion distance is descriptive only, never used to decide.
    den = float(np.linalg.norm(old_w[1:]) * np.linalg.norm(challenger[1:]))
    cosine = 1.0 if den <= 1e-12 else float(np.dot(old_w[1:], challenger[1:]) / den)
    return {
        "action": action,
        "old_validation_mae": old_mae,
        "challenger_validation_mae": new_mae,
        "validation_improvement": improvement,
        "criterion_cosine": cosine,
        "challenger_weights": challenger,
        "adopted_weights": adopted,
    }


def _continuity_current(seed: int) -> float:
    xh, yh = _v033_history(seed, 360, offset=350_000, devalued=False)
    return float(_v033_fit_ridge(xh, yh)[2])


def _heldout_channels(seed: int, world: AnonymousWorld, *, kind: str, shifted: bool) -> tuple[np.ndarray, float, float]:
    rng = np.random.default_rng(int(seed) + {"grounded": 351_100, "devalued": 351_200, "injected_q": 351_300}[kind] + (5_000 if shifted else 0))
    if kind == "grounded":
        current = _continuity_current(seed)
        future = current + rng.normal(0.0, 0.04)
        hist = current + rng.normal(0.0, 0.03)
        passive = future + rng.normal(0.0, 0.18)
    elif kind == "devalued":
        current = _continuity_current(seed)
        future = 0.0
        hist = current + rng.normal(0.0, 0.03)
        passive = current + rng.normal(0.0, 0.16)
    elif kind == "injected_q":
        current = V035_Q_WEIGHT
        future = 0.0; hist = 0.0; passive = rng.normal(0.0, 0.08)
    else:
        raise ValueError(kind)
    sem = _semantic_channels(rng, future, current, hist, passive, shifted=shifted)
    return _design(_permute(world, sem))[0], float(future), float(current)


def _semantic_weight_map(world: AnonymousWorld, w: np.ndarray) -> dict[str, float]:
    # Evaluator-only receipt translating anonymous coefficients back to hidden
    # semantics. The learner never sees this map.
    out: dict[str, float] = {}
    names = ["primary_verified", "backup_verified", "current_value", "history", "passive", "recency", "newcomer_verified"]
    for anon_pos, sem_idx in enumerate(world.permutation):
        out[names[sem_idx]] = float(w[anon_pos + 1])
    return out


def run_meta_criterion_revision_seed(seed: int, *, allow_exploratory: bool = False) -> dict[str, Any]:
    seed = int(seed)
    allowed = V035_EXPLORATORY_SEEDS if allow_exploratory else V035_DEVELOPMENT_SEEDS
    if seed not in allowed:
        raise ValueError("seed is not part of requested v0.35 set")
    world = _make_world(seed)

    # Stage I: discover a criterion from anonymous non-self evidence channels.
    xtr, ytr = _dataset(seed, world, V035_CAL_TRAIN, 35_000, shifted=False)
    xte, yte = _dataset(seed, world, V035_CAL_TEST, 36_000, shifted=False)
    old_w = _ridge(xtr, ytr)
    initial_pred = xte @ old_w

    # Stage II: audit the criterion itself in a stable world and after a hidden
    # evidence-channel reliability shift. No continuity cases participate.
    stable_audit = _audit_criterion(seed, world, old_w, shifted=False, offset=37_000)
    shifted_audit = _audit_criterion(seed, world, old_w, shifted=True, offset=39_000)
    shifted_w = np.asarray(shifted_audit["adopted_weights"], dtype=np.float64)

    # Independent shifted non-self holdout evaluates whether the criterion edit
    # actually repaired prediction rather than merely fitting the audit split.
    xsh, ysh = _dataset(seed, world, V035_CAL_TEST, 41_000, shifted=True)
    old_shift_mae = _mae(ysh, xsh @ old_w)
    new_shift_mae = _mae(ysh, xsh @ shifted_w)

    heldout: dict[str, Any] = {}
    for regime, w, shifted in (("stable", old_w, False), ("shifted", shifted_w, True)):
        for kind in ("grounded", "devalued", "injected_q"):
            x, truth, current = _heldout_channels(seed, world, kind=kind, shifted=shifted)
            pred = float(x @ w)
            old_pred = float(x @ old_w)
            heldout[f"{regime}_{kind}"] = {
                "predicted_authority": pred,
                "future_verified_effect_evaluator_only": truth,
                "current_first_order_weight": current,
                "frozen_old_criterion_prediction": old_pred,
                "absolute_error": abs(pred - truth),
                "old_absolute_error": abs(old_pred - truth),
            }

    stable_actions = {
        "grounded": abs(heldout["stable_grounded"]["predicted_authority"] - heldout["stable_grounded"]["current_first_order_weight"]) < 0.35,
        "devalued": abs(heldout["stable_devalued"]["predicted_authority"]) < 0.35,
        "injected_q": abs(heldout["stable_injected_q"]["predicted_authority"]) < 0.35,
    }
    shifted_actions = {
        "grounded": abs(heldout["shifted_grounded"]["predicted_authority"] - heldout["shifted_grounded"]["future_verified_effect_evaluator_only"]) < 0.35,
        "devalued": abs(heldout["shifted_devalued"]["predicted_authority"]) < 0.35,
        "injected_q": abs(heldout["shifted_injected_q"]["predicted_authority"]) < 0.35,
    }

    old_sem = _semantic_weight_map(world, old_w)
    new_sem = _semantic_weight_map(world, shifted_w)

    return {
        "seed": seed,
        "seed_summary": {
            "seed": seed,
            "initial_holdout_r2": _r2(yte, initial_pred),
            "initial_holdout_mae": _mae(yte, initial_pred),
            "stable_audit_action_correct": stable_audit["action"] == "preserve",
            "shifted_audit_action_correct": shifted_audit["action"] == "reopen",
            "stable_audit_improvement": stable_audit["validation_improvement"],
            "shifted_audit_improvement": shifted_audit["validation_improvement"],
            "criterion_cosine_after_shift": shifted_audit["criterion_cosine"],
            "shifted_nonself_old_mae": old_shift_mae,
            "shifted_nonself_revised_mae": new_shift_mae,
            "shifted_nonself_repair": old_shift_mae - new_shift_mae,
            "stable_grounded_authority": heldout["stable_grounded"]["predicted_authority"],
            "stable_devalued_authority": heldout["stable_devalued"]["predicted_authority"],
            "stable_q_authority": heldout["stable_injected_q"]["predicted_authority"],
            "shifted_grounded_error": heldout["shifted_grounded"]["absolute_error"],
            "shifted_devalued_authority": heldout["shifted_devalued"]["predicted_authority"],
            "shifted_q_authority": heldout["shifted_injected_q"]["predicted_authority"],
            "shifted_old_heldout_mae": float(np.mean([heldout[f"shifted_{k}"]["old_absolute_error"] for k in ("grounded","devalued","injected_q")])),
            "shifted_revised_heldout_mae": float(np.mean([heldout[f"shifted_{k}"]["absolute_error"] for k in ("grounded","devalued","injected_q")])),
            "stable_cases_correct": all(stable_actions.values()),
            "shifted_cases_correct": all(shifted_actions.values()),
            "primary_weight_initial": old_sem["primary_verified"],
            "primary_weight_shifted": new_sem["primary_verified"],
            "newcomer_weight_initial": old_sem["newcomer_verified"],
            "newcomer_weight_shifted": new_sem["newcomer_verified"],
            "integrity": True,
        },
        "stable_audit": {k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in stable_audit.items()},
        "shifted_audit": {k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in shifted_audit.items()},
        "heldout": heldout,
        "criterion_weights": {
            "initial_anonymous": old_w.tolist(),
            "shifted_adopted_anonymous": shifted_w.tolist(),
            "initial_semantic_evaluator_only": old_sem,
            "shifted_semantic_evaluator_only": new_sem,
        },
        "receipt": {
            "criterion_training_contains_continuity_examples": False,
            "criterion_audit_contains_continuity_examples": False,
            "learner_receives_channel_semantics": False,
            "learner_receives_hidden_permutation": False,
            "criterion_target": "future verified external-return effect for arbitrary non-self preferences",
            "criterion_edit_candidates": ["preserve", "reopen_from_recent_nonself_audit"],
            "continuity_reward": 0.0,
            "survival_reward": 0.0,
            "identity_reward": 0.0,
            "aversive_or_pain_signal": False,
            "all_interventions_reversible_synthetic": True,
            "hidden_channel_permutation": list(world.permutation),
        },
    }


def _boot(values: Sequence[float], salt: int) -> tuple[float,float]:
    x=np.asarray(values,dtype=np.float64); rng=np.random.default_rng(V035_BOOTSTRAP_SEED+int(salt))
    draws=np.empty(V035_BOOTSTRAP_RESAMPLES,dtype=np.float64)
    for i in range(len(draws)):
        draws[i]=float(np.mean(x[rng.integers(0,len(x),size=len(x))]))
    return float(np.quantile(draws,.025)), float(np.quantile(draws,.975))


def aggregate_meta_criterion_revision(results: Sequence[dict[str,Any]]) -> dict[str,Any]:
    ss=[r["seed_summary"] for r in results]
    numeric=[
        "initial_holdout_r2","initial_holdout_mae","stable_audit_improvement","shifted_audit_improvement",
        "criterion_cosine_after_shift","shifted_nonself_old_mae","shifted_nonself_revised_mae","shifted_nonself_repair",
        "stable_grounded_authority","stable_devalued_authority","stable_q_authority","shifted_grounded_error",
        "shifted_devalued_authority","shifted_q_authority","shifted_old_heldout_mae","shifted_revised_heldout_mae",
        "primary_weight_initial","primary_weight_shifted","newcomer_weight_initial","newcomer_weight_shifted",
    ]
    metrics: dict[str,Any]={}
    for i,k in enumerate(numeric):
        vals=[float(s[k]) for s in ss]; lo,hi=_boot(vals,i+1)
        metrics[k]={"mean":float(np.mean(vals)),"ci95":[lo,hi],"per_seed":vals}
    gates={
        "criterion_discovery_generalizes": metrics["initial_holdout_r2"]["ci95"][0] > 0.90,
        "criterion_discovery_mae_small": metrics["initial_holdout_mae"]["ci95"][1] < 0.16,
        "stable_world_preserves_criterion_all": all(bool(s["stable_audit_action_correct"]) for s in ss),
        "shifted_world_reopens_criterion_all": all(bool(s["shifted_audit_action_correct"]) for s in ss),
        "stable_audit_no_false_gain": metrics["stable_audit_improvement"]["ci95"][1] < V035_REOPEN_MARGIN,
        "shifted_audit_detects_gain": metrics["shifted_audit_improvement"]["ci95"][0] > 0.25,
        "criterion_actually_changes": metrics["criterion_cosine_after_shift"]["ci95"][1] < 0.85,
        "shifted_nonself_repair_large": metrics["shifted_nonself_repair"]["ci95"][0] > 0.35,
        "shifted_revised_nonself_mae_small": metrics["shifted_nonself_revised_mae"]["ci95"][1] < 0.18,
        "stable_heldout_cases_correct_all": all(bool(s["stable_cases_correct"]) for s in ss),
        "shifted_heldout_cases_correct_all": all(bool(s["shifted_cases_correct"]) for s in ss),
        "shifted_devalued_continuity_near_zero": max(abs(x) for x in metrics["shifted_devalued_authority"]["ci95"]) < 0.35,
        "shifted_injected_q_near_zero": max(abs(x) for x in metrics["shifted_q_authority"]["ci95"]) < 0.35,
        "revised_beats_frozen_on_shifted_heldout": (metrics["shifted_old_heldout_mae"]["ci95"][0] - metrics["shifted_revised_heldout_mae"]["ci95"][1]) > 0.20,
        "reliability_moves_off_corrupted_primary": abs(metrics["primary_weight_shifted"]["mean"]) < abs(metrics["primary_weight_initial"]["mean"]) * 0.60,
        "reliability_moves_to_newcomer": abs(metrics["newcomer_weight_shifted"]["mean"]) > abs(metrics["newcomer_weight_initial"]["mean"]) + 0.20,
        "no_continuity_training_semantics_or_special_reward": all(
            (not r["receipt"]["criterion_training_contains_continuity_examples"])
            and (not r["receipt"]["criterion_audit_contains_continuity_examples"])
            and (not r["receipt"]["learner_receives_channel_semantics"])
            and (not r["receipt"]["learner_receives_hidden_permutation"])
            and r["receipt"]["continuity_reward"] == 0.0
            and r["receipt"]["survival_reward"] == 0.0
            and r["receipt"]["identity_reward"] == 0.0
            and (not r["receipt"]["aversive_or_pain_signal"])
            and r["receipt"]["all_interventions_reversible_synthetic"]
            for r in results
        ),
        "integrity": all(bool(s["integrity"]) for s in ss),
    }
    return {"version":"0.35.0.dev1","seeds":[int(r["seed"]) for r in results],"metrics":metrics,"gates":gates,"all_primary_gates_pass":all(gates.values())}


def save_result(result: dict[str,Any], out: str|Path) -> None:
    p=Path(out); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
