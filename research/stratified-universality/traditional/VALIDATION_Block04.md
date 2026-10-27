# Komorebi Stratified Universality - Block 04 Validation Record

**Version:** 1.4.0 Block 04  
**Date:** 29 August 2026  
**Artifact:** `Komorebi_Stratified_Universality_Foundations_v1.4.0_Block04.pdf`

## Exact mathematical verification

### Block 03 regression verifier

- semantic cases: 583 primitive unit-periodic words
- exact checks: 39,805
- failures: 0
- status: PASS

### Block 04 rational-mask verifier

- reduced normalized masks: 125
- prime fields: `F_2`, `F_3`, `F_5`
- collapse masks: 51
- noncollapse masks: 74
- exact checks: 11,391
- failures: 0
- status: PASS

### Combined exact regression total

- exact checks: 51,196
- failures: 0

All verifier arithmetic is exact. The scripts use finite-field coefficient arithmetic, polynomial reduction, formal-series recursion, Cartier transitions, reachable-state enumeration, linear-span rank, and exact behavioral distinguishability. The finite ranges support the implementation and named examples. They do not replace the unbounded proofs.

## LaTeX build audit

- compiler: `latexmk` with `pdflatex`
- result: PASS
- pages: 93
- page size: US Letter, 612 by 792 points
- PDF outline entries: 85
- unresolved references: 0
- undefined control sequences: 0
- overfull boxes: 0
- underfull boxes: 0
- LaTeX or package warnings affecting the manuscript: 0

## PDF preflight

- openable with PyMuPDF: yes
- encrypted: no
- likely scanned: no
- XFA: absent
- embedded fonts: yes
- forms or JavaScript: none

`qpdf` was not installed in the build environment, so no `qpdf --check` result is claimed.

## Visual inspection

- all 93 pages rendered
- eight contact sheets generated and included under `render_checks/`
- title page, abstract, table of contents, landscape registries, theorem pages, generated tables, four new figures, conclusion, concordance, edition ledger, and bibliography inspected
- no clipped text, overlapping blocks, broken glyphs, blank terminal pages, or malformed figures found

The principal Block 04 pages were additionally inspected at full resolution, including the rational-collapse theorem, reachable Cartier-core theorem, bridge-passport table, rational-mask atlas figure, exact examples table, automata figure, validation table, and final result box.

## Clean-extraction replay

A clean archive copy was extracted to a separate directory. The replay performed:

1. Block 03 exact verifier
2. Block 04 exact verifier
3. figure regeneration
4. generated-LaTeX regeneration
5. clean `latexmk` compilation

Replay result:

- pages: 93
- build warnings listed above: 0
- render comparison at 96 dpi: 93 of 93 pages pixel-identical
- byte identity of the two PDF containers: not claimed, because PDF metadata contains build timestamps

## Source-package integrity

- source files represented in `MANIFEST.sha256`: 83
- manifest excludes only the manifest file itself
- the final source archive contains the manuscript, compiled PDF, exact verifiers, generated JSON and LaTeX, source and rendered figures, contact sheets, build script, progress notes, change ledgers, and validation records

## Claim boundary

This validation establishes internal reproducibility, exact finite agreement on the recorded ranges, clean compilation, and render stability. It is not peer review, external mathematical validation, a proof that every automatic sequence has a rational canonical mask, or evidence for the unrestricted eight-stratum universality claim.
