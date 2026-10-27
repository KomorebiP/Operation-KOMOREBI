# Realization Boundaries — checked Lean companion v0.4.0

**Current checkpoint:** `verification/accepted_v0.4.0/run.json`, PASS. This is a continuation of the checked v0.3.0 source, not a claim that the entire book is formalized.

## What is new

Six new modules prove the full diagonal description of arbitrary group homomorphisms, the actual endomorphism rings, the rational quotient scalar and its ring laws, the automorphism criterion, and completion reflection for a supplied map. All twenty inherited production modules and the finalized monograph are unchanged.

For every rational preimage H_W inside the actual product P, an arbitrary additive homomorphism has a unique coordinate formula. Continuity follows from the formula and is not assumed. For the selector groups G_A the converse is exact: a coordinate family c is admissible precisely when c*u_A differs from a target rational section by an element of D.

The endomorphism ring consists of admissible families eventually equal to one rational along the selected primes. The rational scalar is unique and gives a surjective ring homomorphism. Automorphisms require every prime coordinate to be nonzero, not merely a nonzero rational quotient scalar. The original-group inverse is the exact reciprocal multiplier and its admissibility is proved.

The induced map on canonical profinite completions is explicitly constructed, continuous, eta-compatible and unique. For a supplied homomorphism between paired groups it is an isomorphism exactly when the original map is. This does not reconstruct an unknown source from its completion and does not apply to the proper D -> G_A inclusion.

The actual End(D) is also identified as a ring with the full product of the prime fields.

## Main entrypoints

| Declaration | Use |
|---|---|
| `hom_coordinate_formula` | Derived diagonal formula for every actual homomorphism. |
| `selectorHomEquiv` | Full classification by the finite-defect realization condition. |
| `endomorphismRingEquiv` | Ring equivalence, including composition multiplication. |
| `quotientScalar` | Unique rational quotient character with checked ring laws. |
| `selector_endomorphism_automorphism_iff` | Exact all-coordinate automorphism criterion. |
| `paired_completion_reflects_isomorphisms` | Reflection for the same supplied map. |
| `finiteSupportEndomorphismRingEquiv` | End(D) as the full coordinate ring. |

All names lie in `RealizationBoundaries`. Import the root module `RealizationBoundaries` to access the complete current development. Exact hypotheses and source locations are in `docs/EXACT_STATEMENT_REVIEW.md` and `docs/NAMED_THEOREMS.json`.

## Verification

The accepted run cleanly rebuilt 26 production modules and the root entrypoint, audited 628 declarations, compiled 101 positive contract proofs, accepted 26 intended rejection controls, and replayed all 26 modules through Lean's kernel checker. All 83 command gates passed. There are 260 explicitly written source theorems and lemmas. Those counts measure different things and are not discovery counts or completion percentages.

## Reproduce

Use the pinned Linux portable kit with Lean 4.34.0-rc2 and the recorded Mathlib revision. No network update is required. The multi-gigabyte runtime is intentionally excluded from this source distribution.

```bash
export KOMOREBI_LEAN_KIT=/path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 scripts/verify.py --output ../realization-boundaries-fresh-verification
```

Choose a new output directory. The verifier checks all pinned package revisions, takes a source/cache baseline, deletes project compiled output, rebuilds serially, audits declarations and axioms, compiles contracts, checks expected diagnostic failures, replays production modules and compares final hashes. Failed gates exit nonzero. Deliberately invalid files in `tests/negative` are never imported by production.

For a single-source development check, use `python3 scripts/check.py SOURCE --kit PATH`. This is not a substitute for the clean verifier.

## Handoff map

`CURRENT_CHECKPOINT.json` identifies the accepted receipt. `PROGRESS_LEDGER_v0.4.0.md` is the restart ledger. `LEAN_VERIFICATION_REPORT.md` records the run and its limits. The coverage JSON retains all 45 numbered book results, with five newly complete entries: 2.2, 7.5, 7.7, 7.8 and 9.4. `docs/DEVELOPMENT_INCIDENTS_v0.4.0.md` retains failures and corrections; historical docs and accepted receipts remain in place.

The next block is the exact seed-generation obstruction and rank comparison, with root-fiber counts, CRT cyclicity, oracle semantics and grammar escape still explicitly pending. Definitions marked noncomputable do not certify those oracle claims.

## Trust and license

Only `propext`, `Classical.choice`, and `Quot.sound` are allowed as transitive proof axioms. Production has no admitted proof, custom axiom or unsafe declaration. Kernel replay uses Lean's own implementation; the restored compiler and imported caches were not rebuilt from source or independently authenticated upstream. Endpoint equality does not detect every possible transient change. No external peer review, independent second kernel, Python extraction theorem, or historical-priority claim is made.

The new Lean source and verification tooling retain the open license in `LICENSE`. Archived publication materials retain their own license files. No compiler, external dependency cache or font file is included in the source package.
