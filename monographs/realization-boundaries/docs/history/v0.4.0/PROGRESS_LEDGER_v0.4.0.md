# Progress ledger — Realization Boundaries Lean v0.4.0

## Authoritative checkpoint

- Parent: `Realization_Boundaries_Lean_v0.3.0_Checked.zip`.
- Accepted receipt: `verification/accepted_v0.4.0/run.json`, PASS.
- Current production source: twenty-six modules and one root import entrypoint.
- All twenty parent production modules are unchanged. See `provenance/PARENT_v0.3.0_SOURCE_IDENTITY.json`.
- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`; all nine lockfile revisions checked.

## Newly completed

1. Arbitrary maps between actual rational preimages are uniquely diagonal, automatically continuous, and induce rational-linear quotient maps. No diagonal or continuity hypothesis is used.
2. Exact admissibility and the finite-defect scalar condition classify all selector-group homomorphisms. Ring composition gives a genuine endomorphism-ring equivalence.
3. The unique rational quotient scalar is a surjective ring homomorphism, with its exact zero-scalar kernel and explicit lifts. The lifts are not claimed additive.
4. Every-coordinate nonvanishing is the exact automorphism criterion for infinite-selector groups. Reciprocal maps are proved to preserve the original rank-one groups. Supplied injective and supplied surjective maps in this family are bijective.
5. The induced continuous map on canonical completions is built, eta-compatible, unique, compositional and faithful on family hom sets. The supplied-map reflection theorem for paired groups is complete.
6. The actual ring End(D) is isomorphic to the full prime-coordinate product. Every endomorphism preserves zero coordinates.

## Verification totals

26 cleanly rebuilt production modules; 260 explicitly named source theorems/lemmas; 628 audited declarations; 101 positive contract declarations; 26 intended rejection controls; 26 same-kernel replays; 83 passing command gates. The source and recorded compiler/dependency endpoints match. Production axiom dependencies are limited to `propext`, `Classical.choice`, and `Quot.sound`.

## Coverage boundary

The 45-entry monograph map remains `docs/MONOGRAPH_COVERAGE.json`. Entries 2.2, 7.5, 7.7, 7.8 and 9.4 are newly COMPLETE. The earlier common-completion and classification theorems remain checked. Entry 9.3 remains PARTIAL because the global categorical statement for all residually finite groups has not been supplied. The exact Pro-object decoder interface in 9.1 is also still separate.

Do not confuse a nonzero rational quotient scalar with an automorphism: a checked projection has scalar one but kills complementary prime seeds. Do not broaden supplied-map reflection from rank-one selector groups to all preimages: the checked inclusion D -> G_A is not surjective while its completion map is bijective.

## Next major restart point

Start `RealizationBoundaries/SeedGeneration.lean` from the actual diagonal and countability interfaces, preserving all accepted sources and evidence.

1. Define the precise endomorphism-generated subgroup for a seed set, and its topological closure. Choose a definition that directly matches the book's generation contract instead of assuming a seed-rank value.
2. For any finite seed set in D, select a missing prime coordinate. Use `finiteSupport_endomorphism_preserves_zero` and closure of the coordinate kernel to prove both algebraic and topological non-generation.
3. For finitely many elements of G_A, prove that their nonzero support outside the paired selected set is finite. Choose an omitted unselected prime; use `hom_preserves_zero_coordinate` or `hom_coordinate_formula` to obtain a nonzero prime-seed witness outside the generated hull and its closure.
4. Establish exact cardinal rank aleph_0 with a genuine countable upper bound and finite-cardinal lower bound. The inherited countability theorems supply the upper side; do not silently count topological and algebraic seed rank as the same contract.
5. Separately prove topological cyclicity of P from actual finite-coordinate Chinese-remainder realization. This supplies the comparison needed to close book 7.9 completely. Merely proving the no-finite-seed half is not full coverage of that result.

A distinct continuation can handle root-fiber equivalences/cardinality, radical cyclic quotient identifications, and rational dimension language. Oracle claims require explicit presentation/relative-computability semantics and must preserve the marked/unmarked distinction. The grammar diagonalization must disagree infinitely often because finite selector changes preserve the unmarked group.

## Implementation details worth retaining

`homDiagonal` reads the scalar from the image of the actual prime seed. `diagonalTail` derives rational linearity on P/D. `selectorHomEquiv` and `endomorphismRingEquiv` are the reusable classification interfaces. `diagonalSlope_unique` requires infinite target support. `inverseDiagonal_admissible` requires infinite source support and proves inverse preservation; it is not an extra hypothesis.

The pinned Mathlib has canonical additive completion objects and eta/density interfaces but not all of the convenient additive functor/lift API names tested in development. Use `completionHom` and its eta/uniqueness/composition theorems, rather than reintroducing nonexistent APIs or treating an arbitrary completion comparison as the extension of a supplied map.

## Runtime and reproduction

Run `scripts/verify.py` with `--kit` or `KOMOREBI_LEAN_KIT` and a fresh evidence directory. The five Library archives `Lean_Compact_01.zip` through `05.zip` restore the pinned runtime. Their concatenated archive hash is `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`. Original Library identifiers and recovery details remain in the v0.1.0 ledger. The runtime is not re-embedded in this source ZIP.

## Preservation and limits

The finalized PDF and original publication ZIP are unchanged. Historical documentation is retained in `docs/history/v0.3.0`; all earlier accepted evidence remains in its original directory. Development failures are preserved separately. The same-kernel replay and endpoint checks do not constitute an independent verifier, source rebuild of external caches, or external peer review. No Python extraction or historical-priority claim is made.
