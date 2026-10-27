# Komorebi Physics Lean v0.3.0 — Checked Block 03

## Fresh cumulative result

`verification/final/report.json`: **PASS**.

| Inventory | Count |
|---|---:|
| Block 03 new theorem declarations | 83 |
| Block 02 new theorem declarations | 51 |
| Block 01 new theorem declarations | 37 |
| Preserved Paper VII theorem declarations, freshly recompiled | 39 |
| **Cumulative theorem declarations** | **210** |
| All named declarations audited, including definitions/structures | 263 |
| Mathematical modules freshly compiled | 15 |
| Aggregate import module freshly compiled | 1 |
| Intentionally invalid controls correctly rejected | 15 / 15 |
| Prior mathematical modules preserved byte-for-byte | 10 / 10 |

The 83 new theorems comprise 9 nonlinear-flow, 20 refinement-tower, 31 mixed-state, 7 source-balance and 16 exact-example declarations. The theorem count is not a count of independent new discoveries. The named audit covers 20 new definitions/structures as well as the new theorem declarations.

## New checked mathematics

- **Chapter 4.1:** actual state-dependent skew-flow packet derivatives, current antisymmetry, subsystem/coarse balance, and all-time norm/total-energy constancy along an assumed trajectory. No generator-map differentiability is needed for these first-order consequences.
- **Chapter 4.2:** finite matrix trace-probability derivatives from the actual von Neumann derivative; trace reality; conjugation/cyclicity; current antisymmetry; trace conservation; subsystem flux; PSD probability bounds and normalization; pure-state specialization; actual mixed-state coarsening.
- **Chapter 4.3:** address-map pushforward composition, actual coarse projectors/packets/corners/energies/currents, incidence composition and current-matrix congruence. An arbitrary-depth list theorem uses one fixed finite label type; two-stage composition permits different finite label types.
- **Chapter 4.5:** source-driven scalar balance, actual subset/coarse derivatives and explicit survival of total sources.

Exact examples use a normalized positive mixed 2×2 density matrix with currents −1/2 and +1/2. An actual local affine density curve has those probability derivatives at zero. Additional exact theorems expose the roles of Hermiticity, conjugation, source terms and genuine partition incidence.

## Hypotheses versus conclusions

Fine atlas laws, the original trajectory derivative and the skew/Hermitian assumptions are inputs. Coarse atlas laws, probability reality/positivity under PSD input, currents, antisymmetry and quantum packet derivatives are derived. At the separate universal scalar-balance interface, the scalar balance equation itself is explicitly an input.

State positivity and trace one are inputs to the probability-bound theorem; they are not claimed to follow from arbitrary initial data or from trace preservation alone. Binary entries do not replace the partition hypothesis. Generic weighted current aggregation is an algebraic statement, not automatically an orthogonal-atlas construction.

## Trust boundary

Lean 4.34.0-rc2, Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, nine clean pinned dependency trees. One worker, warnings as errors. The active source precheck and full axiom inventory pass. Only `propext`, `Classical.choice` and `Quot.sound` occur as axiom dependencies. The imported compiler/Mathlib cache was not independently rebuilt wholesale.

The full master PDF is preserved. Its SHA-256 is `ea289c7c1bd2090296e4d436c9ef38b617066becc40cd33c44507f1386a61bc0`. All ten prior mathematical source modules are checked against `reference/block02_preservation.json`.

## Not completed

No tensor-product mixed-state marginals, entropy/moment/Rényi derivatives, Lindblad diagonal reduction, Chapter 5 positive/overlapping atlas program, countable/unbounded extensions, full Chapter 3 inventory, gravitational/cosmological formalization, full-edition completion fraction, ODE existence/uniqueness, density-positivity preservation from initial data, or empirical physics claim is supplied by this release.

The next literal target is (4.23)–(4.28), then (4.35)–(4.44), then (4.45)–(4.52). See `CONTINUE_HERE.md`.
