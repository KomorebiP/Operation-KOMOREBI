#!/usr/bin/env python3
"""Exact finite regression of AVOC's Bayesian/model-to-policy bridge.

All arithmetic uses Fraction. Bounded evidence, not a replacement for the Lean
proofs and not a benchmark of real LLM behavior. Run with Python 3.10+.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json
import platform
import time

Row = tuple[F, ...]
Channel = tuple[Row, ...]
ROOT = Path(__file__).resolve().parents[1]


def validate_row(row: Row) -> None:
    if not row or any(x < 0 for x in row) or sum(row) != 1:
        raise ValueError('A probability row must be nonempty, nonnegative and normalized')


def l1(x: Row, y: Row) -> F:
    if len(x) != len(y):
        raise ValueError('Row dimensions differ')
    return sum((abs(a-b) for a, b in zip(x, y)), F(0))


def observation(b: Row, e: Channel) -> tuple[Row, tuple[Row, ...]]:
    validate_row(b)
    if len(b) != len(e) or not e or any(len(r) != len(e[0]) for r in e):
        raise ValueError('Channel dimensions differ')
    for r in e:
        validate_row(r)
    masses = tuple(sum((b[w]*e[w][o] for w in range(len(b))), F(0))
                   for o in range(len(e[0])))
    post = tuple(tuple(b[w]*e[w][o]/masses[o] for w in range(len(b)))
                 if masses[o] else b for o in range(len(masses)))
    return masses, post


def continuation(o: int, b: Row) -> F:
    # Each of these is bounded by 1 and 1-Lipschitz in belief L1.
    return max(b) if o == 0 else b[0]-b[1]


def quantize(b: Row) -> Row:
    # Binary belief, nearest quarter, deterministic upper tie-breaking.
    v = b[1]*4 + F(1, 2)
    integer = v.numerator // v.denominator
    p = F(integer, 4)
    return (1-p, p)


def main() -> None:
    start = time.monotonic()
    grid = tuple(F(k, 4) for k in range(5))
    beliefs = tuple((1-p, p) for p in grid)
    channels = tuple(((1-p, p), (1-q, q)) for p, q in product(grid, repeat=2))
    count = zero_events = codec_checks = 0
    max_ratio = F(0)
    for b, c, e, f in product(beliefs, beliefs, channels, channels):
        p, bp = observation(b, e)
        q, cp = observation(c, f)
        joint = sum((abs(b[w]*e[w][o]-c[w]*f[w][o])
                     for o in range(2) for w in range(2)), F(0))
        alpha, beta = l1(b, c), max(l1(e[w], f[w]) for w in range(2))
        avg = sum((p[o]*l1(bp[o], cp[o]) for o in range(2)), F(0))
        delta = l1(p, q)
        assert delta <= joint <= alpha+beta
        assert avg <= 2*joint
        for o in range(2):
            for w in range(2):
                assert p[o]*bp[o][w] == b[w]*e[w][o]
        actual = abs(sum((p[o]*continuation(o, bp[o])-q[o]*continuation(o, cp[o])
                          for o in range(2)), F(0)))
        assert actual <= 3*joint <= 3*(alpha+beta)
        coded = tuple(quantize(x) for x in bp)
        chi = sum((p[o]*l1(coded[o], bp[o]) for o in range(2)), F(0))
        assert chi <= F(1, 4)
        compiled = abs(sum((p[o]*continuation(o, coded[o])-q[o]*continuation(o, cp[o])
                            for o in range(2)), F(0)))
        assert compiled <= chi+3*(alpha+beta)
        if joint:
            max_ratio = max(max_ratio, avg/joint)
        count += 1
        codec_checks += 1
        zero_events += sum(x == 0 for x in p+q)

    # Rare-event boundary: large conditional error, small mean error.
    eps = F(1, 100)
    b = (F(1, 2), F(1, 2))
    e, f = ((1-eps, eps), (F(1), F(0))), ((F(1), F(0)), (1-eps, eps))
    p, bp = observation(b, e)
    q, cp = observation(b, f)
    assert p[1] == F(1, 200)
    assert l1(bp[1], cp[1]) == 2
    rare_average = sum((p[o]*l1(bp[o], cp[o]) for o in range(2)), F(0))
    assert rare_average == F(1, 50)

    # Model misspecification and an intentionally inaccurate continuation table.
    # Independent full sequence enumeration supplies the true optimum here.
    raw_rewards, learned_rewards = (F(1, 2), F(2, 5)), (F(3, 10), F(2, 5))
    sequences = q_checks = 0
    policy_results = []
    for n in range(8):
        all_values = []
        for seq in product(range(2), repeat=n):
            all_values.append(sum((raw_rewards[a] for a in seq), F(0)))
            sequences += 1
        optimum = max(all_values)
        deployed = n*raw_rewards[1]
        assert optimum == F(n, 2)
        assert optimum-deployed == F(n, 10)
        regret_bound = sum((2*(F(4*k, 15)+F(1, 5)) for k in range(n)), F(0))
        assert optimum-deployed <= regret_bound
        for k in range(n):
            w, next_w = F(k, 3), F(k+1, 3)
            assert abs(max(learned_rewards)+w-next_w) == F(1, 15)
            for a in range(2):
                raw_q = raw_rewards[a]+F(k, 2)
                model_q = learned_rewards[a]+w
                assert abs(raw_q-model_q) <= F(4*k, 15)+F(1, 5)
                q_checks += 1
        policy_results.append(dict(horizon=n, regret=str(optimum-deployed), bound=str(regret_bound)))

    rejected = 0
    for row in ((), (F(-1), F(2)), (F(1, 3), F(1, 3))):
        try:
            validate_row(row)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError('Invalid probability row accepted')
    report = dict(status='PASS', arithmetic='exact fractions.Fraction',
        bounds=dict(worlds=2, observations=2, prior_grid=[str(x) for x in grid],
                    bernoulli_channel_grid=[str(x) for x in grid],
                    constant_model_horizons=[0, 7]),
        counts=dict(joint_and_transport_cases=count, codec_cases=codec_checks,
                    zero_predictive_entries=zero_events, enumerated_action_sequences=sequences,
                    q_bound_checks=q_checks, invalid_probability_rows_rejected=rejected),
        rare_event=dict(probability='1/200', branch_posterior_l1='2', average_posterior_l1=str(rare_average)),
        max_average_to_joint_ratio=str(max_ratio), policy_results=policy_results,
        seconds=round(time.monotonic()-start, 3), python=platform.python_version(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        nonclaims=['not a universal proof by finite testing', 'not Lean-extracted',
                   'not empirical LLM validation', 'not efficient general planning'])
    out = ROOT/'results/v0.15.0/model_bridge_regression.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
