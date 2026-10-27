# Paper XI — complete revised release 1.1.0

## Tame and Wild Packet Geometry for Local Langlands

**Komorebi P. · Operation Komorebi · 18 October 2026**

This package completes the revised publication and verification work for Paper XI. It includes five readers totaling **516 pages**, their available editable sources, the portable formalization project, current verification evidence, the full recovered predecessor archive and a versioned research ledger. **Conjecture 66 remains open.** The exact surviving arithmetic tasks are stated below and in the paper.

## Start reading

| Reader | PDF pages | Purpose |
|---|---:|---|
| [Main monograph](publication/pdfs/Paper_XI_Traditional_v1.1.0.pdf) | 111 | Finite theory, restricted arithmetic results, fifteen construction appendices and references. |
| [Core visual guide](publication/pdfs/Paper_XI_Visual_Guide_v1.1.0.pdf) | 53 | Diagrams, examples, conventions and the boundary of the comparison. |
| [Lean guide](publication/pdfs/Paper_XI_Lean_Guide_v1.1.0.pdf) | 239 | Fresh verification, the supplementary implication, forty excerpts and the full selected source catalogue. |
| [Research progress paper](publication/pdfs/Paper_XI_Conjecture66_Progress_v0.4.0.pdf) | 77 | Preserved Parts I–III: constructions, occurrence obstructions, conductors and marking contracts. |
| [Conjecture atlas](publication/pdfs/Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf) | 36 | Thirty-two worked plates and the explicit remaining obligations. |

Start with the main monograph. Its reading guide distinguishes the finite results, restricted arithmetic constructions and remaining general realization. Keep all five PDFs together with these filenames so their companion links work. `READING_CONCORDANCE.md` provides the exact route map. The research companions retain their historical mathematical version labels; this edition removes only the matching cover ornament from those files.

## What changed

The moving-phase statement now uses the correct moving spaces and explicit symplectic action. The twisted-algebra proof uses direct averaging. The pairing convention, carrier-versus-orbit distinction, scalar-holonomy assumptions, rank-one tame conductor and trivial-character Gauss-sum exception are explicit. Appendix notation and transition bounds are repaired. The bibliography, navigation and covers are revised. `CHANGES_v1.1.0.md` explains each change; `evidence/release_1_1/PUBLICATION_SOURCE.diff` records every active-source edit.

The main source contains 68 proof environments, with 65 byte-identical proof bodies and 3 revised bodies compared with v1.0.0. The 423 selected Lean modules and 40 inherited teaching excerpts are unchanged. The additional one-candidate comparison is printed in full in the Lean guide and counted separately.

## Formal verification

| Population | Modules | Catalogue names resolved | Owned logical declarations audited | Result |
|---|---:|---:|---:|---|
| Selected publication sources | 423 | 4,342 | 7,672 | PASS |
| Recovered terminal | 1 | 0 | 51 | PASS |
| One-candidate supplement | 1 | 1 | 1 | PASS |

All targets were freshly compiled in this release session using Lean 4.34.0-rc2 and the pinned Mathlib/dependency revisions. The continuations reused only authenticated successful objects from this session; no historical Paper XI objects were used. The first resource-planning stop, terminal diagnostic failure and two memory-limit kills remain recorded. Bounded diagnostics isolated an expensive conversion in the terminal proof. The separately reviewed local proof repairs passed the final compilation. All three aggregate imports and both axiom-audit negative controls passed. Only `Classical.choice`, `Quot.sound` and `propext` are allowed transitive axioms. Actual declaration-level results are in `verification/lean/RELEASE_VERIFICATION.md` and its companion JSON.

These checks establish the formal statements with their written hypotheses. The one-candidate lemma assumes the admissible candidate/reference and equal factor profiles; it supplies no arithmetic existence result. External Mathlib cache objects were imported, not rebuilt. No independent checker or fresh additional full `leanchecker` pass is claimed.

## Other completed checks

Six inherited replay suites passed 117 methods. The complete recovered predecessor passed its 3966-file manifest check. The selected Henniart–Lemaire interface was checked against the official full text. Bibliography provenance now covers the 29 active entries with explicit field-level access limits. All active reader pages received layout review, and source fingerprints, reference destinations, companion routes and package files have exact receipts.

## Remaining mathematics and source recovery

1. Construct the general actual arithmetic realization for all admitted H1–H4 data.
2. Prove the full characterizing H5 identities for that same candidate.
3. Prove corrected full-character occurrence in the fixed Continuation113 candidate and identify its required noncompact extension.
4. Compute the actual native square/section data and honest phases where the stronger fixed-native contract is prescribed.

The complete Block02 editable archive remains unrecovered. The original reader component is preserved in the cumulative research PDF. The original successful terminal receipt remains absent; this release supplies a separately dated successful replay after compatibility and local proof repairs. Its original and failed intermediate sources remain identifiable. `FAILURES_AND_LIMITATIONS.md` preserves these distinctions and the unsuccessful execution history.

## Files and reproduction

| Location | Contents |
|---|---|
| `publication/pdfs/` | The five final readers. |
| `publication/source/` | Editable active reader sources, vector figures, selected Lean catalogue and excerpts. |
| `formalization/` |425 separately scoped module sources, exact toolchain pins and portable bootstrap/replay/audit scripts. |
| `verification/` | Fresh formal, bounded replay, baseline integrity and reader-build records. |
| `evidence/release_1_1/` | Mathematical/source reviews, exact diff, navigation, cover and visual-review evidence. |
| `historical/` | Complete recovered v1.0.0 archive and searchable original-path index. |
| `ledger/` | Unchanged v1.0.0 and new v1.1.0 ledger snapshots. |
| `tools/` | Reader builder, release verifier, targeted cover edit and verifier control harness. |

Read `BUILD.md` for exact commands, `RELEASE_SCOPE.md` for the claim contract and `CONTINUE_HERE.md` for the next mathematical step. The root `MANIFEST.json` fingerprints every other packaged file. The final delivery-verification receipt is supplied outside the ZIP so it can identify and verify the exact archive without a circular self-hash. Preserve the release and append a new dated checkpoint for subsequent work.
