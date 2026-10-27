# Progress ledger — Realization Boundaries Lean v0.2.0

## Authoritative checkpoint

- Parent: `Realization_Boundaries_Lean_v0.1.0_Checked.zip`.
- Current accepted receipt: `verification/accepted_v0.2.0/run.json`, PASS.
- Current source: fifteen modules under `RealizationBoundaries/`, plus the root entrypoint.
- All nine inherited production modules are unchanged. See `provenance/PARENT_SOURCE_IDENTITY.json`.
- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

## Newly closed endpoints

The pure-preimage order correspondence, countability of actual infinite groups, product topology and density, continuous extension and natural finite-target equivalence, the actual canonical profinite completion, equality of the full profinite topology with the induced topology, residual finiteness, and the proper D inclusion with an isomorphism on completions.

The completion is Mathlib's limit over all finite-index normal additive subgroups. The proof constructs both comparison maps, verifies their inverse laws, and preserves the original canonical inclusion. No completion equivalence is assumed.

## Verification totals

Fifteen production modules, 146 explicitly named source theorems/lemmas, 391 audited declarations including generated helpers, 36 positive contracts, 14 intended rejections, and fifteen successful same-kernel replays. All accepted proof sources and recorded compiler/imported cache endpoints are unchanged across the accepted run. No admitted production proof or project-specific axiom was accepted.

## Current theorem-map boundary

Use `docs/MONOGRAPH_COVERAGE.json`. Eight book entries moved to COMPLETE: 2.1, 2.5, 4.2, 4.4, 4.5, 5.1, 6.4 and 9.2. Proposition 4.6 has the countability equivalence with its quotient, but not yet the printed dimension-language equivalence. The cyclic CRT clause of 6.3 and exact root counts remain open formalization tasks.

## Next major restart point

Start `RealizationBoundaries/TailSignature.lean` from `CompletionConsequences` and `Sections`.

1. For a nonzero rational coordinate r and finite-support d, prove that the nonzero-coordinate set of s_A(r)+d differs from the selected prime set at only finitely many primes. The exceptional set must explicitly include numerator primes, denominator primes and support(d).
2. Combine that signature with `preimage_root_iff` to prove the eventual divisibility signature of every infinite-order element.
3. Prove both directions of unmarked isomorphism classification. Preserve the exact conclusion: selectors agree modulo finitely many changes, not literal equality. The forward direction must derive preservation from actual additive isomorphisms. The converse should identify the literal preimage subgroups when selectors differ finitely.
4. For the all-homomorphism block, use the already checked finite-target factorization to derive coordinate behavior. Do not postulate diagonality as an input.

A separate follow-on can close root-fiber counts, the cyclic CRT equivalence, topological cyclicity, and the rational-dimension formulation. The oracle theorem needs explicit computable-presentation and oracle semantics; noncomputable Lean definitions do not establish that theorem.

## Runtime restart

The five mounted or Library archives `Lean_Compact_01.zip` through `Lean_Compact_05.zip` restore the portable kit. The concatenated archive hash is `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`. The parent ledger retains their exact Library identifiers. In a fresh runtime, do not infer filesystem paths from Library titles. The current source package excludes the large compiler/cache payload.

## Preservation and limitations

The printed monograph and original final publication ZIP were not changed. Prior accepted evidence is under `verification/history/v0.1.0/accepted`; prior documentation is under `docs/history/v0.1.0`. The old v0.1.0 ledger is retained as a historical checkpoint and is superseded by this one. Current failed development attempts remain in the development logs. This is internal formal verification, not external peer review.
