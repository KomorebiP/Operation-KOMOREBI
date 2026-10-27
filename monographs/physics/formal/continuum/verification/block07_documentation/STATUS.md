# Komorebi Physics Lean v0.7.0 — Block 07

## Cumulative inventory

**Completed cumulative audit: PASS**, `verification/final/report.json`.

| Inventory | Count |
|---|---:|
| Block 07 new theorem declarations | 89 |
| Block 06 | 81 |
| Block 05 | 98 |
| Block 04 | 94 |
| Block 03 | 83 |
| Block 02 | 51 |
| Block 01 | 37 |
| Recovered Paper VII | 39 |
| **Cumulative theorem declarations** | **572** |
| Inventoried named declarations, including definitions/structures | 688 |
| Mathematical modules | 34 |
| Aggregate module | 1 |
| Intentionally invalid controls | 50 |
| Prior mathematical modules preserved unchanged | 29 |

Block 07 adds 62 general/support theorems and 27 example/support theorems, plus 19 definitions and one structure. Counts are not independent physical discoveries or an estimate of full-edition completion. Preservation uses `reference/block06_preservation.json` and every earlier preservation layer.

## Newly checked source coverage

Chapter 5.1–5.3, equations (5.1)–(5.21), and the sharp-current specialization (5.32). A finite positive Hermitian operator resolution is constructed without orthogonality or idempotence. Probability is the Born expectation, separately proved real, nonnegative and normalized when the state is normalized. Its actual derivative follows from the original state flow. The explicit antisymmetric current needs skewness to reproduce the derivative, not merely to be antisymmetric.

For moving effects, the actual operator derivatives yield Hermitian velocities and zero derivative of the operator sum. These results establish reality and zero sum of the moving source. The probability derivative has both source and exchange terms. Unitary conjugation is constructed and differentiated, preserving K = dot(U) U* and the sign of [K,F].

Actual coarsened operators, probabilities, currents, sources and moving derivatives satisfy the incidence-matrix formulas. Sequential and composed address maps agree. A separately labeled strengthening handles fixed nonnegative column-normalized real weights, with weighted composition and actual derivative formulas.

Exact normalized two-dimensional witnesses have nonzero effect overlap, failure of idempotence, Born probability distinct from squared effected norm, and nonzero currents. A globally positive sine-weighted scalar atlas has probability derivative 1/2 at zero with constant state and zero generator, exposing the indispensable moving source.

## Verification and trust boundary

Fresh Block 06 baseline: PASS, 483 theorems. Current production audit: PASS, all 34 mathematical modules plus aggregate freshly compiled, all 688 named declarations axiom-audited, and all 50 controls rejected for their intended diagnostics. All 29 preceding mathematical modules are unchanged.

Lean 4.34.0-rc2; Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06; nine exact clean dependency repositories; one worker; warnings as errors. Imported compiled cache reused, not rebuilt wholesale. Allowed axiom dependencies are propext, Classical.choice and Quot.sound. Master PDF SHA-256: ea289c7c1bd2090296e4d436c9ef38b617066becc40cd33c44507f1386a61bc0. No admitted active proof or custom axiom. The external archive-check report separately records the fresh-extraction run; package metadata cannot self-certify that external run.

## Remaining

The finite-atlas/bounded-operator Chapter 5.1–5.3 block is checked. No countable positive-operator-valued measure, unbounded generator, state-flow existence/uniqueness, universal factorization, or dilation theorem is claimed by this block. Postprocessing weights are fixed in time. Time-dependent weights require an additional derivative term. No physical interpretation identifies arbitrary effect motion with unitary motion.

Next literal target: Chapter 5.4, (5.22)–(5.31), actual Parseval-channel analysis/synthesis, reconstruction and dilation. The earlier conditional boundaries remain: positivity-preserving dynamical semigroups; zero-probability/q=1 entropy; general-graph convergence and rates; automatic coarse Markov closure; quantum relative entropy; infinite towers and formal-series convergence; countable/unbounded/trace-class extensions; full Chapter 3 inventory; relativity, gauge/gravity, cosmology and empirical adequacy.
