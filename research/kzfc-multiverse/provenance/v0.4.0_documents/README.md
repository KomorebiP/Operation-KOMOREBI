# Komorebi KZFC Residual Reflection v0.4.0

## Main result

For every regular infinite cardinal kappa, the following precisely specified principles are equivalent:

    FixedDomainKRR(kappa)
      <-> FixedDomainKRR0(kappa)
      <-> FixedDomainCompactness(kappa)
      <-> BooleanCompactness(kappa)
      <-> CompleteFilterExtension(kappa)
      <-> FineUltrafilterPrinciple(kappa).

The filter extension property is independently defined using actual Mathlib filters and ultrafilters. It is not a renamed version of the compactness conclusion. The reverse construction builds an ultrafilter from a satisfying Boolean assignment. The forward construction uses the explicit fine cone filter and the preceding ultrafilter compactness theorem.

Under the ordinary all-sets interpretation at regular uncountable kappa, this is the standard strong-compactness form, not a newly discovered stronger large-cardinal axiom. See LITERATURE.md for the external terminology check and its limits.

## Additional results

* The ordinary baseline at aleph0 is proved without any extra existence hypothesis.
* For every infinite cardinal mu, fixed-domain compactness and the corresponding residual/filter principles fail at mu-plus. The proof gives a uniform family of binary distinct-value constraints, not a bounded numerical test.
* The candidate uncountable residual-existence assertion is equivalent to the independently stated uncountable filter-extension existence assertion. Neither is proved to hold or inserted as an axiom.
* All eight predecessor mathematical modules are byte-for-byte preserved. Their 65 named theorem declarations remain, including the exact integer-tower obstruction and its finite-support counterexample.

## Verification

Final status: PASS. There are 97 audited theorem declarations, 32 added in this block. Counts include auxiliary lemmas and interfaces, not 97 independent discoveries. A clean project build completed with 1204 jobs, including dependencies. The verifier reread all active source files with warnings as errors and checked all named theorem axiom dependencies. Only `Classical.choice`, `Quot.sound`, and `propext` were observed. No custom axiom, proof placeholder, or prohibited native proof shortcut occurs in active source. Both deliberately invalid compiler controls were rejected for the expected reasons.

The proof-input hashes match before and after the final run. The final record is `verification/RESULTS.json`. Failed development attempts and the interrupted verification drivers are retained separately. The final complete run supersedes, but does not erase, the interrupted runs.

## Contents

`Komorebi/Foundation` contains twelve mathematical modules and the complete axiom audit. The four new modules are `FilterExtension.lean`, `ConeFilter.lean`, `ResidualClassification.lean`, and `SuccessorObstruction.lean`. `THEORY.md` gives the mathematical construction and exact scope. `PROOF_BOUNDARY.md` separates proved results from remaining obligations. `THEOREM_INDEX.md` and `verification/theorems.json` identify the checked declarations. `scripts/verify.py` reproduces the proof checks and negative controls.

## Foundation boundary

These are universe-polymorphic theorems in Lean's type theory. They are not yet encoded as first-order derivations about models of ZFC. No independence, relative-consistency, or uncountable existence theorem is claimed. The classification concerns the declared small-domain, small-scope semantic constraint class, whose obstruction encoding is concentrated in degree zero. It does not classify arbitrary derived residual systems, or identify the explicit integer cokernel with Mathlib's right-derived limits.

Pinned environment: Lean 4.34.0-rc2, Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Compiler, dependency source/cache, and build products are excluded from the distribution. See REPRODUCE.md.
