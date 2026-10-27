# Proof Boundaries — v0.6.0

## Certified meaning

A v0.6 claim is certified only when its exact statement occurs in the saved `src/` snapshot and the required module passes the pinned strict Lean gate. `AUDIT.json` is the machine-readable ledger.

## Rank/nullity scope

The exact rank and nullity formulas are proved for the finite degree-bounded complex profile realization of the saved projector-factorized affine section normal form. They do not certify equality with an unsaved stronger root-aggregation section operator.

## Characteristic scope

The rank/nullity proof uses the complex realization. A separate generic field theorem proves the exact obstruction: when `[CharP K p]` and `p | m`, affine polynomial substitution collapses to evaluation. Another theorem proves `p ∤ m` implies `(m : K) ≠ 0`. v0.6 does not claim a full Reynolds/DFT rank theorem over arbitrary positive-characteristic or arbitrary characteristic-zero coefficient fields.

## Bell remains external

Bell's generalized Cobham theorem is not formalized. Future work may import only an explicit statement-level conclusion as a hypothesis/interface.

## Integral normal form remains rejected

The square-sequence obstruction from earlier checkpoints remains in force. No base-independent integral lattice normal form follows from the complex DFT/Reynolds results. Future integral work must be localized and retain Smith/Fitting/radix-local defect data.

## Positive-radix boundary

The raw-radix lcm and rank/nullity theorems use positive radices. Zero radices are not silently incorporated.

## Still open after this checkpoint

- precise Bell-conclusion interface;
- uniform all-positive-radix common-hull theorem;
- active-shell / shell-jet minimal-hull sharpening;
- localized integral common-lattice theory;
- any identification of the saved affine normal form with a stronger unsaved root-aggregation operator.

## Novelty boundary

Lean certification proves the formal statements relative to their imports and hypotheses. It does not establish literature novelty, publication priority, or peer review.
