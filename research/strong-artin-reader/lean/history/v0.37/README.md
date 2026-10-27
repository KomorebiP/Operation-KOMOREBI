# Strong Artin v0.37 — Effective resonant scalar horizon

Author: Komorebi P.

This checkpoint closes the effective survival problem for scalar unit prefixes,
including every positive degree divisible by the residue characteristic. It also
constructs actual invertible p-adic matrix roots in a fixed diagonal algebra.
It does not classify general matrix roots or prove Strong Artin.

The exact parent is `base/Strong_Artin_Lean_v0.36.0_Resonant_Branch_Compactness_Checked.zip`.
Its SHA-256 is `eb5b1430e26c864f4b39aa8bdaf337c5fb77b3c06058c6e24f5bc02e9d5a841b`.
The parent is preserved unchanged. No historical sibling has been merged.

## The new finite criterion

Let p be prime, d > 0, m >= 1, a in Z_p^×, and U in Z_p.
Write s = v_p(d), k = max(m,s+1), and

\[
H=\max(m,s+1)+s.
\]

Then a p-adic root z with z^d=U and z=a modulo p^m exists if and only if
there is b modulo p^H such that b^d=U modulo p^H and b=a modulo p^m.
There is no all-depth occupancy hypothesis and no requirement that p not divide d.
The horizon depends only on p,d,m, not on the higher digits of U.
This is an explicit sufficient horizon; optimality is not claimed.

For a deeper prefix m>s, the criterion simplifies to

\[
\exists!z\equiv a\pmod{p^m},\quad z^d=U
\quad\Longleftrightarrow\quad
a^d\equiv U\pmod{p^{m+s}}.
\]

Both existence-only and unique-existence versions are formalized. Shallow prefixes
may admit several roots, as happens with +1 and -1 over Z_2.

## Principal declarations

All names below are in `Komorebi.StrongArtin.EffectiveResonance`.

| Declaration | Scope |
| --- | --- |
| `polynomial_norm_difference` | Exact local norm scaling for a scalar integral polynomial |
| `polynomial_ball_root_iff` | Exact image criterion on a ball smaller than the derivative norm |
| `polynomial_prefix_root_iff` | Effective polynomial criterion at a prefix deeper than the derivative valuation |
| `scalar_deep_prefix_root_iff` | Unique scalar power root iff one congruence holds |
| `scalar_deep_prefix_exists_iff` | The same criterion for existence alone |
| `scalar_root_iff_finite_horizon` | Explicit horizon for every positive scalar unit prefix |
| `scalar_horizon_iff_all_deeper_levels` | One finite test supplies the all-depth finite premise |
| `scalar_no_root_iff_horizon_obstruction` | Failure is certified at the computed horizon |
| `diagonal_root_iff_finite_horizon` | Exact criterion within the fixed diagonal algebra |
| `exists_diagonal_matrix_unit_root` | Construction of an actual matrix-ring unit over PadicInt |

Read `PROOF.md` for the full argument and `RESEARCH_BOUNDARY.md` for its limits.

## Run

Lean 4.34.0-rc2 and Mathlib commit
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06` are required.
The runtime itself is not bundled in this checkpoint.

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 checks/scalar_survival.py --p 3 --degree 3 --prefix-depth 2 --prefix 4 --target 10 --precision 12
python3 checks/exact_horizons.py
```

The first command replays all four new source modules and an axiom audit in an
isolated output directory, reusing the pinned Mathlib cache. It authenticates the
parent archive but does not replay its historical modules. The new proof is a
direct Hensel argument and imports no project theorem from the parent.

The exact Python checker supplements the universal Lean proofs. The scalar CLI
tests canonical refinements at depth k and can generate digits of one surviving
root for an integer target. It raises an error, with no mathematical verdict,
if its candidate cap is exceeded.

## Controls

* Over Z_3, a unique cube root of 10 is congruent to 4 modulo 9.
* Over Z_3, no cube root of 1 is congruent to 4 modulo 9.
* Over Z_2, no square root of 1 is congruent to 9 modulo 16.
* Although 10^3=1 modulo 27, no p-adic cube root of 1 is 10 modulo 27.
* An actual invertible 2 by 2 matrix F over Z_3 is constructed with
  F^3=diag(10,28) and F=diag(4,1) modulo 9.

A horizon witness certifies survival of the original prefix. It need not itself
extend as a prefix at depth H. The last scalar control checks this distinction.

The mechanism is a consequence of classical Hensel lifting. No historical
novelty, automorphy, global localization, or Strong Artin conclusion is claimed.
