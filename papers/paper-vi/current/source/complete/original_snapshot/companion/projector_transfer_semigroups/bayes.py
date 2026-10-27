from __future__ import annotations

from collections.abc import Sequence
import numpy as np
from scipy.special import betaln
import math


def _normalize(probability: np.ndarray) -> np.ndarray:
    p = np.asarray(probability, dtype=float)
    if p.ndim != 1 or not np.all(np.isfinite(p)) or np.any(p < 0):
        raise ValueError("prior must be a finite nonnegative vector")
    total = float(np.sum(p))
    if not np.isfinite(total) or total <= 0:
        raise ValueError("positive total mass required")
    return p / total


def bayes_update(prior: np.ndarray, likelihood: np.ndarray) -> np.ndarray:
    p = _normalize(prior)
    l = np.asarray(likelihood, dtype=float)
    if p.shape != l.shape or not np.all(np.isfinite(l)) or np.any(l < 0):
        raise ValueError("likelihood must be nonnegative and match the prior")
    evidence = float(l @ p)
    if not np.isfinite(evidence) or evidence <= 0:
        raise ValueError("positive evidence required")
    return l * p / evidence


def packet_bayes_update(
    prior: np.ndarray,
    likelihood: np.ndarray,
    groups: Sequence[Sequence[int]],
) -> dict[str, object]:
    posterior = bayes_update(prior, likelihood)
    p = _normalize(prior)
    l = np.asarray(likelihood, dtype=float)
    groups = _validate_groups(groups, p.size)
    packet_evidence = np.array([sum(l[i] * p[i] for i in group) for group in groups], dtype=float)
    total = float(packet_evidence.sum())
    packet_masses = packet_evidence / total
    conditional_shapes: list[np.ndarray] = []
    for group, mass in zip(groups, packet_evidence, strict=True):
        local = np.array([l[i] * p[i] for i in group], dtype=float)
        conditional_shapes.append(local / mass if mass > 0 else local)
    reconstructed = np.zeros_like(posterior)
    for packet_mass, group, shape in zip(packet_masses, groups, conditional_shapes, strict=True):
        for local_index, global_index in enumerate(group):
            reconstructed[global_index] = packet_mass * shape[local_index]
    return {
        "posterior": posterior,
        "packet_evidence": packet_evidence,
        "packet_masses": packet_masses,
        "conditional_shapes": conditional_shapes,
        "reconstructed": reconstructed,
    }


def beta_binomial_posterior(a: float, b: float, successes: int, trials: int) -> dict[str, float]:
    if min(a, b) <= 0 or not 0 <= successes <= trials:
        raise ValueError("valid Beta prior and binomial counts required")
    ap = a + successes
    bp = b + trials - successes
    return {
        "a": ap,
        "b": bp,
        "mean": ap / (ap + bp),
        "variance": ap * bp / ((ap + bp) ** 2 * (ap + bp + 1)),
        "log_evidence": math.log(math.comb(trials, successes)) + betaln(ap, bp) - betaln(a, b),
    }


def bayesian_flow(prior: np.ndarray, score: np.ndarray, time: float) -> np.ndarray:
    """B_t(p) with likelihood exp(t*score)."""
    return bayes_update(prior, np.exp(float(time) * np.asarray(score, dtype=float)))


def bayesian_flow_generator(probability: np.ndarray, score: np.ndarray) -> np.ndarray:
    p = _normalize(probability)
    g = np.asarray(score, dtype=float)
    return (g - float(g @ p)) * p


def hmm_filter(
    transition: np.ndarray,
    initial: np.ndarray,
    likelihoods: Sequence[np.ndarray],
) -> list[np.ndarray]:
    k = np.asarray(transition, dtype=float)
    p = _normalize(initial)
    filtered = [p.copy()]
    for likelihood in likelihoods:
        predicted = k @ p
        p = bayes_update(predicted, np.asarray(likelihood, dtype=float))
        filtered.append(p.copy())
    return filtered


def _validate_groups(groups: Sequence[Sequence[int]], size: int) -> tuple[tuple[int, ...], ...]:
    import operator

    try:
        normalized = tuple(tuple(operator.index(i) for i in group) for group in groups)
    except TypeError as exc:
        raise ValueError("state indices must be integers") from exc
    flattened = [i for group in normalized for i in group]
    if sorted(flattened) != list(range(size)):
        raise ValueError("groups must form a partition of the state indices")
    if any(len(group) == 0 for group in normalized):
        raise ValueError("groups must be nonempty")
    return normalized


def coarsen_probability(probability: np.ndarray, groups: Sequence[Sequence[int]]) -> np.ndarray:
    """Sum fine-state masses over a declared packet partition."""
    p = _normalize(probability)
    partition = _validate_groups(groups, p.size)
    return np.array([float(np.sum(p[list(group)])) for group in partition], dtype=float)


def effective_coarse_likelihood(
    prior: np.ndarray,
    likelihood: np.ndarray,
    groups: Sequence[Sequence[int]],
) -> np.ndarray:
    """Return the conditional within-packet evidence seen by each coarse state.

    If P_a is the coarse mass and q_{a,i}=p_i/P_a, the returned value is
    r_a(p)=sum_{i in I_a} q_{a,i} lambda_i.  Its value on a zero-mass packet is
    set to zero because that coordinate does not affect the posterior.
    """
    p = _normalize(prior)
    l = np.asarray(likelihood, dtype=float)
    if p.shape != l.shape or not np.all(np.isfinite(l)) or np.any(l < 0):
        raise ValueError("likelihood must be nonnegative and match the prior")
    partition = _validate_groups(groups, p.size)
    result = np.zeros(len(partition), dtype=float)
    for a, group in enumerate(partition):
        indices = list(group)
        mass = float(np.sum(p[indices]))
        if mass > 0:
            result[a] = float(l[indices] @ (p[indices] / mass))
    return result


def bayesian_coarsening_defect(
    prior: np.ndarray,
    likelihood: np.ndarray,
    groups: Sequence[Sequence[int]],
    coarse_likelihood: np.ndarray,
) -> dict[str, np.ndarray | float]:
    """Exact Bayesian refinement defect and its information-loss factorization."""
    p = _normalize(prior)
    l = np.asarray(likelihood, dtype=float)
    partition = _validate_groups(groups, p.size)
    coarse = np.asarray(coarse_likelihood, dtype=float)
    if coarse.shape != (len(partition),) or not np.all(np.isfinite(coarse)) or np.any(coarse < 0):
        raise ValueError("coarse likelihood must be nonnegative and match the groups")

    P = coarsen_probability(p, partition)
    effective = effective_coarse_likelihood(p, l, partition)
    fine_then_coarse = coarsen_probability(bayes_update(p, l), partition)
    coarse_then_update = bayes_update(P, coarse)
    defect = fine_then_coarse - coarse_then_update

    delta = effective - coarse
    Z_effective = float(effective @ P)
    Z_coarse = float(coarse @ P)
    if Z_effective <= 0 or Z_coarse <= 0:
        raise ValueError("positive fine and coarse evidence required")
    coarse_posterior = coarse_then_update
    factor_matrix = np.diag(P) - np.outer(coarse_posterior, P)
    factored = factor_matrix @ delta / Z_effective
    weighted_packet_loss = float(np.sum(P * np.abs(delta)))
    bound = 2.0 * weighted_packet_loss / min(Z_effective, Z_coarse)
    return {
        "coarse_prior": P,
        "effective_likelihood": effective,
        "coarse_likelihood": coarse,
        "information_loss_packet": delta,
        "fine_then_coarse": fine_then_coarse,
        "coarse_then_update": coarse_then_update,
        "defect": defect,
        "factor_matrix": factor_matrix,
        "factored_defect": factored,
        "weighted_packet_loss": weighted_packet_loss,
        "l1_bound": float(bound),
    }


def bayesian_sufficient_partition(
    likelihood: np.ndarray,
    groups: Sequence[Sequence[int]],
    *,
    atol: float = 0.0,
) -> tuple[bool, np.ndarray]:
    """Test blockwise constancy of one likelihood and return coarse values."""
    if not np.isfinite(atol) or atol < 0:
        raise ValueError("atol must be finite and nonnegative")
    l = np.asarray(likelihood, dtype=float)
    if l.ndim != 1 or not np.all(np.isfinite(l)) or np.any(l < 0):
        raise ValueError("likelihood must be a nonnegative vector")
    partition = _validate_groups(groups, l.size)
    coarse = np.zeros(len(partition), dtype=float)
    sufficient = True
    for a, group in enumerate(partition):
        values = l[list(group)]
        coarse[a] = float(values[0])
        sufficient = sufficient and bool(np.max(np.abs(values - values[0])) <= atol)
    return sufficient, coarse


def canonical_bayesian_partition(
    likelihood_family: Sequence[np.ndarray],
    *,
    atol: float = 0.0,
) -> tuple[tuple[int, ...], ...]:
    """Coarsest likelihood-resolving partition when ``atol == 0``.

    Exact packets are equality classes of complete likelihood profiles.
    For positive ``atol``, this is greedy representative clustering, which
    depends on state order; proximity within a tolerance is not an
    equivalence relation and is not an exact Bayesian sufficiency claim.
    """
    if not np.isfinite(atol) or atol < 0:
        raise ValueError("atol must be finite and nonnegative")
    family = [np.asarray(likelihood, dtype=float) for likelihood in likelihood_family]
    if not family:
        raise ValueError("at least one likelihood is required")
    size = family[0].size
    if any(l.ndim != 1 or l.size != size or not np.all(np.isfinite(l)) or np.any(l < 0) for l in family):
        raise ValueError("likelihoods must be nonnegative vectors of equal length")

    groups: list[list[int]] = []
    representatives: list[int] = []
    for state in range(size):
        for group_index, representative in enumerate(representatives):
            if all(abs(l[state] - l[representative]) <= atol for l in family):
                groups[group_index].append(state)
                break
        else:
            representatives.append(state)
            groups.append([state])
    return tuple(tuple(group) for group in groups)
