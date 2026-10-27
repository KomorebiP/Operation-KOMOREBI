# Integral p-adic polynomial contraction

Author: Komorebi P.

Frozen mathematical source: `formalization/PolynomialPadicContraction.lean`.
SHA256: `e667bd03d6577c8a7180659ef5fa95f068ccc172a7cf43d0f7f2508156f8e7ce`.

The source has two definitions and seven theorems. It treats actual multivariate polynomials with arbitrary coefficients in Z_p, for any prime p and any finite dimension, including dimension zero. No contraction or polynomial congruence condition is assumed as a premise of the fixed-point theorem.

## Statement and proof outline

For H in (Z_p[X_1,...,X_d])^d and c in Z_p^d, let
T(u)_i = c_i + p H_i(u).
Each polynomial is 1-Lipschitz for the supremum metric. This is proved by polynomial induction. The sum step uses the nonarchimedean norm inequality. The product-by-variable step expands the evaluation difference into two products, whose factors in Z_p have norm at most one. Consequently T is contracting with constant norm(p) < 1. Completeness gives a unique fixed point u.

If H(0)=0, then p^N divides every coordinate of c only if it divides every coordinate of u. This implication is proved for every natural N by induction using actual polynomial congruence preservation. The successor step combines p^N dividing H(u) with the extra factor p. The theorem does not depend on a selected finite search range or on numerical iteration.

## Development record

- `attempt_01.log`: failed. Two linter findings and an unresolved type/cancellation expression in the coordinate contraction estimate.
- `attempt_02.log`: failed. The mathematical terms checked, but one unnecessary sequence-focus linter remained.
- `attempt_03.log`: passed with warnings treated as errors and default heartbeat budget.
- `axiom_audit_01.log`: Lean exited successfully and printed the standard three axioms for all nine declarations. A misspelled LD_PRELOAD path produced loader warnings, so this is retained as a development run, not the clean audit.
- `axiom_audit_02.log`: same audit with the corrected runtime path.

The frozen mathematical source was not changed after `attempt_03.log`.

## Local primary dependencies inspected

Pinned Lean 4.34.0-rc2 and Mathlib revision aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

- `Mathlib/Topology/MetricSpace/Contracting.lean`: `ContractingWith`, `fixedPoint_isFixedPt`, `fixedPoint_unique`.
- `Mathlib/NumberTheory/Padics/PadicIntegers.lean`: complete normed ring structure, `norm_le_one`, `nonarchimedean`, `norm_lt_one_iff_dvd`.
- `Mathlib/Algebra/MvPolynomial/Basic.lean`: actual polynomial evaluation and polynomial induction.

No external novelty claim is made. This module is one dependency of the weighted polynomial lifting theorem; it does not by itself establish the normalization of a given weighted polynomial system.
