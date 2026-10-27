# Progress ledger — Realization Boundaries Lean v0.6.0

## Authoritative checkpoint

- Parent: `Realization_Boundaries_Lean_v0.5.0_Checked.zip`.
- Accepted receipt: `verification/accepted_v0.6.0/run.json`, PASS.
- Production: 36 modules and the root import entrypoint.
- All 31 parent production modules and both publication artifacts remain unchanged.
- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

## Newly completed

1. `RootFibers`: actual root/kernel subtypes, additive kernel-coordinate equivalence, coset translation, full root parameterization and finiteness.
2. `RadicalCounts`: actual distinct-prime product, kernel and fiber cardinalities, zero branch for obstruction, literal equality of multiple subgroups and quotient cardinal.
3. `CyclicQuotients`: CRT ring equivalence, cyclic integer quotient, cyclic enumeration of the entire fiber, exact representative formulas and commuting quotient reductions.
4. `CyclicFiniteTargets`: finite quotients exactly cyclic squarefree targets, constructive converse, and literal kernel of every finite surjection.
5. `RootConsequences`: specified normalized root and conditional uniqueness, unrestricted uniqueness iff multiplier one, prime-power counts, and the infinite/nonempty multiplier-zero boundary.

## Verification totals

36 clean production rebuilds and kernel replays; 371 named source theorems/lemmas; 813 audited declarations; 173 positive contracts; 41 intended rejections; 118 passing command gates. Source/compiler/cache endpoint identity PASS. Axiom dependencies confined to `propext`, `Classical.choice`, `Quot.sound`.

The interrupted preliminary run and failed development compilations are preserved outside accepted evidence. Every shipped proof input matches the accepted final source snapshot.

## Coverage boundary

Newly COMPLETE book entries: **6.2 and 6.3**. The 45-record map remains `docs/MONOGRAPH_COVERAGE.json`. Entry **6.1 remains CORE_COMPLETE** because the book's particular finite normal-form arithmetic engine, support/cost bounds and extraction correspondence are not formalized by coordinate-root existence or a noncomputable definition. All earlier verified results remain unchanged.

## Next concrete restart point

Start `RealizationBoundaries/SubgroupSpectrum.lean` from the actual `finiteSupport` additive subgroup D. Target the book's subgroup/prime-spectrum classification (3.1), not a fresh arbitrary family of abstract groups.

1. For a subgroup H of D, define its prime spectrum using the actual standard prime seeds and define D_A using actual support containment.
2. For x in H and a nonzero p-coordinate, construct an integer multiple isolating that coordinate. The existing `finite_coordinate_interpolation` supplies the CRT step on the finite support. Normalize the nonzero coordinate to the standard seed by an invertible scalar.
3. Prove both inclusions H = D_spectrum(H), and use them to build an actual order isomorphism with Set Prime, including joins/intersections/complements.
4. Derive full invariance from the checked diagonality of every D endomorphism. Preserve actual source/target inclusions, not merely same cardinalities.
5. Recover the spectrum from prime-order torsion for abstract isomorphism classification. Handle empty and finite prime sets explicitly. Only then connect to cardinality and finite-stage observation examples.

Alternative independent targets: finitely generated subgroup structure (5.5), rational-dimension formulations (4.6), and the full directed-graph contract (1.8). Oracle-copy semantics and infinitely repeated grammar escape require their own precise encodings and must not be inferred from classical noncomputable constructions.

## Runtime recovery and reproduction

The five archived `Lean_Compact_01.zip` through `05.zip` member chunks concatenate to an XZ tar archive with SHA-256 `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`. Original Library IDs remain in the v0.1.0 ledger. The restored directory is `Komorebi_Portable_Lean_4.34.0-rc2`.

```bash
export KOMOREBI_LEAN_KIT=/path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 scripts/verify.py --output ../new-boundary-verification
```

Use a new evidence directory. The multi-gigabyte runtime/cache is not duplicated in the source package.

## Preservation and trust

Parent documentation is retained in `docs/history/v0.5.0`; earlier ledgers and accepted receipts remain. The original PDF and publication source ZIP are unchanged. Kernel replay uses the same Lean implementation and restored caches, not independent upstream authentication or external peer review.
