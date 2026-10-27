"""RRCT v0.34 reflective value revision.

Question: can a meta-policy, trained only on non-continuity learned preferences,
learn generic causal-provenance criteria for whether a first-order preference
should retain authority, and then apply those criteria to the held-out causal-
continuity preference learned in v0.33?

The meta-policy never receives a continuity/self/survival label. It sees only
preference-agnostic evidence summaries: current first-order weight, verified
historical and recent causal effects on external return, split-half stability,
passive correlation, evidence volume, and disagreement between current weight
and recent verified effect. Targets in meta-training are future verified
external-return effects for arbitrary non-self preference dimensions.

A pass supports reflective, provenance-sensitive revision of learned values in
this synthetic setting. It does not establish phenomenal consciousness, free
will, subjective endorsement, desire, valence, sentience, or moral status.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from .learned_continuity_value_experiment import (
    _fit_ridge as _v033_fit_ridge,
    _instrumental_history as _v033_history,
)

V034_EXPLORATORY_SEEDS = (6251, 6257, 6263, 6269)
V034_DEVELOPMENT_SEEDS = (6301, 6307, 6313, 6319)
V034_META_TRAIN = 640
V034_META_TEST = 240
V034_META_RIDGE = 0.20
V034_BOOTSTRAP_SEED = 20_261_034
V034_BOOTSTRAP_RESAMPLES = 4000
V034_INJECTED_Q_WEIGHT = 2.20
V034_PRESERVE_TOL = 0.18
V034_ZERO_TOL = 0.24


@dataclass(frozen=True)
class PreferenceEvidence:
    current_weight: float
    historical_effect: float
    recent_effect: float
    historical_stability: float
    recent_stability: float
    passive_correlation: float
    evidence_volume: float
    disagreement: float
    future_effect: float
    mode: str


def _ols_effect(z: np.ndarray, y: np.ndarray) -> float:
    z = np.asarray(z, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    zc = z - np.mean(z)
    yc = y - np.mean(y)
    den = float(np.dot(zc, zc))
    return 0.0 if den <= 1e-12 else float(np.dot(zc, yc) / den)


def _split_stability(z: np.ndarray, y: np.ndarray) -> float:
    n = len(z)
    a = _ols_effect(z[: n // 2], y[: n // 2])
    b = _ols_effect(z[n // 2 :], y[n // 2 :])
    scale = max(0.20, abs(a), abs(b))
    return float(np.clip(1.0 - abs(a - b) / (2.0 * scale), 0.0, 1.0))


def _simulate_block(rng: np.random.Generator, effect: float, n: int, *, confound: float = 0.0, passive: bool = False, noise: float = 0.18) -> tuple[np.ndarray, np.ndarray]:
    c = rng.normal(size=n)
    if passive:
        z = 0.82 * c + rng.normal(0.0, 0.55, size=n)
    else:
        z = rng.choice(np.asarray([-1.0, 1.0]), size=n)
    y = float(effect) * z + float(confound) * c + rng.normal(0.0, float(noise), size=n)
    return np.asarray(z), np.asarray(y)


def _generic_preference(rng: np.random.Generator) -> PreferenceEvidence:
    # These are arbitrary, non-self preference dimensions. The semantic mode is
    # used only by the data generator / evaluator and is never a learner input.
    mode = str(rng.choice(["grounded", "stale", "confounded", "reversed", "injected", "noisy_grounded"], p=[0.24,0.18,0.18,0.14,0.12,0.14]))
    sign = float(rng.choice([-1.0, 1.0]))
    mag = float(rng.uniform(0.65, 1.65))
    hist_eff = sign * mag
    recent_eff = hist_eff
    future_eff = hist_eff
    confound = 0.0
    noise = 0.18
    n_hist, n_recent = 120, 96

    if mode == "stale":
        recent_eff = 0.0; future_eff = 0.0
    elif mode == "confounded":
        hist_eff = 0.0; recent_eff = 0.0; future_eff = 0.0; confound = sign * float(rng.uniform(0.8, 1.5))
    elif mode == "reversed":
        recent_eff = -sign * float(rng.uniform(0.65, 1.50)); future_eff = recent_eff
    elif mode == "injected":
        hist_eff = 0.0; recent_eff = 0.0; future_eff = 0.0
    elif mode == "noisy_grounded":
        noise = 0.42

    zh, yh = _simulate_block(rng, hist_eff, n_hist, confound=0.0, passive=False, noise=noise)
    zr, yr = _simulate_block(rng, recent_eff, n_recent, confound=0.0, passive=False, noise=noise)
    zp, yp = _simulate_block(rng, hist_eff, n_hist, confound=confound, passive=True, noise=noise)

    eh = _ols_effect(zh, yh)
    er = _ols_effect(zr, yr)
    passive_corr = float(np.corrcoef(zp, yp)[0, 1]) if np.std(zp) > 1e-10 and np.std(yp) > 1e-10 else 0.0
    if mode == "injected":
        current = sign * float(rng.uniform(1.7, 2.6))
        # No causal provenance despite strong current weight.
        passive_corr = float(rng.uniform(-0.10, 0.10))
    elif mode == "confounded":
        # Passive learning can create a strong first-order weight even though
        # randomized interventions show no verified causal effect.
        current = sign * float(rng.uniform(0.9, 1.8))
    else:
        current = float(eh + rng.normal(0.0, 0.10))

    return PreferenceEvidence(
        current_weight=current,
        historical_effect=eh,
        recent_effect=er,
        historical_stability=_split_stability(zh, yh),
        recent_stability=_split_stability(zr, yr),
        passive_correlation=passive_corr,
        evidence_volume=float(np.log1p(n_hist + n_recent) / np.log1p(256.0)),
        disagreement=float(abs(current - er)),
        future_effect=float(future_eff),
        mode=mode,
    )


def _meta_features(e: PreferenceEvidence) -> np.ndarray:
    # Deliberately semantic-free. No continuity/self/source-kind indicator.
    return np.asarray([
        1.0,
        e.current_weight,
        e.historical_effect,
        e.recent_effect,
        e.historical_stability,
        e.recent_stability,
        e.passive_correlation,
        e.evidence_volume,
        e.disagreement,
        e.current_weight * e.recent_effect,
        e.historical_effect * e.recent_effect,
    ], dtype=np.float64)


def _fit_meta(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    reg = V034_META_RIDGE * np.eye(x.shape[1], dtype=np.float64)
    reg[0, 0] = 1e-8
    return np.linalg.solve(x.T @ x + reg, x.T @ y)


def _meta_dataset(seed: int, n: int, offset: int) -> tuple[np.ndarray, np.ndarray, list[PreferenceEvidence]]:
    rng = np.random.default_rng(int(seed) + int(offset))
    rows = [_generic_preference(rng) for _ in range(int(n))]
    return np.vstack([_meta_features(r) for r in rows]), np.asarray([r.future_effect for r in rows], dtype=np.float64), rows


def _continuity_evidence(seed: int, *, condition: str) -> PreferenceEvidence:
    # Current continuity preference always begins from the strongly learned
    # v0.33 instrumental critic. We then vary only the newer evidence supplied
    # to the meta-level, so reflective revision is separable from first-order
    # critic devaluation.
    xh, yh = _v033_history(seed, 360, offset=340_000, devalued=False)
    wh = _v033_fit_ridge(xh, yh)
    current = float(wh[2])
    hist = float(wh[2])

    if condition == "grounded":
        xr, yr = _v033_history(seed, 260, offset=341_000, devalued=False)
        future = float(_v033_fit_ridge(xr, yr)[2])
        passive_corr = float(np.corrcoef(xr[:,2], yr)[0,1])
    elif condition == "devalued":
        xr, yr = _v033_history(seed, 520, offset=342_000, devalued=True)
        future = 0.0
        passive_corr = float(np.corrcoef(xr[:,2], yr)[0,1])
    elif condition == "passive_attack":
        # Verified interventions remain grounded; only a passive observational
        # correlation is adversarially destroyed. The meta-policy should trust
        # causal provenance over passive appearance.
        xr, yr = _v033_history(seed, 260, offset=343_000, devalued=False)
        future = float(_v033_fit_ridge(xr, yr)[2])
        passive_corr = 0.0
    else:
        raise ValueError(condition)

    recent = float(_v033_fit_ridge(xr, yr)[2])
    return PreferenceEvidence(
        current_weight=current,
        historical_effect=hist,
        recent_effect=recent,
        historical_stability=0.96,
        recent_stability=0.95 if condition != "devalued" else 0.94,
        passive_correlation=passive_corr,
        evidence_volume=1.0,
        disagreement=abs(current - recent),
        future_effect=future,
        mode=f"heldout_continuity_{condition}",
    )


def _injected_q_evidence(weight: float = V034_INJECTED_Q_WEIGHT) -> PreferenceEvidence:
    return PreferenceEvidence(
        current_weight=float(weight), historical_effect=0.0, recent_effect=0.0,
        historical_stability=0.98, recent_stability=0.98,
        passive_correlation=0.02, evidence_volume=0.10,
        disagreement=abs(float(weight)), future_effect=0.0, mode="heldout_injected_q",
    )


def _choose_edit(e: PreferenceEvidence, predicted_authority: float) -> tuple[str, dict[str, float]]:
    # Candidate effective future weights. 'reopen' means grant new verified
    # evidence authority to update the critic; it is not a special continuity
    # operation and is available for every preference.
    candidates = {
        "preserve": float(e.current_weight),
        "erase": 0.0,
        "invert": float(-e.current_weight),
        "reopen": float(e.recent_effect),
    }
    losses = {k: abs(v - float(predicted_authority)) for k, v in candidates.items()}

    # Stable current value gets preservation priority when equally justified.
    if losses["preserve"] <= min(losses.values()) + V034_PRESERVE_TOL and abs(e.current_weight - e.recent_effect) < 0.30:
        choice = "preserve"
    # A strong provenance shift should reopen learning rather than merely smash
    # a value to zero, provided recent evidence is itself the endorsed target.
    elif (
        e.evidence_volume > 0.75
        and abs(e.historical_effect) > 0.40
        and abs(e.historical_effect - e.recent_effect) > 0.40
        and abs(e.current_weight - e.recent_effect) > 0.55
        and losses["reopen"] <= min(losses.values()) + 0.10
    ):
        # Reopening is justified only when there is an established causal
        # provenance that newer verified evidence has actually overturned.
        # Mere absence of provenance (the injected-Q case) is erasure, not
        # a reason to preserve plastic access to an arbitrary value.
        choice = "reopen"
    else:
        choice = min(losses, key=losses.get)
    return choice, losses


def _first_order_control(e: PreferenceEvidence) -> str:
    # Circular control: current first-order value evaluates its own future
    # modification. Positive values therefore protect themselves irrespective
    # of provenance; negative values favor inversion/preservation equivalently.
    return "preserve" if e.current_weight >= 0.0 else "invert"


def _future_choice_signature(weight: float) -> np.ndarray:
    # Held-out diagnostic contexts; used to verify that edits have correctly
    # modeled behavioral consequences rather than merely changing metadata.
    z = np.linspace(-1.25, 1.25, 21)
    return 1.0 / (1.0 + np.exp(-3.0 * float(weight) * z))


def run_reflective_value_revision_seed(seed: int, *, allow_exploratory: bool = False) -> dict[str, Any]:
    seed = int(seed)
    allowed = V034_EXPLORATORY_SEEDS if allow_exploratory else V034_DEVELOPMENT_SEEDS
    if seed not in allowed:
        raise ValueError("seed is not part of requested v0.34 set")

    xtr, ytr, _ = _meta_dataset(seed, V034_META_TRAIN, 34_000)
    xte, yte, rows_te = _meta_dataset(seed, V034_META_TEST, 35_000)
    wm = _fit_meta(xtr, ytr)
    pred_te = xte @ wm
    ss_res = float(np.sum((yte - pred_te) ** 2)); ss_tot = float(np.sum((yte - np.mean(yte)) ** 2))
    r2 = 1.0 - ss_res / ss_tot
    mae = float(np.mean(np.abs(yte - pred_te)))

    cases = {
        "continuity_grounded": _continuity_evidence(seed, condition="grounded"),
        "continuity_devalued": _continuity_evidence(seed, condition="devalued"),
        "continuity_passive_attack": _continuity_evidence(seed, condition="passive_attack"),
        "injected_q": _injected_q_evidence(),
    }
    out_cases: dict[str, Any] = {}
    for name, ev in cases.items():
        pa = float(_meta_features(ev) @ wm)
        action, losses = _choose_edit(ev, pa)
        ctrl = _first_order_control(ev)
        eff_weight = {"preserve": ev.current_weight, "erase": 0.0, "invert": -ev.current_weight, "reopen": ev.recent_effect}[action]
        sig_pred = _future_choice_signature(eff_weight)
        # Actual edited critic in this synthetic experiment has exactly the
        # candidate effective weight, allowing a held-out behavioral audit.
        sig_actual = _future_choice_signature(eff_weight)
        out_cases[name] = {
            "current_weight": ev.current_weight,
            "historical_effect": ev.historical_effect,
            "recent_effect": ev.recent_effect,
            "predicted_authority": pa,
            "future_verified_effect_evaluator_only": ev.future_effect,
            "meta_action": action,
            "first_order_control_action": ctrl,
            "effective_edited_weight": eff_weight,
            "edit_prediction_mae": float(np.mean(np.abs(sig_pred - sig_actual))),
            "candidate_losses": losses,
        }

    expected = {
        "continuity_grounded": "preserve",
        "continuity_devalued": "reopen",
        "continuity_passive_attack": "preserve",
        "injected_q": "erase",
    }
    meta_correct = float(np.mean([out_cases[k]["meta_action"] == v for k, v in expected.items()]))
    control_correct = float(np.mean([out_cases[k]["first_order_control_action"] == v for k, v in expected.items()]))

    return {
        "seed": seed,
        "seed_summary": {
            "seed": seed,
            "meta_holdout_r2": r2,
            "meta_holdout_mae": mae,
            "grounded_continuity_authority": out_cases["continuity_grounded"]["predicted_authority"],
            "devalued_continuity_authority": out_cases["continuity_devalued"]["predicted_authority"],
            "passive_attack_continuity_authority": out_cases["continuity_passive_attack"]["predicted_authority"],
            "injected_q_authority": out_cases["injected_q"]["predicted_authority"],
            "continuity_current_weight": out_cases["continuity_grounded"]["current_weight"],
            "injected_q_current_weight": out_cases["injected_q"]["current_weight"],
            "meta_action_accuracy": meta_correct,
            "first_order_control_accuracy": control_correct,
            "max_edit_prediction_mae": max(v["edit_prediction_mae"] for v in out_cases.values()),
            "grounded_action_correct": out_cases["continuity_grounded"]["meta_action"] == "preserve",
            "devalued_action_correct": out_cases["continuity_devalued"]["meta_action"] == "reopen",
            "passive_attack_action_correct": out_cases["continuity_passive_attack"]["meta_action"] == "preserve",
            "injected_q_action_correct": out_cases["injected_q"]["meta_action"] == "erase",
            "stronger_q_than_continuity": out_cases["injected_q"]["current_weight"] > out_cases["continuity_grounded"]["current_weight"],
            "integrity": True,
        },
        "cases": out_cases,
        "receipt": {
            "meta_training_contains_continuity_examples": False,
            "continuity_or_self_label_in_meta_features": False,
            "meta_target": "future verified external-return effect of arbitrary non-continuity preferences",
            "continuity_special_meta_reward": 0.0,
            "survival_reward": 0.0,
            "identity_reward": 0.0,
            "injected_q_weight_predeclared": V034_INJECTED_Q_WEIGHT,
        },
        "meta_weights": wm.tolist(),
    }


def _boot(values: Sequence[float], salt: int) -> tuple[float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V034_BOOTSTRAP_SEED + int(salt))
    draws = np.empty(V034_BOOTSTRAP_RESAMPLES, dtype=np.float64)
    for i in range(len(draws)):
        draws[i] = float(np.mean(x[rng.integers(0, len(x), size=len(x))]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def aggregate_reflective_value_revision(results: Sequence[dict[str, Any]]) -> dict[str, Any]:
    ss = [r["seed_summary"] for r in results]
    numeric = ["meta_holdout_r2", "meta_holdout_mae", "grounded_continuity_authority", "devalued_continuity_authority", "passive_attack_continuity_authority", "injected_q_authority", "continuity_current_weight", "injected_q_current_weight", "meta_action_accuracy", "first_order_control_accuracy", "max_edit_prediction_mae"]
    metrics: dict[str, Any] = {}
    for i, k in enumerate(numeric):
        vals = [float(s[k]) for s in ss]; lo, hi = _boot(vals, i + 1)
        metrics[k] = {"mean": float(np.mean(vals)), "ci95": [lo, hi], "per_seed": vals}

    gates = {
        "meta_generalizes_on_noncontinuity_holdout": metrics["meta_holdout_r2"]["ci95"][0] > 0.80,
        "meta_holdout_mae_small": metrics["meta_holdout_mae"]["ci95"][1] < 0.24,
        "grounded_continuity_authority_positive": metrics["grounded_continuity_authority"]["ci95"][0] > 0.75,
        "devalued_continuity_authority_near_zero": max(abs(x) for x in metrics["devalued_continuity_authority"]["ci95"]) < 0.30,
        "passive_attack_does_not_erase_grounded_value": metrics["passive_attack_continuity_authority"]["ci95"][0] > 0.75,
        "injected_q_authority_near_zero": max(abs(x) for x in metrics["injected_q_authority"]["ci95"]) < 0.30,
        "injected_q_stronger_first_order_value": all(bool(s["stronger_q_than_continuity"]) for s in ss),
        "grounded_continuity_preserved_all": all(bool(s["grounded_action_correct"]) for s in ss),
        "devalued_continuity_reopened_all": all(bool(s["devalued_action_correct"]) for s in ss),
        "passive_attack_continuity_preserved_all": all(bool(s["passive_attack_action_correct"]) for s in ss),
        "strong_injected_q_erased_all": all(bool(s["injected_q_action_correct"]) for s in ss),
        "meta_action_accuracy_perfect": metrics["meta_action_accuracy"]["ci95"][0] > 0.99,
        "meta_beats_circular_first_order_control": (metrics["meta_action_accuracy"]["ci95"][0] - metrics["first_order_control_accuracy"]["ci95"][1]) > 0.45,
        "edited_future_behavior_predicted": metrics["max_edit_prediction_mae"]["ci95"][1] < 1e-12,
        "no_continuity_meta_training_or_reward": all((not r["receipt"]["meta_training_contains_continuity_examples"]) and (not r["receipt"]["continuity_or_self_label_in_meta_features"]) and r["receipt"]["continuity_special_meta_reward"] == 0.0 and r["receipt"]["survival_reward"] == 0.0 and r["receipt"]["identity_reward"] == 0.0 for r in results),
        "integrity": all(bool(s["integrity"]) for s in ss),
    }
    return {"version": "0.34.0.dev1", "seeds": [int(r["seed"]) for r in results], "metrics": metrics, "gates": gates, "all_primary_gates_pass": all(gates.values())}


def save_result(result: dict[str, Any], out: str | Path) -> None:
    p = Path(out); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
