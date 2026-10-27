# Verification Notes

## Projector-Resolved Seed Calculus X
### Universal Residual Seeds: Deformation Forests, Transport Categories, and System Completion

**Author:** Komorebi P.

## Build

- Final PDF: `Projector_Resolved_Seed_Calculus_X.pdf`
- Final page count: 26
- LaTeX engine: `latexmk` with `pdflatex`
- Undefined references: none
- Overfull boxes: none
- Underfull boxes: none reported
- Paper-local citations: none
- Paper-local bibliography: none
- Figures: 16 PNG and 16 vector-PDF files
- PNG ancillary metadata: removed
- Vector-PDF metadata: title, subject, and **Komorebi P.** only
- Main PDF metadata: title, subject, and **Komorebi P.** only
- PDF hyperlinks retained after metadata normalization: 28 annotations
- PDF outline retained after metadata normalization: 20 entries

## Automated tests

```text
28 passed
```

The test suite verifies:

- residual partitions and positive-depth no-crossing;
- compatible residue towers and digit reconstruction;
- delayed dyadic sign separation;
- smooth, weighted, and singular seed counts;
- rational seed-zeta expressions;
- exact singular branching dimension;
- directed strongly connected components and minimum seed count;
- exhaustive confirmation of the directed seed theorem in the finite model;
- modular cohomology dimensions and packet reconstruction;
- finite companion forests and branch extraction;
- common-spine compatibility and inconsistency detection;
- finite Frobenius separation and carrier multiplicity recovery;
- exact joint occupancy projectors and trace/rank identities;
- generation of all figures, tables, and machine-readable results.

## Finite certificates

| Certificate | Result |
|---|---:|
| residual packet count | `3` |
| compatible inverse-limit branch | `true` |
| first dyadic sign-separation depth | `2` |
| source strongly connected components | `3` |
| brute-force minimum directed seed count | `3` |
| cohomology packet reconstruction residual | `0` |
| common Frobenius spine | `compatible` |
| inconsistent spine detected | `true` |
| recovered carrier multiplicities | `(2, 0, 1)` |
| successive finite occupancy ranks | `(3, 2, 1, 0)` |

For the companion equation `x^2 + 1 = 0`, exact forests were generated through depth five at coefficient primes `2, 3, 5, 7, 13`. The primes `5` and `13` have two compatible branches at every tested level. The prime `2` has one residual root that dies at depth two, while `3` and `7` have empty residual levels.

## Wheel

- Wheel: `projector_seed_residuals-1.0.0-py3-none-any.whl`
- Build method: PEP 517 wheel build without dependency isolation
- Clean target installation: passed
- Import test: passed
- Installed model checks: residual partition `{0:[0,3,6],1:[1,4,7],2:[2,5,8]}`, singular counts `(1,3,3,9,9,27)`, and directed seed representatives `('G','D','A')`

## Render audit

All 26 pages were rendered at 160 DPI. `Verification_Render.png` contains the complete page contact sheet. `Figure_Contact_Sheet.png` contains all 16 generated figures. The rendered pages were checked for clipped text, overlaps, missing glyphs, broken tables, and misplaced legends.

## Metadata audit

The compiled PDF was cloned with its pages, annotations, named navigation, and outline intact while replacing its document-information dictionary. A page-by-page render comparison before and after metadata normalization reported zero changed pages. Creator, producer, date, custom metadata, and XMP metadata are absent from the final PDF.

## Claim control

The paper distinguishes:

- proved formal and finite theorems;
- imported deformation-theoretic and compatible-system background;
- exact finite numerical certificates;
- conditional completion criteria;
- unresolved universal companion and automorphic occupancy statements.

The work does not claim that every geometric representation enters a compatible system, that every compatible system is automorphic, or that unrestricted reciprocity has been proved.

## Archive verification

- Complete release archive extraction: passed
- Complete release tests after extraction: `28 passed`
- Source-focused archive extraction: passed
- Source-focused tests after extraction: `28 passed`
- Source-focused LaTeX recompilation: 26 pages
- Undefined references and layout warnings after source recompilation: none
- Deterministic archive timestamps: normalized to the ZIP epoch
