# Komorebi Physics Lean v0.5.0 — Block 05

## Cumulative inventory

The authoritative machine result is `verification/final/report.json`: **PASS**.

| Inventory | Count |
|---|---:|
| Block 05 new theorem declarations | 98 |
| Block 04 | 94 |
| Block 03 | 83 |
| Block 02 | 51 |
| Block 01 | 37 |
| Recovered Paper VII, freshly recompiled | 39 |
| **Cumulative theorem declarations** | **402** |
| Named declarations, including definitions/structures | 490 |
| Mathematical modules | 25 |
| Aggregate module | 1 |
| Intentionally invalid controls | 34 |
| Prior mathematical modules preserved unchanged | 20 |

Block 05 consists of 73 general/support theorems and 25 exact example/support declarations, plus 20 definitions. These are not 98 independent new physical laws. The previous 20 mathematical files are checked against `reference/block04_preservation.json`; older preservation checks remain active.

## New mathematics

**Chapter 4.7:** actual square-root jump matrices and the gain-minus-anticommutator expression give the exact population gain–loss derivative for general coherent inputs. Current antisymmetry, complex trace cancellation, subsystem flux and exact coarse current sums are derived. The full matrix rate is Hermitian for Hermitian inputs. None of this assumes positivity preservation of an initial-value solution.

**Off-diagonal and combined dynamics:** coherences have the actual derivative minus half the sum of the two escape rates times the coherence. Escape rates exclude self-jumps. The coherent Hamiltonian current is retained in combined dynamics. The population-information derivative interfaces start with the original matrix derivative.

**Chapter 4.8:** detailed balance with a fixed positive reference, nonnegative rates and positive populations gives a proved relative-entropy derivative equal to minus a nonnegative conductance sum. An explicit zero-edge branch avoids relying on log(0/0); active fluxes are proved positive. Nonincrease holds along supplied positive trajectories on convex time sets. Gibbs nonnegativity is proved separately for normalized positive distributions. Zero dissipation means equal density/reference ratios on active edges; equality with the reference is additionally proved when every distinct pair has positive rate and both distributions are normalized. General-graph convergence is not asserted.

**Exact tests:** the old coherent mixed density with rates 4 and 1 has actual matrix rate [[3/2,-5/8],[-5/8,-3/2]]. The correct reference (4/5,1/5) gives relative-entropy slope -3 log 2. A second positive normalized diagonal input and the wrong uniform reference give +log 3/4 along an actual matrix derivative. Exact counterexamples expose source orientation, square-root normalization, negative rates, loss factors, self-jump coherences and missing coherent currents. An empty transition graph rejects equilibrium uniqueness without connectivity assumptions.

## Trust boundary

Lean 4.34.0-rc2; Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06; nine exact clean dependency repositories; one worker; warnings as errors. Imported cache reused, not rebuilt wholesale. Only propext, Classical.choice and Quot.sound are allowed axiom dependencies. The master PDF SHA-256 remains ea289c7c1bd2090296e4d436c9ef38b617066becc40cd33c44507f1386a61bc0.

## Remaining

Next literal source is Chapter 4.9 (4.59–4.67), general refinement-cancellation towers. Exact polynomial cancellation and justified Big-O/asymptotic remainder claims must be distinguished. No full-edition completion denominator is established.

Still outside the checked scope: existence/uniqueness, initial-state positivity preservation and completely positive dynamical semigroups; zero-probability and q=1 entropy limits; general-graph convergence/rates; automatic coarse Markov closure; quantum relative-entropy dissipation; infinite-dimensional trace-class, countable/unbounded extensions; complete Chapter 3 inventory; later relativity, gauge/gravity and cosmology sectors; and empirical adequacy.
