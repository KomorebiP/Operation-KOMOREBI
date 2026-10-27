# Block 03 semantic and hypothesis review

## Objects checked against the paper

| Mathematical role | Literal Lean object | What is proved |
|---|---|---|
| Operator action | `Module.AEval' T` | The existing polynomial-orbit span equals this module's span. |
| Primary model | Product of `k[X] ⧸ Ideal.span {p i ^ e i}` | An actual polynomial-linear equivalence is constructed from finite-dimensionality. |
| Irreducibility | `Irreducible (p i)` | Inherited from the proved PID decomposition, not assumed by the public operator theorem. |
| Nontrivial primary blocks | Positive `e i` | Exponent-zero blocks are removed by an explicit equivalence. |
| Primary label | `Ideal.span {p i}` | Associate irreducibles are grouped into the same label. |
| Residue image | `residueFiberMap` | Coordinatewise quotient factors, explicitly proved surjective. |
| Residue dimension | Dimension over `R ⧸ a`, a field | Lower bound is the number of primary factors, not degree-weighted base-field dimension. |
| Upper-bound generators | `coloredSeeds`, with `fiberColor` | CRT coefficients construct a single family achieving the maximum count under the shared action. |
| Minimum | `IsLeast {r | SeedNumberLE T r}` | Both existence at the stated rank and impossibility below it. |
| Canonical rank | Existing `seedFinrank` and `seedRank` over `operatorAlgebra T` | Equality follows through the existing proved minimum-to-rank bridge. |
| Invariant-factor chain | Actual equivalence plus positive degrees and `f i ∣ f j` for ordered indices | Count theorem is proved from those displayed hypotheses, not stored as a certificate. |

## Strongest public theorem

`exists_operator_primary_seed_formula` assumes only a field, a finite-dimensional vector space and its endomorphism, in addition to the standard algebraic typeclasses. It does not assume a decomposition, a Jordan basis, an eigenbasis, a polynomial cyclicity equivalence, or a seed-number certificate. Its conclusion includes an actual positive primary decomposition and the exact minimum.

`primaryGeneratorCount` is defined from the block count of a presentation obtained from proved existence. The canonical-rank equality is a theorem. The presentation record itself stores no seed conclusion.

## What is not smuggled into the theorem

The proof does not require the base field to be algebraically closed. It does not substitute eigenvalues for higher-degree irreducibles. It does not replace the shared operator algebra by a product of freely acting coordinate algebras. It does not count exponent-zero summands. It does not distinguish associate irreducibles as separate primary labels.

Classical choices occur in the finite enumeration of fibres, CRT lifts and the chosen normal-form presentation. These are permitted noncomputable mathematical constructions. They are not implementations of factorization or matrix normal-form algorithms.

## Exact remaining mismatch with the printed general statement

The complete printed theorem defines each multiplicity intrinsically as

    dim_{k[t]/(p)}(X_p / p(T)X_p).

The new theorem instead computes the maximum of primary-block counts in a proved actual presentation. The module map to each residue fibre is surjective, which is enough for the minimum formula. Surjectivity alone does not identify its kernel with the intrinsic p(T)X_p subspace. Nor does it identify the grouped primary product with the specific intrinsic X_p chosen in the publication.

The maximum is proved independent of the presentation. Individual-fibre intrinsic identification is not yet proved. The publication record `PSC-I-T-SINGLE-OPERATOR` therefore remains partial rather than being marked covered after an informal mathematical equivalence argument.

## Invariant-factor record

The invariant-factor corollary is conditional in the manuscript: it begins with a displayed nonconstant divisibility-chain decomposition. `invariantFactor_operator_seedRanks` has that exact mathematical input and derives the count. This is sufficient for that record to be covered. It does not establish an executable normal form or an unconditional existence theorem for sorted invariant factors.

The six-way cyclic criterion still includes additional intrinsic-primary and scalar-extension/geometric clauses. The new no-repeated-primary-label criterion proves an additional characterization, not all six clauses at once.

## Dependency boundary

The primary decomposition, quotient and CRT results imported from Mathlib are proved library theorems. The complete source-owned transitive axiom audit is the final check against unexpected assumptions. It is not replaced by a source search for the word `axiom`.

The final fresh compilation concerns the 28 project modules. Upstream cached Mathlib modules are authenticated and reused. Same-kernel replay is not independent foundational verification. No paper outside Paper I is audited by this block.
