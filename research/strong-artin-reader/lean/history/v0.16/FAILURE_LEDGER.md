# Failure ledger — Strong Artin Lean v0.16

Failures below were not counted as proofs. Every retained module was subsequently recompiled successfully with warnings treated as errors.

## Runtime verification

- The reconstructed portable Lean kit began its broad self-test and passed initial checks, but the outer wrapper timed out before the complete kit suite returned. That incomplete run is not used as checkpoint evidence. v0.16 relies on narrow fresh compilation of its exact dependency closure.

## Lean invocation

- An early dependency compile was launched outside the pinned Lake workspace and reported an unknown `Mathlib` module prefix. The command was corrected to run from the kit workspace with an explicit staged `LEAN_PATH` and module root.

## Auxiliary-column/Jacobian development

- Initial proof attempts used a deprecated negation-normalization tactic and had ordering issues in the dual-injectivity argument. The final proof works directly in `ker J.dualMap`, constructs single auxiliary coordinates explicitly, and compiles without proof escapes.

## Coprime-kernel development

- The first index-divisibility expression was ambiguous between subgroup/cardinality lemmas. It was repaired by applying the index theorem to the explicit subgroup `(a.ker.map q)`.
- The prime specialization initially left the prime fact ambiguous. It was repaired using the typed fact `(Fact.out : Nat.Prime p)`.

## Affine cocycle packaging

- The first design tried to parameterize the action through the wrong homomorphism target. It was replaced by a `DistribMulAction`-based semidirect product.
- Finite-product and subgroup-range instances were initially unavailable because the required imports were missing. `Mathlib.Basic.Finite.Prod` and `Mathlib.Algebra.Group.Subgroup.Ker` were added.
- The final quotient is the actual range of the combined map, not the full ambient product; this avoids a false surjectivity assumption.

## Matrix cocycle conjugacy

- The initial inverse-cocycle proof used an additive-negation lemma in the wrong orientation.
- The first affine conjugation proof omitted the tactic import and later triggered unused-simplifier warnings under `-DwarningAsError=true`.
- The final proof derives the inverse formula explicitly and normalizes the affine expression without unused simp arguments.

## Local quotient interface

- The first version used `Module.Dual` without importing its definition and included unused simplifier arguments.
- The first nonvanishing proof relied on simplification across a quotient lift that did not fire.
- The final version uses explicit linear-map types and rewrites through the proved quotient evaluation theorem.

## Chebotarev-ready capstone

- The initial two-candidate nonvanishing proof simplified the sum insufficiently.
- A commuting-projector hypothesis was initially attached to the preliminary selector where it was not used, triggering an unused-variable error.
- The final design removes that hypothesis from the preliminary theorem and uses it only for full conjugacy-class stability.

## Extracted-archive replay

- After archive creation, a second fully extracted replay was attempted under a 20-minute wrapper. It compiled the three v0.15 dependencies and the first six v0.16 modules shown in its log, then the wrapper timed out while continuing the remaining modules. No theorem error or `sorryAx` had appeared. This timed-out attempt is not counted as a complete replay. The authoritative verification evidence remains the immediately preceding fresh 13-module replay from the release directory, which returned exit code `0`, plus the archive integrity test.
