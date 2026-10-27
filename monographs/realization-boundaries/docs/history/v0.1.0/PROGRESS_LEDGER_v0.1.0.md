# Progress ledger — Realization Boundaries Lean v0.1.0

## Authoritative inputs

- Publication: `publication/Realization_Boundaries_Final.pdf`.
- Original editable release: `provenance/Realization_Boundaries_Final_Package.zip`.
- Formal source: nine modules under `RealizationBoundaries/` and their import entrypoint.
- Accepted receipt: `verification/accepted/run.json`, status PASS.
- Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
- Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06; all nine locked packages checked.

## Completed in this tranche

The actual prime product, finite-support subgroup, torsion equivalence, quotient unique division, derived rational module, admissible preimages, exact root criterion, canonical coordinate quotients and transitions, finite-target kernel containment, rational quotient and nonsplitting, explicit section, finite cocycle, unique normal forms, twisted normal-form additive group, its additive realization equivalence, and paired-prime marked root tests.

There are 90 explicit production theorem/lemma declarations and 232 audited project declarations including generated helpers. All nine modules and the entrypoint compile. All nine modules pass project-only kernel replay. Eleven positive contract proofs and ten intended rejection controls pass. No additional axiom or proof placeholder is accepted.

## Not yet completed

Use `docs/MONOGRAPH_COVERAGE.json` rather than a percentage. In particular:

- The quotient and kernel calculations do not yet constitute the full profinite-completion theorem.
- The direction from an arbitrary pure intermediate subgroup back to a rational subspace remains.
- Countability of D and the resulting preimages, complete root-fiber counts, and the CRT cyclic-group identification remain.
- No complete unmarked classification, all-homomorphism/endomorphism theorem, seed-rank theorem, oracle-degree theorem, or grammar escape theorem is represented as checked.
- The explicit finite Python certificate procedure has not been verified by Lean extraction.

## Next restart point

Preserve the accepted sources and evidence. First close the remaining ambient foundations: countability of the finite-support subgroup and the reverse pure-preimage correspondence. Then formalize the product topology, density, finite-index-kernel cofinality, and the actual profinite completion. The key inputs `integerQuotientEquiv`, `coordinateRestriction_map`, `finite_target_coordinate_kernel`, and `nonzero_coordinate` are ready.

After the completion layer, prove the tail signature and unmarked classification, deriving diagonality of arbitrary homomorphisms from the concrete coordinate quotients rather than assuming it. The computability theorem must have its own oracle and presentation semantics and retain the distinction between uniform marked decoding and nonuniform unmarked decoding.

## Reusable runtime recovery

The kit used here can be recovered from the Library's five `Lean_Compact_01.zip` through `Lean_Compact_05.zip` files. Their archive-member chunks concatenate to an XZ-compressed tar archive with observed SHA-256 `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`. The extracted directory is `Komorebi_Portable_Lean_4.34.0-rc2`. The toolchain and cache are large and are not embedded again in this small companion.

Original Library file identifiers, retained for restart continuity:

| Part | File identifier |
|---|---|
| 01 | file_00000000211881f590f83a9f9114f14a |
| 02 | file_00000000fe5081f58c57aeaedb580fbe |
| 03 | file_00000000e49481f5a027206c8809ea97 |
| 04 | file_000000009e2081f59a298bc4f40f58db |
| 05 | file_00000000380081f595a22a760c9ccffb |

These identifiers are retrieval metadata, not filesystem paths. Materialize Library files before using their bytes in a new runtime. Do not infer a sandbox path from the filename alone.

## Provenance and limits

Development failures remain preserved and are not counted as successful runs. The final book was not overwritten. Kernel replay uses the same trusted Lean implementation and imported caches; it is not independent external verification. The open license covers the new Lean source and verification tooling.
