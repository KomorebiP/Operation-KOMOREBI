"""Deterministic, dependency-free confirmation statistics for workspace assays.

The functions in this module deliberately operate on ordinary mappings, lists,
numbers, and strings.  Every successful result therefore round-trips through
``json.dumps`` without a custom encoder.  Seeds are treated as the independent
replication unit; item and family resampling happens *within* a resampled seed.

The claim-ladder schema accepted by :func:`evaluate_claim_ladder` is documented
in that function.  It is intentionally fail-closed: a missing, malformed, or
non-passing field can never establish a later rung.
"""

from __future__ import annotations

import itertools
import math
import random
from statistics import NormalDist, fmean, median
from typing import Any, Mapping, Sequence


JSONReport = dict[str, Any]


def _finite_float(value: Any, *, name: str) -> float:
    if isinstance(value, bool):
        value = int(value)
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite number")
    return result


def _probability(value: Any, *, name: str) -> float:
    result = _finite_float(value, name=name)
    if not 0.0 <= result <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")
    return result


def _quantile(sorted_values: Sequence[float], probability: float) -> float:
    """Linearly interpolated quantile (stdlib-only, deterministic)."""

    if not sorted_values:
        raise ValueError("cannot take a quantile of no values")
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    position = probability * (len(sorted_values) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return float(sorted_values[lower])
    weight = position - lower
    return float(
        sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight
    )


def wilson_interval(
    successes: int,
    total: int,
    *,
    confidence: float = 0.95,
) -> JSONReport:
    """Return a Wilson score interval for a binomial proportion.

    ``total == 0`` produces an explicit invalid report with ``None`` bounds.
    This is preferable to accidentally treating an empty evaluation as a
    successful interval.  Other invalid counts raise ``ValueError``.
    """

    if isinstance(successes, bool) or not isinstance(successes, int):
        raise ValueError("successes must be an integer")
    if isinstance(total, bool) or not isinstance(total, int):
        raise ValueError("total must be an integer")
    if successes < 0 or total < 0 or successes > total:
        raise ValueError("counts must satisfy 0 <= successes <= total")
    confidence_value = _finite_float(confidence, name="confidence")
    if not 0.0 < confidence_value < 1.0:
        raise ValueError("confidence must be strictly between 0 and 1")
    if total == 0:
        return {
            "method": "wilson_score",
            "valid": False,
            "successes": 0,
            "total": 0,
            "rate": None,
            "confidence": confidence_value,
            "lower": None,
            "upper": None,
            "reason": "no_trials",
        }

    z_value = NormalDist().inv_cdf(0.5 + confidence_value / 2.0)
    proportion = successes / total
    z_squared = z_value * z_value
    denominator = 1.0 + z_squared / total
    center = (proportion + z_squared / (2.0 * total)) / denominator
    radius = (
        z_value
        * math.sqrt(
            proportion * (1.0 - proportion) / total
            + z_squared / (4.0 * total * total)
        )
        / denominator
    )
    return {
        "method": "wilson_score",
        "valid": True,
        "successes": successes,
        "total": total,
        "rate": proportion,
        "confidence": confidence_value,
        "lower": max(0.0, center - radius),
        "upper": min(1.0, center + radius),
    }


def exact_paired_sign_flip(
    seed_effects: Mapping[str, float],
    *,
    alternative: str = "two-sided",
    max_exact_seeds: int = 22,
) -> JSONReport:
    """Exact paired randomization test with seed as the exchangeable unit.

    ``seed_effects`` maps an independent seed identifier to its paired effect
    (candidate minus control).  Under the sharp null, each effect's sign is
    exchangeable.  All ``2**n`` assignments are enumerated, so this function
    does not use a Monte Carlo correction or a random number generator.
    """

    if alternative not in {"two-sided", "greater", "less"}:
        raise ValueError("alternative must be two-sided, greater, or less")
    ordered = sorted((str(key), value) for key, value in seed_effects.items())
    if not ordered:
        return {
            "method": "exact_paired_seed_sign_flip",
            "valid": False,
            "alternative": alternative,
            "seed_count": 0,
            "effects": {},
            "mean_effect": None,
            "p_value": None,
            "reason": "no_independent_seeds",
        }
    if len(ordered) > max_exact_seeds:
        raise ValueError(
            f"exact enumeration is limited to {max_exact_seeds} seeds; "
            "increase max_exact_seeds explicitly if intended"
        )
    effects = [_finite_float(value, name=f"effect[{key}]") for key, value in ordered]
    observed_sum = sum(effects)
    tolerance = 1e-12 * max(1.0, abs(observed_sum), sum(abs(x) for x in effects))
    extreme = 0
    assignments = 1 << len(effects)
    for signs in itertools.product((-1.0, 1.0), repeat=len(effects)):
        permuted_sum = sum(sign * effect for sign, effect in zip(signs, effects))
        if alternative == "two-sided":
            is_extreme = abs(permuted_sum) + tolerance >= abs(observed_sum)
        elif alternative == "greater":
            is_extreme = permuted_sum + tolerance >= observed_sum
        else:
            is_extreme = permuted_sum - tolerance <= observed_sum
        extreme += int(is_extreme)
    return {
        "method": "exact_paired_seed_sign_flip",
        "valid": True,
        "alternative": alternative,
        "seed_count": len(effects),
        "effects": {key: effect for (key, _), effect in zip(ordered, effects)},
        "mean_effect": fmean(effects),
        "median_effect": median(effects),
        "positive_seed_count": sum(effect > 0.0 for effect in effects),
        "negative_seed_count": sum(effect < 0.0 for effect in effects),
        "zero_seed_count": sum(effect == 0.0 for effect in effects),
        "assignments_enumerated": assignments,
        "extreme_assignments": extreme,
        "p_value": extreme / assignments,
    }


def exact_paired_permutation(
    seed_pairs: Mapping[str, Mapping[str, float] | Sequence[float]],
    *,
    candidate_key: str = "candidate",
    control_key: str = "control",
    alternative: str = "two-sided",
    max_exact_seeds: int = 22,
) -> JSONReport:
    """Convenience wrapper for paired arm values keyed by independent seed.

    Each value may be ``{"candidate": x, "control": y}`` or a two-element
    sequence ``[x, y]``.  The returned test is the exact paired sign-flip test
    of ``candidate - control``.
    """

    effects: dict[str, float] = {}
    arm_values: dict[str, dict[str, float]] = {}
    for raw_seed, raw_pair in sorted(seed_pairs.items(), key=lambda item: str(item[0])):
        seed = str(raw_seed)
        if isinstance(raw_pair, Mapping):
            if candidate_key not in raw_pair or control_key not in raw_pair:
                raise ValueError(
                    f"seed {seed!r} must contain {candidate_key!r} and {control_key!r}"
                )
            candidate = _finite_float(raw_pair[candidate_key], name=f"{seed}.candidate")
            control = _finite_float(raw_pair[control_key], name=f"{seed}.control")
        else:
            if isinstance(raw_pair, (str, bytes)) or len(raw_pair) != 2:
                raise ValueError(f"seed {seed!r} must contain exactly two arm values")
            candidate = _finite_float(raw_pair[0], name=f"{seed}.candidate")
            control = _finite_float(raw_pair[1], name=f"{seed}.control")
        arm_values[seed] = {candidate_key: candidate, control_key: control}
        effects[seed] = candidate - control
    report = exact_paired_sign_flip(
        effects,
        alternative=alternative,
        max_exact_seeds=max_exact_seeds,
    )
    report["arm_values"] = arm_values
    report["candidate_key"] = candidate_key
    report["control_key"] = control_key
    return report


def _normalise_hierarchy(
    seed_outcomes: Mapping[
        str,
        Mapping[str, Sequence[float]] | Sequence[Mapping[str, Any]],
    ],
    *,
    family_key: str,
    value_key: str,
) -> dict[str, dict[str, list[float]]]:
    hierarchy: dict[str, dict[str, list[float]]] = {}
    for raw_seed, raw_outcomes in sorted(
        seed_outcomes.items(), key=lambda item: str(item[0])
    ):
        seed = str(raw_seed)
        families: dict[str, list[float]] = {}
        if isinstance(raw_outcomes, Mapping):
            for raw_family, raw_values in sorted(
                raw_outcomes.items(), key=lambda item: str(item[0])
            ):
                family = str(raw_family)
                if isinstance(raw_values, (str, bytes)):
                    raise ValueError(f"{seed}.{family} outcomes must be a sequence")
                values = [
                    _finite_float(value, name=f"{seed}.{family}[{index}]")
                    for index, value in enumerate(raw_values)
                ]
                if not values:
                    raise ValueError(f"{seed}.{family} has no item outcomes")
                families[family] = values
        else:
            if isinstance(raw_outcomes, (str, bytes)):
                raise ValueError(f"seed {seed!r} outcomes must be records or families")
            for index, record in enumerate(raw_outcomes):
                if not isinstance(record, Mapping):
                    raise ValueError(f"{seed}[{index}] must be a mapping")
                if family_key not in record or value_key not in record:
                    raise ValueError(
                        f"{seed}[{index}] must contain {family_key!r} and {value_key!r}"
                    )
                family = str(record[family_key])
                value = _finite_float(record[value_key], name=f"{seed}[{index}].value")
                families.setdefault(family, []).append(value)
        if not families:
            raise ValueError(f"seed {seed!r} has no family outcomes")
        hierarchy[seed] = dict(sorted(families.items()))
    return hierarchy


def _hierarchical_estimate(hierarchy: Mapping[str, Mapping[str, Sequence[float]]]) -> float:
    seed_means = []
    for families in hierarchy.values():
        family_means = [fmean(values) for values in families.values()]
        seed_means.append(fmean(family_means))
    return fmean(seed_means)


def hierarchical_bootstrap(
    seed_outcomes: Mapping[
        str,
        Mapping[str, Sequence[float]] | Sequence[Mapping[str, Any]],
    ],
    *,
    replicates: int = 10_000,
    random_seed: int = 0,
    confidence: float = 0.95,
    family_key: str = "family_id",
    value_key: str = "effect",
    include_samples: bool = False,
) -> JSONReport:
    """Seed-family-item hierarchical bootstrap of an equal-seed estimand.

    Input can use either nested mappings::

        {"seed1": {"familyA": [0, 1], "familyB": [1]}}

    or item records::

        {"seed1": [{"family_id": "familyA", "effect": 0}, ...]}

    A replicate samples seeds, then families within each selected seed, then
    items within each selected family, all with replacement.  Family means are
    averaged within seeds and seed means are averaged across seeds, preventing
    a seed or family with more logged items from silently dominating inference.
    """

    if isinstance(replicates, bool) or not isinstance(replicates, int) or replicates < 1:
        raise ValueError("replicates must be a positive integer")
    confidence_value = _finite_float(confidence, name="confidence")
    if not 0.0 < confidence_value < 1.0:
        raise ValueError("confidence must be strictly between 0 and 1")
    hierarchy = _normalise_hierarchy(
        seed_outcomes,
        family_key=family_key,
        value_key=value_key,
    )
    if not hierarchy:
        return {
            "method": "seed_family_item_hierarchical_bootstrap",
            "valid": False,
            "seed_count": 0,
            "estimate": None,
            "lower": None,
            "upper": None,
            "reason": "no_independent_seeds",
        }

    rng = random.Random(int(random_seed))
    seed_ids = sorted(hierarchy)
    samples: list[float] = []
    for _ in range(replicates):
        replicate_seed_means: list[float] = []
        for _seed_draw in range(len(seed_ids)):
            selected_seed = seed_ids[rng.randrange(len(seed_ids))]
            families = hierarchy[selected_seed]
            family_ids = sorted(families)
            sampled_family_means: list[float] = []
            for _family_draw in range(len(family_ids)):
                selected_family = family_ids[rng.randrange(len(family_ids))]
                values = families[selected_family]
                sampled_values = [values[rng.randrange(len(values))] for _ in values]
                sampled_family_means.append(fmean(sampled_values))
            replicate_seed_means.append(fmean(sampled_family_means))
        samples.append(fmean(replicate_seed_means))

    ordered_samples = sorted(samples)
    tail = (1.0 - confidence_value) / 2.0
    estimate = _hierarchical_estimate(hierarchy)
    sample_mean = fmean(samples)
    sample_variance = (
        sum((value - sample_mean) ** 2 for value in samples) / (len(samples) - 1)
        if len(samples) > 1
        else 0.0
    )
    report: JSONReport = {
        "method": "seed_family_item_hierarchical_bootstrap",
        "valid": True,
        "random_seed": int(random_seed),
        "replicates": replicates,
        "confidence": confidence_value,
        "seed_count": len(seed_ids),
        "family_count": sum(len(families) for families in hierarchy.values()),
        "item_count": sum(
            len(values)
            for families in hierarchy.values()
            for values in families.values()
        ),
        "estimand": "equal_seed_mean_of_equal_family_means",
        "estimate": estimate,
        "bootstrap_mean": sample_mean,
        "bootstrap_standard_error": math.sqrt(sample_variance),
        "lower": _quantile(ordered_samples, tail),
        "upper": _quantile(ordered_samples, 1.0 - tail),
    }
    if include_samples:
        report["samples"] = samples
    return report


def holm_correction(
    p_values: Mapping[str, float],
    *,
    alpha: float = 0.05,
) -> JSONReport:
    """Holm family-wise error correction for predeclared primary contrasts."""

    alpha_value = _probability(alpha, name="alpha")
    ordered = sorted(
        ((str(name), _probability(value, name=f"p[{name}]")) for name, value in p_values.items()),
        key=lambda item: (item[1], item[0]),
    )
    count = len(ordered)
    adjusted: dict[str, float] = {}
    running = 0.0
    for index, (name, p_value) in enumerate(ordered):
        running = max(running, (count - index) * p_value)
        adjusted[name] = min(1.0, running)
    results = {
        name: {
            "raw_p": p_value,
            "adjusted_p": adjusted[name],
            "reject": adjusted[name] <= alpha_value,
            "rank": index + 1,
        }
        for index, (name, p_value) in enumerate(ordered)
    }
    return {
        "method": "holm",
        "valid": bool(ordered),
        "alpha": alpha_value,
        "hypothesis_count": count,
        "results": results,
        **({} if ordered else {"reason": "no_hypotheses"}),
    }


def benjamini_hochberg(
    p_values: Mapping[str, float],
    *,
    alpha: float = 0.05,
) -> JSONReport:
    """Benjamini-Hochberg FDR correction for predeclared secondary contrasts."""

    alpha_value = _probability(alpha, name="alpha")
    ordered = sorted(
        ((str(name), _probability(value, name=f"p[{name}]")) for name, value in p_values.items()),
        key=lambda item: (item[1], item[0]),
    )
    count = len(ordered)
    adjusted: dict[str, float] = {}
    running = 1.0
    for reverse_index in range(count - 1, -1, -1):
        name, p_value = ordered[reverse_index]
        rank = reverse_index + 1
        running = min(running, p_value * count / rank)
        adjusted[name] = min(1.0, running)
    results = {
        name: {
            "raw_p": p_value,
            "adjusted_p": adjusted[name],
            "reject": adjusted[name] <= alpha_value,
            "rank": index + 1,
        }
        for index, (name, p_value) in enumerate(ordered)
    }
    return {
        "method": "benjamini_hochberg",
        "valid": bool(ordered),
        "alpha": alpha_value,
        "hypothesis_count": count,
        "results": results,
        **({} if ordered else {"reason": "no_hypotheses"}),
    }


def multiplicity_report(
    primary_p_values: Mapping[str, float],
    secondary_p_values: Mapping[str, float],
    *,
    alpha: float = 0.05,
) -> JSONReport:
    """Apply Holm to primary and BH to secondary contrast families."""

    primary = holm_correction(primary_p_values, alpha=alpha)
    secondary = benjamini_hochberg(secondary_p_values, alpha=alpha)
    return {
        "valid": bool(primary["valid"]),
        "alpha": _probability(alpha, name="alpha"),
        "primary": primary,
        "secondary": secondary,
        "policy": {
            "primary": "holm_family_wise_error",
            "secondary": "benjamini_hochberg_false_discovery_rate",
        },
    }


def _interval_values(interval: Mapping[str, Any]) -> tuple[float, float, float] | None:
    estimate_raw = interval.get("estimate", interval.get("rate_difference"))
    lower_raw = interval.get("lower", interval.get("ci_lower"))
    upper_raw = interval.get("upper", interval.get("ci_upper"))
    if estimate_raw is None or lower_raw is None or upper_raw is None:
        return None
    try:
        estimate = _finite_float(estimate_raw, name="estimate")
        lower = _finite_float(lower_raw, name="lower")
        upper = _finite_float(upper_raw, name="upper")
    except ValueError:
        return None
    if lower > estimate or estimate > upper:
        return None
    return estimate, lower, upper


def effect_decision(
    interval: Mapping[str, Any],
    *,
    minimum_effect: float = 0.0,
    direction: str = "greater",
) -> JSONReport:
    """Decide whether an entire confidence interval clears an effect threshold."""

    if direction not in {"greater", "less"}:
        raise ValueError("direction must be greater or less")
    threshold = _finite_float(minimum_effect, name="minimum_effect")
    values = _interval_values(interval)
    if values is None:
        return {
            "valid": False,
            "passed": False,
            "direction": direction,
            "minimum_effect": threshold,
            "reason": "missing_or_invalid_interval",
        }
    estimate, lower, upper = values
    passed = lower > threshold if direction == "greater" else upper < threshold
    return {
        "valid": True,
        "passed": passed,
        "direction": direction,
        "minimum_effect": threshold,
        "estimate": estimate,
        "lower": lower,
        "upper": upper,
        "distance_past_threshold": (
            lower - threshold if direction == "greater" else threshold - upper
        ),
    }


def equivalence_decision(
    interval: Mapping[str, Any],
    *,
    margin: float,
) -> JSONReport:
    """Declare practical equivalence only when the full CI is inside ±margin."""

    margin_value = _finite_float(margin, name="margin")
    if margin_value <= 0.0:
        raise ValueError("margin must be positive")
    values = _interval_values(interval)
    if values is None:
        return {
            "valid": False,
            "passed": False,
            "margin": margin_value,
            "reason": "missing_or_invalid_interval",
        }
    estimate, lower, upper = values
    return {
        "valid": True,
        "passed": lower > -margin_value and upper < margin_value,
        "margin": margin_value,
        "estimate": estimate,
        "lower": lower,
        "upper": upper,
    }


def paired_effect_report(
    seed_effects: Mapping[str, float],
    *,
    minimum_effect: float = 0.0,
    alternative: str = "greater",
    alpha: float = 0.05,
) -> JSONReport:
    """Compact descriptive and exact-inference report for seed effects."""

    alpha_value = _probability(alpha, name="alpha")
    exact = exact_paired_sign_flip(seed_effects, alternative=alternative)
    if not exact["valid"]:
        return {
            "valid": False,
            "passed": False,
            "minimum_effect": _finite_float(minimum_effect, name="minimum_effect"),
            "alpha": alpha_value,
            "exact_test": exact,
            "reason": "no_independent_seeds",
        }
    threshold = _finite_float(minimum_effect, name="minimum_effect")
    mean_effect = float(exact["mean_effect"])
    direction_passed = mean_effect > threshold if alternative != "less" else mean_effect < threshold
    return {
        "valid": True,
        "passed": direction_passed and float(exact["p_value"]) <= alpha_value,
        "mean_effect": mean_effect,
        "median_effect": float(exact["median_effect"]),
        "minimum_effect": threshold,
        "alpha": alpha_value,
        "exact_test": exact,
    }


def _nested(mapping: Mapping[str, Any], *path: str) -> Any:
    value: Any = mapping
    for key in path:
        if not isinstance(value, Mapping) or key not in value:
            return None
        value = value[key]
    return value


def _explicit_pass(value: Any) -> bool:
    if value is True:
        return True
    return isinstance(value, Mapping) and value.get("passed") is True


def evaluate_claim_ladder(
    evidence: Mapping[str, Any],
    *,
    required_confirmatory_seeds: int = 3,
    required_consumers: int = 2,
) -> JSONReport:
    """Evaluate a conservative arithmetic-workspace/J-space claim ladder.

    Canonical input schema (all fields are required for the final rung)::

        {
          "validity": {"passed": true},
          "competence": {"passed": true},
          "compact_representation": {"passed": true},
          "causal_necessity": {
            "candidate_vs_random": {"passed": true},
            "candidate_vs_pca": {"passed": true}
          },
          "directional_patch": {"passed": true},
          "rescue": {"passed": true},
          "mediation": {"passed": true},
          "multiple_consumers": {"passed": true, "consumer_count": 2},
          "arithmetic_vs_pseudo": {"passed": true},
          "confirmation": {
            "passed": true,
            "independent": true,
            "confirmatory_seed_ids": [101, 102, 103]
          }
        }

    Passing both rescue and mediation is required.  Confirmatory seed IDs must
    be distinct and explicitly marked independent.  Missing data, a bare truthy
    string/number, or an invalid count fails closed and is listed in ``missing``
    or ``failed``.
    """

    if isinstance(required_confirmatory_seeds, bool) or not isinstance(
        required_confirmatory_seeds, int
    ) or required_confirmatory_seeds < 1:
        raise ValueError("required_confirmatory_seeds must be a positive integer")
    if isinstance(required_consumers, bool) or not isinstance(required_consumers, int) or required_consumers < 2:
        raise ValueError("required_consumers must be an integer of at least two")

    raw_consumers = _nested(evidence, "multiple_consumers")
    consumer_count: int | None = None
    if isinstance(raw_consumers, Mapping):
        raw_count = raw_consumers.get("consumer_count")
        if isinstance(raw_count, int) and not isinstance(raw_count, bool) and raw_count >= 0:
            consumer_count = raw_count

    raw_confirmation = _nested(evidence, "confirmation")
    seed_ids: list[str] = []
    confirmation_independent = False
    if isinstance(raw_confirmation, Mapping):
        raw_seed_ids = raw_confirmation.get("confirmatory_seed_ids")
        if isinstance(raw_seed_ids, Sequence) and not isinstance(raw_seed_ids, (str, bytes)):
            seed_ids = [str(value) for value in raw_seed_ids]
        confirmation_independent = raw_confirmation.get("independent") is True
    distinct_seed_count = len(set(seed_ids))

    checks: dict[str, dict[str, Any]] = {
        "validity": {"passed": _explicit_pass(_nested(evidence, "validity"))},
        "competence": {"passed": _explicit_pass(_nested(evidence, "competence"))},
        "compact_representation": {
            "passed": _explicit_pass(_nested(evidence, "compact_representation"))
        },
        "candidate_vs_random_causal_necessity": {
            "passed": _explicit_pass(
                _nested(evidence, "causal_necessity", "candidate_vs_random")
            )
        },
        "candidate_vs_pca_causal_necessity": {
            "passed": _explicit_pass(
                _nested(evidence, "causal_necessity", "candidate_vs_pca")
            )
        },
        "directional_patch": {
            "passed": _explicit_pass(_nested(evidence, "directional_patch"))
        },
        "rescue": {"passed": _explicit_pass(_nested(evidence, "rescue"))},
        "mediation": {"passed": _explicit_pass(_nested(evidence, "mediation"))},
        "multiple_consumers": {
            "passed": _explicit_pass(raw_consumers)
            and consumer_count is not None
            and consumer_count >= required_consumers,
            "observed_consumer_count": consumer_count,
            "required_consumer_count": required_consumers,
        },
        "arithmetic_vs_learnable_pseudo_control": {
            "passed": _explicit_pass(_nested(evidence, "arithmetic_vs_pseudo"))
        },
        "independent_confirmation": {
            "passed": _explicit_pass(raw_confirmation)
            and confirmation_independent
            and len(seed_ids) == distinct_seed_count
            and distinct_seed_count >= required_confirmatory_seeds,
            "explicitly_independent": confirmation_independent,
            "confirmatory_seed_ids": seed_ids,
            "distinct_confirmatory_seed_count": distinct_seed_count,
            "required_confirmatory_seed_count": required_confirmatory_seeds,
        },
    }

    source_paths = {
        "validity": ("validity",),
        "competence": ("competence",),
        "compact_representation": ("compact_representation",),
        "candidate_vs_random_causal_necessity": (
            "causal_necessity",
            "candidate_vs_random",
        ),
        "candidate_vs_pca_causal_necessity": (
            "causal_necessity",
            "candidate_vs_pca",
        ),
        "directional_patch": ("directional_patch",),
        "rescue": ("rescue",),
        "mediation": ("mediation",),
        "multiple_consumers": ("multiple_consumers",),
        "arithmetic_vs_learnable_pseudo_control": ("arithmetic_vs_pseudo",),
        "independent_confirmation": ("confirmation",),
    }
    missing = [
        ".".join(source_paths[name])
        for name in checks
        if _nested(evidence, *source_paths[name]) is None
    ]
    failed = [name for name, check in checks.items() if not check["passed"]]

    rung_specs = [
        ("valid_measurement", ["validity"]),
        ("competent_system", ["validity", "competence"]),
        (
            "compact_candidate_representation",
            ["validity", "competence", "compact_representation"],
        ),
        (
            "causally_necessary_and_patchable_candidate",
            [
                "validity",
                "competence",
                "compact_representation",
                "candidate_vs_random_causal_necessity",
                "candidate_vs_pca_causal_necessity",
                "directional_patch",
            ],
        ),
        (
            "rescued_mediating_shared_candidate",
            [
                "validity",
                "competence",
                "compact_representation",
                "candidate_vs_random_causal_necessity",
                "candidate_vs_pca_causal_necessity",
                "directional_patch",
                "rescue",
                "mediation",
                "multiple_consumers",
            ],
        ),
        ("arithmetic_selective_independently_confirmed", list(checks)),
    ]
    ladder: list[dict[str, Any]] = []
    highest_rung = "none"
    for rung_name, requirements in rung_specs:
        passed = all(checks[name]["passed"] for name in requirements)
        ladder.append(
            {
                "rung": rung_name,
                "passed": passed,
                "requirements": requirements,
                "unmet": [name for name in requirements if not checks[name]["passed"]],
            }
        )
        if passed:
            highest_rung = rung_name

    established = ladder[-1]["passed"]
    return {
        "method": "fail_closed_arithmetic_workspace_claim_ladder_v1",
        "established": established,
        "claim_status": (
            "ARITHMETIC_JSPACE_EQUIVALENT_SUPPORTED"
            if established
            else "JSPACE_CLAIM_NOT_ESTABLISHED"
        ),
        "highest_rung": highest_rung,
        "required_confirmatory_seeds": required_confirmatory_seeds,
        "required_consumers": required_consumers,
        "checks": checks,
        "missing": missing,
        "failed": failed,
        "ladder": ladder,
    }


__all__ = [
    "benjamini_hochberg",
    "effect_decision",
    "equivalence_decision",
    "evaluate_claim_ladder",
    "exact_paired_permutation",
    "exact_paired_sign_flip",
    "hierarchical_bootstrap",
    "holm_correction",
    "multiplicity_report",
    "paired_effect_report",
    "wilson_interval",
]
