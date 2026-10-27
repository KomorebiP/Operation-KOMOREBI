# Komorebi Physics Lean v0.4.0 — Block 04

## Fresh cumulative result

`verification/final/report.json`: **PASS**.

| Inventory | Count |
|---|---:|
| Block 04 new theorem declarations | 94 |
| Block 03 new theorem declarations | 83 |
| Block 02 new theorem declarations | 51 |
| Block 01 new theorem declarations | 37 |
| Recovered Paper VII theorem declarations, freshly recompiled | 39 |
| **Cumulative theorem declarations** | **304** |
| All named declarations audited, including definitions/structures | 372 |
| Mathematical modules freshly compiled | 20 |
| Aggregate module freshly compiled | 1 |
| Intentionally invalid controls correctly rejected | 23 / 23 |
| Prior mathematical modules preserved byte-for-byte | 15 / 15 |

The 94 new theorems comprise 17 tensor-atlas, 32 partial-trace, 12 information-transport, five entanglement-witness and 28 exact-example declarations. The named inventory also includes 15 new definitions. Counts are not a number of independent new discoveries.

## New checked mathematics

**Chapter 4.4:** the actual Kronecker atlas has proved Hermiticity, orthogonality and completeness. Both complex marginal-trace identities hold for arbitrary joint matrices. Under PSD and trace one, joint packet probabilities are genuine normalized probabilities. Marginals are identified with actual address coarsening and actual reduced states, not restricted to product inputs.

**Additional partial-trace infrastructure:** explicit entrywise reductions preserve PSD, trace and Hermiticity; product normalization factors, local multiplication and remote cyclicity are proved; actual matrix derivatives induce actual reduced derivatives. These are finite-matrix results, not infinite-dimensional trace-class theorems.

**Chapter 4.6:** actual Shannon, real-order moment and Rényi derivatives under explicit positivity and differentiability assumptions. The generic weighted antisymmetric identity is proved. Matrix-flow interfaces discharge the scalar balance assumption from the original density derivative. Rényi requires nonempty index type and q≠1, with positivity of the moment proved. The q=1 limit is not formalized.

**Exact entanglement test:** the Bell joint density is PSD, trace one and idempotent. Its marginals are both I₂/2, while joint probabilities do not factor. A distinct dephased density has the same marginals. An exact negative partial-transpose pairing excludes every finite nonnegative mixture of product pure states under the explicit decomposition definition. No separability equivalence theorem beyond that definition is claimed.

**Exact information-rate tests:** the local positive normalized trajectory (1/4+a t, 3/4-a t) has rates S'=a log 3, M₂'=-a and H₂'=8a/5 at zero. The choices a=±1 prove opposite entropy signs. This refutes automatic packet-entropy monotonicity from antisymmetry alone; it is not a statement about thermodynamic entropy production under additional physical assumptions.

## Hypotheses and trust boundary

Fine projector laws and the original trajectory derivative are explicit inputs. Joint atlas laws, reductions, current consequences and functional derivatives are proved. PSD/trace-one inputs are required for the density interpretation. Strict packet positivity is stronger than PSD; the Bell joint coordinate probabilities have zeros and do not satisfy the entropy theorem's strict-domain hypothesis.

Lean 4.34.0-rc2; Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`; nine clean pinned dependencies; one worker; warnings as errors. The imported dependency cache is not rebuilt wholesale. Only `propext`, `Classical.choice` and `Quot.sound` may occur as audited axioms.

The master PDF is unchanged: SHA-256 `ea289c7c1bd2090296e4d436c9ef38b617066becc40cd33c44507f1386a61bc0`. Every Block 03 mathematical file is checked against `reference/block03_preservation.json`.

## Remaining

Lindblad diagonal reduction is next. Still unproved here: flow existence/uniqueness, density positivity from initial data, zero-probability and q=1 entropy limits, universal entropy monotonicity, infinite-dimensional partial trace, countable/unbounded extensions, complete Chapter 3 inventory, Chapter 5 and later physics, and empirical adequacy. Full-edition completion has no established denominator.
