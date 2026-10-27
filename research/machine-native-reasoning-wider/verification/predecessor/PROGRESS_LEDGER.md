# Machine-Native Reasoning — working publication ledger

This ledger is an editorial and reproducibility record, not part of the published mathematical argument. It is deliberately versioned and dated; the book's normal running prose is not an engineering log.

## Current delivery: first integrated working edition, 2026-10-22

**Publication:** 57-page continuous LaTeX/PDF working manuscript, titled *Machine-Native Reasoning: Representation, Inference, Discovery, and Self-Correction*. It contains the full nine-chapter reviewed mathematical core verbatim at the source-chapter level; an original mathematical prologue connecting the core to Komorebi Space; a carefully bounded finite theorem composing legal-action quotients and stochastic instruments; a complete expanded written proof of the safe-ending result, including history-dependent policy necessity; a three-state counterexample; and a mathematical research-boundary chapter. The authoritative target for the **final 30-chapter book remains incomplete**.

**Original reviewed core:** the 27 theorem/proposition/corollary statement/proof spans in `sources/core/src/core.tex` were preserved in `core_chapters.tex` by an exact source slice. The compiled book reflows them and adds other chapters. No claim is made of new independent mathematical peer review of all 27 proofs.

**Formal assurance:** Original Machine Theory Lean Block 15 archive SHA-256 `f9996165ed76c11589f39e27e6ded51608c8366e43c3f88c40aed225e6394ea2`, 1,442 original manifest entries, all verified by SHA-256 and byte length in the current session. Its two prior complete Lean gates support **23/27 selected source results** under the pinned historical trust boundary. No pinned Lean executable or Mathlib runtime is installed here; no fresh Lean compilation or kernel replay was run. New proof material in this edition is **written mathematical proof, not newly machine certified**.

**New Core 8.3 exact finite checker:** `formal/check_core83.py`: PASS, 2,304 exhaustive two-state cases, 4,000 seeded three-state cases, 2,000 seeded four-state cases, and two explicit boundary/counterexample cases. The fixed-point attractor/viability algorithms agree with separately enumerated positional-policy outcomes; all checked rank witnesses decrease. The source theorem is NOT promoted to Lean-certified status.

**Joint stochastic/legal quotient example:** `formal/check_joint_contract.py`: PASS; 8-state fine system, 4-state quotient, 10 fibre-law/action contracts, exact rational history laws matching at horizons 0 to 4, plus exact marginal-only counterexample. The prose composition theorem is not a new Lean theorem.

**Reviewed-core finite checks rerun:** `verification/reproduced_core/code/check_core.py`: PASS, 21 groups and 115,762 assertions. `code/check_admissions.py`: PASS, 6 groups and 89,715 assertions. Combined 27 groups and 205,477 finite assertions. Original reviewed-core archive 130-file integrity check passed before replay. These are same-project reference checks and do not certify general theorems.

**PDF:** pdfLaTeX multi-pass build succeeds; 57 pages; all 57 pages rendered for review; no text blocks outside page bounds; no unresolved references or overfull-box warnings in final build. Vector figures are Python/matplotlib outputs of exact declared models. First draft compilation initially failed with undefined `lemma` theorem environment; the environment was defined and the retry passed. A 55 pt overfull cover line and duplicate preliminary-page anchor were then corrected; final build has neither issue.

## Remaining obligations, classified

### Core formal correspondence
1. 8.3 sure-ending and safe-running fixed points, positional strategy, history-dependent necessity, rank bounds. **Written and finite tested; Lean pending**.
2. 2.4 common observable quotient and switching candidates. **Lean pending**.
3. 2.5 cone-preserving packet mixtures, zero weights, nonnegative idempotent classification. **Lean pending**.
4. 3.2 partition correction-memory occupancy and exact `2^r` cardinality. **Lean pending**.

### Main book mathematical content
5. Complete the full thirty-chapter manuscript by admitting selected proofs from other original sources individually. This working edition has twelve numbered chapters plus an unnumbered realization prologue, not thirty.
6. Audit the new stochastic/legal interface theorem independently, including effect of policy access and action availability when support changes.
7. Develop evidence-preserving model-revision composition contracts; do not assert a learned translator or a verified action dispatcher until their respective interfaces are proved.
8. Produce a complete cross-paper theorem correspondence, bibliography, author index and larger visual atlas while avoiding duplicate proof credit.

### Publication and archival work
9. Consolidate the full specialist source catalog; repair editable-source gaps where available, especially the latest Large Signal Model source-package lineage.
10. Run final manuscript proofread, cross-reference audit, mathematical literature/priority review, figure verification, reproducible builds and complete single-ZIP distribution checks.
11. Preserve MIT / CC BY 4.0 original-material policy with relevant third-party source and font exceptions. No standalone font files are distributed.
12. Any user-hosted GitHub release, hosted CI, native Windows replay or external peer review is separate and not yet claimed here.

## Exact next restart

First, resume from the frozen Lean Block 15 complete ZIP, verify the existing SHA-256 manifest and pinned toolchain, and port the source theorem `r:ending` (Core 8.3, `source/core_v0.2.tex` lines 903–927). The independent mathematical proof is in `ending_chapter.tex` and the model checker is `formal/check_core83.py`. Prove the rank and fixed-point lemmas before the one-policy equivalence, then add negative controls, compile in fresh directories, audit transitive axioms, replay objects in the pinned kernel, and update the exact theorem map. Retain 2.4, 2.5 and 3.2 as pending until independently admitted. The newer joint interface theorem is a separate future Lean target.
