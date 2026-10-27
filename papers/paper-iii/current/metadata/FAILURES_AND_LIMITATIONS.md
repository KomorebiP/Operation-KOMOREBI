# Failures, repairs and remaining limits

This record distinguishes observed failures from outstanding work. The earlier candidate record is retained at `../provenance/rc1_release/metadata/FAILURES_AND_LIMITATIONS.md`.

## Resolved in the final release

| Observed issue | Resolution and evidence |
|---|---|
| Exact Lean compiler unavailable in the recovered bundle | Restored the official pinned release, verified its SHA-256 and commit, restored all nine dependency revisions, and ran a cold owned-source build. Compiler/dependency provenance is under `formal/verification/`. |
| Sandbox network, executable-location and ownership-restoration errors | Used approved scoped network/execution access and extraction without ownership changes. Failures and successful commands are recorded in compiler provenance. |
| Two uncompiled Section 17 candidate modules | Both compiled. They are imported into the final production root and included in its four passing phases. |
| Actual Banach-space range interface missing from the candidate formalization | Added and independently reviewed `ContinuousPacketJets.lean` on actual submodule ranges with inherited norms. |
| Higher composition and support had no project formal bridge | Added and independently reviewed `PacketJetComposition.lean`, including every original slot, every intermediate label and the one-way support implication. |
| Deprecated Lean names and explicit coercion elaboration | Updated exact API spellings and made the continuous/algebraic coercions explicit. Original failed attempts are preserved. No theorem statement was weakened. |
| An axiom control expected the audit to encounter an axiom before its consumer | Kept the auditor unchanged and corrected the expected rejection marker to accept either valid ownership rejection order. The final control run passes. |
| Second-order composite displayed the wrong output-family symbol | Changed it to the projector acting on the composite codomain. |
| Structural support sets mixed external profiles and decorated witnesses | Defined admissible witnesses and projected them to the same external profile type. |
| First integration of the partition induction referred imprecisely to a singleton | Independent review caught it. The proof now removes exactly the new singleton, or removes the new element from its containing block. |
| Missing local copies of the original TeX font files | Used the same installed font families and rebuilt the reading files. No missing-character result is accepted. |
| RC1 manifest verification was attempted while new working files were being added | Verified every original manifest entry directly against the original archive. The final archive receives a new complete manifest after source freeze and is checked after clean extraction. |
| Initial register gate used 26 as the number of canonical rows with any Paper III target | The exact map contains 26 Paper-III-only rows, three inherited-only rows and one mixed row. The gate now preserves the mixed row and all exact target names. |
| Initial reader assembly omitted TeX named links | Resolved each component’s named destinations explicitly before merging, converted PDF coordinates, and checked all 357 links and component page renderings. |
| A floating figure interrupted the norm proposition | Added a typesetting-only page break after the figure. Removing that one line exactly reproduces the audited Section 17 hash. |
| New Lean-guide scope row omitted pairwise annihilation | Added the hypothesis to match the actual projector-system assumptions. |

## Present limits

The Taylor integral bridge, Stirling term count, additional norm corollaries and matched expanded Lean proofs for Sections 18–27 remain future formal work. Their ordinary mathematical proofs and reviewed scope are supplied. Inherited Papers I–II references were not independently recompiled.

The historical October 16 visual claim of 2,693 declarations and full 98+2 formal coverage has no matched source in the recovered release. It is neither certified nor silently replaced with an invented proof inventory. It remains available as historical material.

Exact computation is bounded evidence. The three main suites include repetitions. Their 80 newer range-norm assertions sample rational vectors for one matrix; they do not compute an exact operator norm. The general range-norm theorem is supported separately by its proof and Lean declaration.

The copyright holder has not selected a project-wide public reuse license. The technical release is final under its declared scope; public licensing and publication remain separate author decisions.

Mathematical reviews in this package are assistant audits at recorded revisions, not external peer review or a guarantee against every possible error. The release exposes source, hypotheses and receipts so its conclusions can be independently checked.
