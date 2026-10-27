# Komorebi Stratified Universality - Block 03 Validation Record

**Version:** 1.3.0 Block 03  
**Date:** 29 August 2026

## Exact mathematical implementation checks

The bundled verifier `verify_block03_periodic_atlas.py` completed successfully.

| Item | Result |
|---|---:|
| Primitive unit-periodic words | 583 |
| Prime fields | `F_2`, `F_3` |
| Maximum periods | 8 over `F_2`, 6 over `F_3` |
| Exact checks | 39,805 |
| Failures | 0 |

The verifier uses exact prime-field and polynomial arithmetic. It checks:

- Berlekamp-Massey recovery of the minimal recurrence
- recurrence divisibility by `x^T-1`
- reduced-denominator divisibility by `1-z^T`
- recovery of the least period from both normalized linear charts
- exact rational functional-Mahler identities
- the finite p-kernel pair model and digit transitions
- the multiplier-orbit cardinality formula
- minimal digital automaton outputs
- the Cartier compiler state bound

The computation validates the implementation and examples. It is not substituted for the symbolic proofs in the manuscript.

## LaTeX build checks

- compiler: `latexmk` with `pdflatex`
- result: successful
- pages: 80
- page size: US letter, 612 by 792 points
- PDF outline entries: 75
- unresolved references: 0
- undefined control sequences: 0
- overfull boxes: 0
- underfull boxes: 0
- fonts: embedded

## PDF preflight

- encrypted: no
- openable by PyMuPDF: yes
- likely scanned: no
- XFA: no
- forms: none
- attachments: none

## Visual inspection

All 80 pages were rendered at 170 DPI and inspected through nine contact sheets. The four new figures were also inspected at source resolution. The landscape bridge-passport table was inspected at full-page resolution. No clipped text, overlapping content, broken glyphs, black squares, or truncated table columns were found.

## Clean extraction rebuild

A clean source copy was rebuilt after regenerating:

1. the exact periodic-atlas validation data
2. all figures
3. all generated LaTeX tables
4. the final PDF

The clean rebuild produced 80 pages with the same warning-free LaTeX log. A 100-DPI pixel comparison reported:

- pages in packaged build: 80
- pages in clean rebuild: 80
- changed pages: 0

The PDF byte streams are not claimed to be identical because TeX metadata contains build times. The rendered mathematical content and layout are identical page by page.

## Claim boundary

The validation establishes package integrity and exact agreement on the declared finite ranges. It does not constitute independent peer review, historical priority verification, or evidence for the unrestricted eight-stratum effective-descent program.
