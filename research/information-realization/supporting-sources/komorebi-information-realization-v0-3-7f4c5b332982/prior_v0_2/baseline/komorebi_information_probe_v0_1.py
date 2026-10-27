"""Komorebi Information Realization: finite-state proof companion v0.1.

Standard library only, Python >= 3.9. No claim of Lean verification.
Checks necessary inequalities exhaustively for tiny finite maps and
computes exact/probabilistic representation deficits for an observable system.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from itertools import product
from math import ceil, log2
from random import Random


def distinct_outputs(states, observation, target):
    cells = defaultdict(set)
    for x in states:
        cells[observation(x)].add(target(x))
    return dict(cells)


def kappa(states, observation, target):
    """Worst-case number of distinct target answers in one observation fiber."""
    cells = distinct_outputs(states, observation, target)
    return max(map(len, cells.values()), default=0)


def repair_bits(states, observation, target):
    """Smallest fixed-width supplemental code for exact target reconstruction."""
    k = kappa(states, observation, target)
    return ceil(log2(k)) if k > 0 else 0


def conditional_entropy(states, pmf, observation, target):
    """H(target | observation), in bits; pmf must sum to one."""
    assert sum((pmf[x] for x in states), Fraction(0)) == 1
    cell_mass = defaultdict(Fraction)
    joint_mass = defaultdict(Fraction)
    for x in states:
        p = pmf[x]
        cell_mass[observation(x)] += p
        joint_mass[(observation(x), target(x))] += p
    ans = 0.0
    for (z, _), p in joint_mass.items():
        if p:
            ans -= float(p) * log2(float(p / cell_mass[z]))
    return ans


def optimal_error(states, pmf, observation, target):
    """Bayes-optimal 0-1 error as an exact rational number."""
    assert sum((pmf[x] for x in states), Fraction(0)) == 1
    answer_mass = defaultdict(lambda: defaultdict(Fraction))
    for x in states:
        answer_mass[observation(x)][target(x)] += pmf[x]
    accuracy = sum((max(m.values()) for m in answer_mass.values()), Fraction(0))
    return 1 - accuracy




def conditional_means(states, pmf, observation, target):
    """Exact rational E[target | observation=z] on positive-mass observation cells."""
    obs_mass = defaultdict(Fraction)
    weighted_sum = defaultdict(Fraction)
    for x in states:
        z = observation(x)
        obs_mass[z] += pmf[x]
        weighted_sum[z] += pmf[x] * target(x)
    return {z: weighted_sum[z] / obs_mass[z]
            for z in obs_mass if obs_mass[z]}


def projection_increment(states, pmf, fine, coarse, target):
    """Squared norm of the removed information projector, exactly rational."""
    fine_means = conditional_means(states, pmf, fine, target)
    coarse_means = conditional_means(states, pmf, coarse, target)
    return sum((pmf[x] * (fine_means[fine(x)] - coarse_means[coarse(x)])**2
                for x in states), Fraction(0))


def optimal_squared_error(states, pmf, observation, target):
    """Exact Bayes MSE for a rational-valued target, using conditional means."""
    obs_mass = defaultdict(Fraction)
    weighted_sum = defaultdict(Fraction)
    for x in states:
        z = observation(x)
        obs_mass[z] += pmf[x]
        weighted_sum[z] += pmf[x] * target(x)
    means = {z: weighted_sum[z] / obs_mass[z] for z in obs_mass if obs_mass[z]}
    return sum((pmf[x] * (target(x) - means[observation(x)]) ** 2 for x in states),
               Fraction(0))


def information_profile(states, pmf, observation, target):
    return (repair_bits(states, observation, target),
            conditional_entropy(states, pmf, observation, target),
            optimal_error(states, pmf, observation, target))


def exhaustively_check_finite_composition():
    """Test the exact fiber-count composition theorem for all maps X->R->S.

    X has n=2,3,4 elements, and R and S are 3-element alphabets.
    Target F also uses a 3-element alphabet.  This is computational testing,
    NOT a formal proof of the general result.
    """
    count = 0
    for n in (2, 3, 4):
        states = tuple(range(n))
        maps = tuple(product(range(3), repeat=n))
        recodings = tuple(product(range(3), repeat=3))
        for r_values in maps:
            r = lambda x, v=r_values: v[x]
            for f_values in maps:
                f = lambda x, v=f_values: v[x]
                k_rf = kappa(states, r, f)
                for s_values in recodings:
                    s = lambda z, v=s_values: v[z]
                    sr = lambda x, r=r, s=s: s(r(x))
                    k_sf = kappa(states, sr, f)
                    k_sr = kappa(states, sr, r)
                    assert k_rf <= k_sf <= k_rf * k_sr
                    assert repair_bits(states, r, f) <= repair_bits(states, sr, f)
                    assert repair_bits(states, sr, f) <= (repair_bits(states, r, f)
                                                       + repair_bits(states, sr, r))
                    count += 1
    return count


def test_probability_transport(seed=7, trials=2000):
    """Numerical independent checks of average-deficit and Bayes-risk bounds."""
    rng = Random(seed)
    for _ in range(trials):
        n = rng.randrange(2, 10)
        states = tuple(range(n))
        r_map = [rng.randrange(n) for _ in states]
        f_map = [rng.randrange(n) for _ in states]
        s_map = [rng.randrange(n) for _ in states]
        weight = [rng.randrange(1, 11) for _ in states]  # strictly positive
        denom = sum(weight)
        pmf = {x: Fraction(weight[x], denom) for x in states}
        r = lambda x, v=r_map: v[x]
        f = lambda x, v=f_map: v[x]
        sr = lambda x, r=r, v=s_map: v[r(x)]
        h_r = conditional_entropy(states, pmf, r, f)
        h_s = conditional_entropy(states, pmf, sr, f)
        h_r_given_s = conditional_entropy(states, pmf, sr, r)
        e_r = optimal_error(states, pmf, r, f)
        e_s = optimal_error(states, pmf, sr, f)
        e_r_given_s = optimal_error(states, pmf, sr, r)
        assert h_r <= h_s + 1e-12
        assert h_s <= h_r + h_r_given_s + 1e-12
        assert e_r <= e_s
        assert e_s <= e_r + e_r_given_s
        numeric_target = lambda x, v=f_map: Fraction(v[x])
        mse_r = optimal_squared_error(states, pmf, r, numeric_target)
        mse_s = optimal_squared_error(states, pmf, sr, numeric_target)
        assert mse_s - mse_r == projection_increment(states, pmf, r, sr, numeric_target)
    return trials


def example():
    states = tuple(product((0, 1), repeat=3))
    def T(x):
        a, b, c = x
        return (b, c, a ^ b)
    def observed_history(x, horizon):
        outputs = []
        for _ in range(horizon + 1):
            outputs.append(x[0])
            x = T(x)
        return tuple(outputs)
    task = lambda x: observed_history(x, 2)  # the 3-bit observable future
    uniform = {x: Fraction(1, 8) for x in states}
    biased = {}
    for x in states:
        a, b, c = x
        biased[x] = (Fraction(1, 2)
                     * (Fraction(1, 4) if b else Fraction(3, 4))
                     * (Fraction(1, 8) if c else Fraction(7, 8)))
    rows = []
    for prior_name, prior in (("uniform", uniform), ("biased", biased)):
        for horizon in (0, 1, 2):
            obs = lambda x, h=horizon: observed_history(x, h)
            bits, h, e = information_profile(states, prior, obs, task)
            mse = optimal_squared_error(states, prior, obs, lambda x: 4*x[0] + 2*x[1] + x[2])
            rows.append((prior_name, horizon, len({obs(x) for x in states}), bits, h, e, mse))
    assert sum(biased.values()) == 1
    return rows


if __name__ == "__main__":
    tested = exhaustively_check_finite_composition()
    randomized = test_probability_transport()
    print("PASS: exact composition inequalities for", tested, "finite-map triples")
    print("PASS: probabilistic transport and exact L2 projection loss for", randomized, "randomized models")
    print("PRIOR   HORIZON   REPRESENTATIONS   REPAIR_BITS   H(F|R)   BAYES_ERROR   MSE")
    for label, horizon, partitions, bits, entropy, risk, mse in example():
        print(f"{label:8} {horizon:7d} {partitions:17d} {bits:13d} {entropy:8.6f}   {float(risk):.6f}   {float(mse):.6f}")
