from __future__ import annotations

import json
import math
from pathlib import Path

import mpmath as mp
import numpy as np
import sympy as sp

import projector_generated_special_functions as pgsf

ROOT = Path(__file__).resolve().parents[1]


def test_declared_symbolic_checks_pass() -> None:
    checks = pgsf.run_symbolic_checks()
    assert len(checks) == 51
    assert all(check.passed for check in checks)


def test_carry_shift_and_weyl_commutator_exact() -> None:
    u = sp.symbols("u")
    for modulus in (2, 3, 5):
        carry = pgsf.carry_matrix_symbolic(modulus, u)
        vector = sp.Matrix([u ** (r + 1) for r in range(modulus)])
        lhs = pgsf.theta_vector_apply(carry * vector, modulus, u)
        rhs = carry * pgsf.theta_vector_apply(vector, modulus, u) + carry * vector
        assert all(sp.simplify(value) == 0 for value in lhs - rhs)


def test_exponential_sections_reconstruct() -> None:
    mp.mp.dps = 60
    z = mp.mpc("0.73", "-0.42")
    for modulus in (2, 3, 4):
        reconstructed = mp.mpc(0)
        for residue in range(modulus):
            section = pgsf.exp_section_hypergeometric(modulus, residue, z**modulus)
            reconstructed += z**residue * section
        assert abs(reconstructed - mp.e**z) < mp.mpf("2e-14")


def test_bernoulli_packet_reconstruction_and_refinement() -> None:
    mp.mp.dps = 60
    z = mp.mpc("2.7", "0.4")
    a = mp.mpf("0.37")
    for modulus in (2, 3, 4):
        direct = pgsf.bernoulli_interpolation(z, a)
        packet_sum = sum(pgsf.bernoulli_packet(z, a, modulus, r) for r in range(modulus))
        assert abs(direct - packet_sum) < mp.mpf("2e-14")
    parent = pgsf.bernoulli_packet(z, a, 2, 1)
    children = sum(pgsf.bernoulli_packet(z, a, 6, 1 + 2 * ell) for ell in range(3))
    assert abs(parent - children) < mp.mpf("2e-14")


def test_cyclotomic_detail_matches_lerch_form() -> None:
    mp.mp.dps = 60
    cases = ((1, 0, 3, 1), (2, 1, 4, 2), (3, 2, 2, 1))
    for modulus, residue, channels, detail in cases:
        direct = pgsf.cyclotomic_detail(mp.mpc("2.2", "0.31"), mp.mpf("0.43"), modulus, residue, channels, detail)
        closed = pgsf.cyclotomic_detail_lerch(mp.mpc("2.2", "0.31"), mp.mpf("0.43"), modulus, residue, channels, detail)
        assert abs(direct - closed) < mp.mpf("2e-14")


def test_bernoulli_euler_channel_identity_exact() -> None:
    x = sp.symbols("x")
    for order in range(1, 13):
        low, high = pgsf.bernoulli_euler_channels(order, x)
        assert sp.simplify(low - sp.bernoulli(order, x) / sp.sqrt(2)) == 0
        if order >= 1:
            assert sp.simplify(high + sp.Rational(order, 2) * sp.euler(order - 1, x) / sp.sqrt(2)) == 0


def test_third_root_norm_parity_law() -> None:
    omega = sp.symbols("omega")
    for order in range(2, 15):
        children = [sp.simplify(3 ** (order - 1) * sp.bernoulli(order, sp.Rational(r, 3))) for r in range(3)]
        # D = c0 + omega^2 c1 + omega c2 = A + B omega under omega^2=-omega-1.
        A = sp.simplify(children[0] - children[1])
        B = sp.simplify(-children[1] + children[2])
        norm = sp.factor(A**2 - A * B + B**2)
        if order % 2 == 0:
            expected = sp.factor((3 ** (order - 1) * (sp.bernoulli(order) - sp.bernoulli(order, sp.Rational(1, 3)))) ** 2)
        else:
            expected = sp.factor(3 * (3 ** (order - 1) * sp.bernoulli(order, sp.Rational(1, 3))) ** 2)
        assert sp.simplify(norm - expected) == 0


def test_generalized_transfer_matches_binomial_zeta_sum() -> None:
    mp.mp.dps = 50
    nmax = 200000
    mu = pgsf.mobius_sieve(nmax)
    for order in (1, 3, 7):
        direct = pgsf.generalized_transfer_direct(2.0, 2.0, order, 0.0, nmax, mu)
        finite_difference = sum((-1) ** j * math.comb(order, j) / mp.zeta(2 * j + 2) for j in range(order + 1))
        assert abs(direct - complex(finite_difference)) < 5e-10


def test_parameter_shift_recursion_numerically() -> None:
    nmax = 100000
    mu = pgsf.mobius_sieve(nmax)
    left = pgsf.generalized_transfer_direct(2.4, 1.3, 6, 0.7, nmax, mu)
    right = (
        pgsf.generalized_transfer_direct(2.4, 1.3, 5, 0.7, nmax, mu)
        - pgsf.generalized_transfer_direct(3.7, 1.3, 5, 0.7, nmax, mu)
    )
    assert abs(left - right) < 5e-13


def test_long_time_diagonal_power_is_positive_and_matches_direct_sum() -> None:
    nmax = 50000
    mu = pgsf.mobius_sieve(nmax)
    power = pgsf.long_time_power(2.0, 2.0, 120, nmax, mu)
    n = np.arange(2, nmax + 1, dtype=float)
    weights = mu[2:].astype(float) / n**2 * np.exp(120 * np.log1p(-1 / n**2))
    direct = float(np.sum(weights**2))
    assert power > 0
    assert abs(power - direct) < 1e-18


def test_energy_asymptotic_is_visible_in_generated_results() -> None:
    results = json.loads((ROOT / "results" / "results.json").read_text())
    assert results["energy_relative_error"] < 0.01
    assert results["symbolic_checks_passed"] == results["symbolic_checks"] == 51


def test_all_figures_exist_in_both_formats() -> None:
    pdfs = sorted((ROOT / "figures").glob("*.pdf"))
    pngs = sorted((ROOT / "figures").glob("*.png"))
    assert len(pdfs) == len(pngs) == 26
    assert {p.stem for p in pdfs} == {p.stem for p in pngs}


def test_manuscript_references_every_figure() -> None:
    manuscript = (ROOT / "Projector_Generated_Special_Functions_I.tex").read_text()
    for figure in (ROOT / "figures").glob("*.pdf"):
        assert figure.stem in manuscript
