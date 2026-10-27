# Komorebi Physics Lean v0.6.0 — Block 06

## Cumulative inventory

**Completed cumulative audit: PASS**, recorded in `verification/final/report.json`. All source counts below match that completed report.

| Inventory | Count |
|---|---:|
| Block 06 new theorem declarations | 81 |
| Block 05 | 98 |
| Block 04 | 94 |
| Block 03 | 83 |
| Block 02 | 51 |
| Block 01 | 37 |
| Recovered Paper VII | 39 |
| **Cumulative theorem declarations** | **483** |
| Named declarations, including definitions/structures | 579 |
| Mathematical modules | 29 |
| Aggregate module | 1 |
| Intentionally invalid controls | 41 |
| Prior mathematical modules preserved unchanged | 25 |

Block 06 adds 52 general/support theorems and 29 example/formula/support theorems, plus eight definitions. It does not add 81 independent physical laws. Preservation is checked against `reference/block05_preservation.json`, with earlier preservation checks still active.

## New proved statements

Chapter 4.9: the actual refinement array obeys the source recurrence; all constant terms are preserved, degrees 1 through m cancel at depth m, and degrees above m have nonzero multipliers for b>1. The actual original error satisfies a separate exact identity before asymptotic estimates are applied.

A finite local expansion of the original sampled function implies the genuine Big-O order improvement. Little-o, fixed-column, one-sided positive-step and actual convergence versions are included. The general statement that the next surviving monomial is not of an extra order is proved on the punctured limiting filter. No assumption identifies f(0) with its limit.

Explicit finite-radius estimates give separate truncation and sample-noise contributions. A unit-bounded noise function is proved to produce output 3 at depth one. The original cubic family 7+2h+3h^2+h^3 has a proved input expansion and actual depth-two error h^3/8. The first three source formulas and an additional fourth formula are checked for arbitrary vector-valued samples.

## Trust boundary

Lean 4.34.0-rc2; Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06; nine exact clean dependency repositories; one worker; warnings as errors. Imported compiled cache reused, not rebuilt wholesale. Allowed axiom dependencies are propext, Classical.choice and Quot.sound. The master PDF SHA-256 remains ea289c7c1bd2090296e4d436c9ef38b617066becc40cd33c44507f1386a61bc0. No active admitted proof or custom axiom.

## Remaining

Chapter 4.9 is proved under explicit finite-expansion and fixed-depth assumptions. An infinite formal series is not proved convergent. No actual later physics discretization is newly proved to satisfy the expansion. Variable-depth/variable-ratio limits, infinite towers, floating-point implementation correctness, and removal of the sample-error floor are not claimed.

Next literal source: Chapter 5.1–5.3, positive/overlapping effects, actual probability derivatives, moving source terms, and exact coarse aggregation. Chapter 5.4's Parseval-channel realization/dilation follows.

Prior scope limits remain: existence/uniqueness, initial-state positivity preservation and completely positive dynamical semigroups; zero-probability/q=1 entropy limits; general graph convergence/rates; automatic coarse Markov closure; quantum relative-entropy dissipation; infinite-dimensional trace-class/countable/unbounded extensions; complete Chapter 3 inventory; relativity, gauge/gravity, cosmology and empirical adequacy. No full-edition completion percentage is justified.
