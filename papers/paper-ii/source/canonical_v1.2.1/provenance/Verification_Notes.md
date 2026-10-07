# Verification Notes

## Deliverable

**Projector-Resolved Seed Calculus II: Polyphase Refinement, Weighted Transfer,
and Dyadic-Odd Resolution**  
Author: **Komorebi P.**  
Paper/Python version: **1.2.1**  
Lean component version: **1.1.1**

## Contract and boundaries

The frozen completion denominator is 25: 21 numbered main-text items, one
Smith-phase identity, and three algorithms. The exact declaration map is in
`formalization/lean/LEAN_THEOREM_MAP_v1.1.1.md`. Certificate-taking results
verify their supplied hypotheses. The finite-graph zeta denominator is now
constructed automatically by determinant/adjugate algebra, and diagonal Smith
congruences over `ZMod (p^L)` are proved directly. The counted Smith theorem is
this concrete result with residue cardinality `p`; its arbitrary-DVR analogue
with residue cardinality `q` is certificate-explicit. The release still does not
claim a general polynomial-resultant constructor, Smith-normal-form
construction, spectral inverse existence, or unrestricted convergence.

Lean completeness is relative to this contract. It is not external
certification, novelty review, or bibliographic priority review.

## Verified release facts

- PDF: 31-page manuscript source, generated figures, a local bibliography, and
  a release PDF built from the same tree and inspected through a full contact sheet.
- Python: version 1.2.1 package, 48 passing tests, exact JSON/CSV consistency checks, and
  an isolated wheel smoke-test path.
- Lean: eight substantive Paper II theorem modules plus aggregate and
  fail-closed kernel-audit modules; the theorem-map checker resolves 160 unique
  compiled declarations across the frozen 25-row map, and the fail-closed scan
  accepts all 1,034 compiled `Komorebi.*` declarations.
- Formal strengthening: coordinate coherence/naturality, periodic finite-table
  Fourier, explicit pruned weighted inverses, automatic finite-graph
  transfer-zeta rationality, direct wrappers for four composite rows, a proved
  ceiling cutoff, minimal and unit-aware separation, concrete
  `ZMod` Smith counts, local resultant/weight endpoints, and polynomial,
  power-majorant, and resolvent-norm defect theorems.
- Clean archive acceptance requires checksum verification, Python tests and
  wheel smoke testing, the Lean aggregate plus standalone theorem-map and
  kernel-audit checks, and a clean LaTeX build. Exact command outputs and
  artifact hashes are recorded in `results/` for the packaged release.
- Baseline lineage: SHA-256
  `44c22768c4bc6d5fbf443fff62076fc216921844dcebcb80a15243a4bcd1abfa`.

The captured build, source-audit, test, wheel-smoke, and LaTeX outputs are in
`results/`. The full-document render contact sheet is
`provenance/Verification_Render.png`.

## PDF metadata

The PDF identifies the title, author, and subject. Standard pdfTeX/hyperref
creator, producer, and build-date fields remain. No private local path or
unrelated author is intentionally embedded in the release.

## Remaining external work

Independent mathematical review, literature/priority review, venue selection,
and any submission-specific formatting remain outside this internal release.
