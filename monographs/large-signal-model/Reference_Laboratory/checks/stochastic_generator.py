"""Declared two-state generator for verification and synthetic reset trials only.

This module is intentionally separate from stochastic_reference.py. The learner
never imports it. Its state coordinates and invariant cone are verifier inputs.
"""
from __future__ import annotations
from itertools import product
import numpy as np
import sympy as sp
Q = sp.Rational
SYMBOLS = tuple(product(range(2), repeat=2))
T = (sp.Matrix([[Q(3,4), Q(1,4)], [Q(1,4), Q(3,4)]]),
     sp.Matrix([[Q(1,4), Q(2,3)], [Q(3,4), Q(1,3)]]))
O = (sp.diag(Q(1,4), Q(3,4)), sp.diag(Q(3,4), Q(1,4)))
INSTRUMENTS = {s: O[s[1]] * T[s[0]] for s in SYMBOLS}
INITIAL = sp.Matrix([Q(2,3), Q(1,3)])
MASS = sp.ones(1,2)
TESTS = ((), ((0,1),))
HISTORIES = TESTS
R = MASS.col_join(MASS * INSTRUMENTS[(0,1)])


def word_probability(word):
    state = INITIAL
    for s in word:
        state = INSTRUMENTS[s] * state
    return (MASS * state)[0]


def population_tables():
    h = sp.Matrix([[word_probability(history+test) for history in HISTORIES] for test in TESTS])
    gs = {s: sp.Matrix([[word_probability(history+(s,)+test) for history in HISTORIES]
                       for test in TESTS]) for s in SYMBOLS}
    b0 = sp.Matrix([word_probability(test) for test in TESTS])
    return h, gs, b0


def required_words():
    words = set(TESTS)
    for history in HISTORIES:
        for test in TESTS:
            words.add(history+test)
            for s in SYMBOLS:
                words.add(history+(s,)+test)
    return sorted(words, key=lambda w: (len(w), w))


def reset_success_count(word, n: int, rng: np.random.Generator) -> int:
    """Run independent simulated trajectories under the requested actions.

    Each trajectory starts at the declared initial distribution. No population
    success probability or binomial shortcut is passed to the estimator.
    """
    if n <= 0:
        raise ValueError('n must be positive.')
    if not word:
        return n
    states = (rng.random(n) >= float(INITIAL[0])).astype(int)
    matched = np.ones(n, dtype=bool)
    for action, target in word:
        transition = np.asarray(T[action], dtype=float)
        states = (rng.random(n) >= transition[0, states]).astype(int)
        p_one = np.where(states == 0, .75, .25)
        observations = (rng.random(n) < p_one).astype(int)
        matched &= observations == target
    return int(matched.sum())
