# Paper XI — release scope 1.1.0

18 October 2026 · Komorebi P. · Checkpoint `P11-RELEASE-1.1.0`

This is the revised publication and verification edition of **Tame and Wild Packet Geometry for Local Langlands**. Its publication scope is the main monograph, core visual guide, Lean guide, preserved research progress paper and conjecture atlas, together with their available sources, exact changes, reproducible verification tools and historical evidence. The paper's universal arithmetic endpoint remains **Conjecture 66**.

## Claims and their evidence

| Claim class | What this release establishes or preserves | Evidence and boundary |
|---|---|---|
| Finite mathematics | The finite packet theory and its stated conditional interfaces, with the explicit local corrections in this edition. | Main manuscript; `CHANGES_v1.1.0.md`; focused proof-review receipts and complete publication source diff under `evidence/release_1_1/`. This is an internal review, not an external referee's certification. |
| Restricted arithmetic constructions | The written odd and dyadic constructions, low-rank carrier arguments, conductors, occurrence obstructions and marking distinctions under their stated classical inputs. | All fifteen construction appendices; research Parts I–III; preserved component audits in the historical archive. A source-defined representation, a supplied type and a factor-matching candidate must remain the same objects wherever the statement requires it. |
| Source compilation | The catalogue-selected 423 modules and two separately identified additional targets, under the pinned Lean and Mathlib environment. | `verification/lean/RELEASE_VERIFICATION.json` gives the actual compilation lineage and outcomes. Compilation checks the formal declarations at their stated hypotheses. The PDF builder does not invoke Lean. |
| Axiom dependencies | Resolution of all 4,342 catalogue names, and a broader audit of all logical declarations owned by the selected modules, including private and generated declarations. | Declaration-level results under `verification/lean/`. The allowed transitive axioms are `Classical.choice`, `Quot.sound` and `propext`. Compiler-only auxiliary names are recorded separately. Name counts are not mathematical discovery counts. |
| One-candidate comparison | Equality of a supplied admissible candidate and reference in the declared isomorphism quotient, from equality of their profiles in a separating factor system. | `PaperXI.SingleCandidateComparison.source`; the complete supplement in the Lean guide. Neither arithmetic existence nor H5 is constructed by this implication. |
| Recovered terminal | The actual-monomial target with its original source retained and separately reviewed compatibility and local proof repairs. | Separate terminal compilation and axiom receipts, original and failed intermediate sources, exact repair diffs and hypothesis review. This is a restricted tame Weil-side attachment, not a universal wild automorphic construction. |
| Bounded computation | Six selected inherited suites, freshly replayed with 117 methods. | `verification/baseline_replay/`. Their original bounds remain in force. The replay is not the separate historical seven-program arithmetic run or a universal realization proof. |
| External-source checking | A selected full-text Henniart–Lemaire interface check, plus documented bibliography metadata reviews. | Dated source-review reports identify exact locators, hypotheses, source hashes and access limits. Bibliographic identity checking does not certify a theorem's application. |
| Publication verification | Matched source/PDF fingerprints, inspected page layouts, resolved local PDF navigation and exact package contents. | `BUILD_RECORD.json`, `VISUAL_REVIEW.json`, the root manifest and the separate final delivery-verification receipt. These checks do not strengthen the mathematical hypotheses. |

## The arithmetic endpoint

Conjecture 66 asks for an actual common arithmetic realization for every admitted H1–H4 datum. The retained conjecture includes the prescribed actions, the character values included in the supplied datum, finite attachments, phases, transports and recovery. An abstract finite model or a structure with an existence field does not furnish that realization.

The surviving comparison proposition is conditional: once an actual admissible candidate exists and satisfies the full characterizing local-factor condition H5, the stated characterization theorem identifies that candidate. The same candidate must occur in both steps. Equal dimensions, conductors, selected profiles or one selected local-factor test do not establish full H5.

The ledger therefore keeps four distinct open tasks:

1. `P11-OPEN-016`: general arithmetic realization with the admitted stabilizers and transports.
2. `P11-OPEN-017`: full H5 for that same realized candidate.
3. `P11-OPEN-021`: corrected full-character occurrence in the fixed Continuation113 automorphic-induction candidate, including its required noncompact extension.
4. `P11-OPEN-022`: actual native square/section data and honest phase certificates when the stronger fixed-native contract is required.

The fourth task does not erase the separate positive construction for transported scalar-pushout markings. The fixed-native and transported-marking contracts have different inputs. No mathematical completion percentage is assigned.

## Preservation and edit boundaries

The active three readers have editable sources in `publication/source/`. The original 423 selected Lean files and forty teaching excerpts retain their source identities. The terminal and supplementary comparison module are separately counted. The main manuscript has 68 proof environments: 65 bodies are byte-identical to v1.0.0, and three bodies were revised. That comparison is about this exact source population, not every historical proof file.

The 77-page research progress paper retains version 0.4.0; the 36-page atlas retains version 0.5.0. Their mathematical text, links and page structure are preserved. The common decorative branch was removed from five embedded covers by a narrowly checked path-paint edit. Their original PDF binaries are retained inside the historical archive. This presentation cleanup is not a unified research-paper source rebuild.

The complete recovered v1.0.0 source-and-evidence archive is included under `historical/`, with a searchable index preserving every original path. The complete Block 2 editable archive remains unavailable. Its original 33-page reader component survives in the cumulative research PDF; missing source is not reconstructed from later claims.

## Reading historical statements

Earlier receipts remain dated records of what their authors checked then. An old statement that Lean was not run, that a terminal receipt was missing, or that a particular source could not be retrieved retains its historical meaning. Current receipts describe this release's additional work. They do not overwrite an old failed run, manufacture an absent historical receipt, or certify every earlier checkpoint.

Fresh Lean compilation, a transitive axiom audit, an additional same-kernel replay, an independent checker, ordinary mathematical proof and external peer review are separate evidence types. This release records the first two in their executed scopes. It does not claim an independently implemented checker, a fresh additional full `leanchecker` pass, a rebuild of all Mathlib, or external peer review.
