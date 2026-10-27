# Komorebi Cross-Radix Rigidity Lean v0.6.0

Durable checkpoint closing the exact finite degree-bounded rank/nullity block above certified v0.5.0.

## New checked results

- exact cardinality `T/g` of the retained width support;
- finite degree-bounded polynomial and residue-profile dimension formulas;
- exact range dimension `(T/g)(d+1)` for the bounded width projector;
- equality of range dimensions after DFT conjugation;
- exact preservation of projector range under reversible affine bookkeeping;
- rank `(T/gcd(T,m))(d+1)` for the bounded affine section normal form;
- nullity `(T - T/gcd(T,m)) * (d+1)`;
- explicit positive-characteristic collapse to evaluation when `char | m`;
- proof that `char ∤ m` implies the radix scalar is nonzero.

The exact Lean theorem for nullity is

`(T - T / gcd(T,m)) * (d+1)`.

## Verification

The new block was compiled with Lean `4.34.0-rc2`, pinned Mathlib, and `-DwarningAsError=true`. A second clean-path audit rebuilt the required custom dependencies into a fresh output directory before compiling `CrossRadixRankNullity.lean` and `CrossRadixV06AxiomAudit.lean`.

`#print axioms` on the load-bearing new theorems contains only `propext`, `Classical.choice`, and `Quot.sound`.

## Boundaries

Bell remains external. The naive base-independent integral normal form remains rejected. The theorem concerns the persisted projector-factorized affine section normal form and does not silently identify it with the stronger unsaved root-aggregation operator. Lean verification does not establish literature novelty or priority.
