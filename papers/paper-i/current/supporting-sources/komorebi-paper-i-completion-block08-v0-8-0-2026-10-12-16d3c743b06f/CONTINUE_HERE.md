# Continue from Paper I Block 08

## Accepted checkpoint and source layout

Read `VERIFICATION.json` and its hashed accepted-run receipt first. Do not infer PASS from this guide alone.

- `source/extension/PaperICompletion8/DivisionRows.lean`: genuine left row-span/generation equivalence and the m ≤ rd generator criterion over division rings.
- `DivisionBlock.lean`: identification with the original canonical cardinal and natural seed ranks.
- `DivisionProduct.lean`: dependent division-ring factors and the maximum ceiling formula.
- `RegularMultiplicity.lean`: actual natural modules, simplicity, columns, finite direct sums and regular multiplicities.
- `SemisimpleFormula.lean`: any-presentation formulas, classical decomposition integration, literal module-top reduction and exact split wrappers.
- `ProductPresentation.lean`: compatible natural-factor decompositions constructed from simple summands and nonzero column projections.
- `SemisimpleExistence.lean`: certificate-free semisimple, Artinian radical-top and finite-dimensional-algebra existence/formulas.
- `source/extension/PaperICompletion8.lean`: import-only current root, retaining `PaperICompletion7`.
- `source/current/`: byte-identical flat copy of every one of the 54 accepted production sources.
- `predecessor/`: complete unchanged Block 07 package and earlier lineage.

The following work is established and must not be repeated as an open obligation: primary decomposition/count, intrinsic primary quotient and exact kernel, general geometric formula, scalar extension, the six-way cyclic criterion, noncommutative module-top/Nakayama, local residue division ring, and the nonsplit semisimple formula with actual compatible decompositions.

## Next mathematical block

Proceed to algebraic exact-sequence generator bounds and actual packet restriction/quotient descent. The current publication records are:

    PSC-I-T-EXACT-SEQUENCE-BOUNDS
    PSC-I-T-QUOTIENT-PACKET-DESCENT
    PSC-I-T-PACKET-EXACT-SEQUENCE
    PSC-I-C-QUOTIENT-PACKET-DESCENT

They remain partial or not mapped after Block 08. The following is a proof plan, not verified new work.

### 1. Finish the actual short-exact-sequence rank bounds

For an actual short exact sequence L → M → N of left modules over A, prove

    seedRank_A(N) ≤ seedRank_A(M) ≤ seedRank_A(L) + seedRank_A(N).

The quotient inequality is already supplied by `Komorebi.SeedRankOperations.seedRank_le_of_surjective_semilinear`. For the upper bound, choose generating sets of minimal cardinality for L and N, lift the latter through the given surjection, and prove that their union with the image of the former spans M. Use the actual exactness equality to move the remaining error into the kernel. Do not replace exactness by a supplied generating family or a desired rank inequality. The printed algebraic statement is not restricted to finite-dimensional spaces.

Relevant current APIs include `exists_generating_set_card_eq_seedRank`, `seedRank_le_of_surjective_semilinear`, `seedRank_eq_of_bijective_semilinear` and `seedRank_prod_le_add`. Inspect their actual types and universe constraints before use.

### 2. Construct quotient projectors from invariance

Use the actual `Komorebi.Foundation.LinearProjectorFamily` from `KomorebiVerification/ProjectorCore.lean`. It records the actual maps `proj`, idempotence, pairwise annihilation and finite completeness. Do not introduce a new family with the desired identities as unexplained inputs.

Given an invariant submodule K, define the restrictions of P_i to K and the actual induced maps on X/K. Use the appropriate pinned submodule quotient-map API or explicit quotient lifts. Prove behavior on representatives

    Pbar_i (x + K) = P_i x + K

and the literal intertwining identity with the quotient map. Derive idempotence, pairwise annihilation and sum-to-identity from the original family and surjectivity of the quotient map.

The Lean family currently allows zero projectors. Intermediate constructions may retain all indices, but the printed packet-system statement removes zero packets. Make that finite subtype/reindexing step explicit rather than assuming all original packets remain nonzero after restriction or quotient.

### 3. Prove exact packet range and quotient identifications

For each i, identify the restriction packet with the actual intersection K ∩ range(P_i). Prove the kernel of the quotient map on range(P_i) is exactly that intersection, and its image is range(Pbar_i). Derive the quotient equivalences from the actual maps, not from matching dimensions:

    range(P_i) / (range(P_i) ∩ K) ≃ range(Pbar_i)
    range(Pbar_i) ≃ (range(P_i) + K) / K.

Take care with Lean's submodule-of-a-submodule types in these displayed formulas. The paper's notation suppresses those embeddings; the proof must not.

Then assemble the full short exact sequence from the packetwise sequences using the existing packet-coordinate equivalences. Do not mark the entire record complete after proving only the projector identities.

### 4. Restrict and descend actual transfer blocks

`Komorebi.Foundation.transferBlock` is defined by the literal composition Q_j ∘ T ∘ P_i. If T and every projector preserve K, show that each block preserves the corresponding restricted packets. Construct the quotient of T and prove the full block intertwining with the same quotient map. Do not supply an independent quotient operator or quotient family as a certificate.

## Boundaries to preserve

Begin with algebraic modules and finite projector systems. The topological packet exact-sequence statement needs separate closedness, boundedness and quotient-norm arguments. The countable unconditional packet theorem and its sequence-space completeness are still separate obligations. A finite algebraic split is not a Banach or unconditional convergence theorem.

Other remaining obligations include category/functor constructions, tensor and dual packets, support-pattern and source-component results, general locally convex completion and executable algorithms. Consult `coverage/COVERAGE_108.json`; do not infer that the new semisimple block closes them.

## Reproduce the accepted Block 08 audit

From Linux or WSL, Python 3 and the exact offline runtime:

    bash scripts/run_block08.sh /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 /absolute/path/to/new-output

The output directory must not already exist. Do not update the toolchain or dependency pins. The matching runtime and upstream cache are external prerequisites.

The accepted strategy freshly compiles eight additions and the new boundary suite, authenticates 46 predecessor source/object pairs, resolves all public/coverage names, audits complete source-module ownership, executes rejection controls and replays the entire logical closure from upstream-only imports. Keep exact replay/ownership name-set matching and the corrupt-proof control. The seven inherited partial runtime helpers are separately inventoried, not proof-replayed.

Papers II–XII remain outside this final audit sweep. Their historical evidence is retained, not revoked. Final process/source/object checks are recorded in `evidence/HANDOFF_POSTFLIGHT.json`.
