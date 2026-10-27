# Block 08 validation record

## Mathematical verifier

`verify_block08_local_polyphase.py` returned:

```text
BLOCK08_STATUS=PASS
BLOCK08_CHECKS=229743
BLOCK08_FAILURES=0
```

The verifier uses exact integer and modular arithmetic. It covers:

- the generating and alternating-sum definitions of the affine Mahler kernel
- finite support and triangular diagonals
- finite polynomial coefficient transport
- mixed-radix composition and Chinese-remainder diamonds
- strict nested branch addresses
- prime-power Frobenius sparsity and exact residual rank
- canonical packet decoders
- sharp integral and fixed-modulus packet minima
- branchwise valuation lower bounds
- scalar principal-unit amplification
- matrix Carmichael-Mahler and Fibonacci congruences
- a negative control for nonunique integral lifts of residue data

## Regression verifier totals

| Block | Result |
|---|---:|
| Block 03 | 39,805 checks, 0 failures |
| Block 04 | 11,391 checks, 0 failures |
| Block 05 | 89,055 checks, 0 failures |
| Block 06 | 697,958 checks, 0 failures |
| Block 07 | 595,964 checks, 0 failures |
| Block 08 | 229,743 checks, 0 failures |
| **Combined** | **1,663,916 checks, 0 failures** |

## PDF validation

- pages: 141
- page size: US letter, 612 by 792 points
- outline entries: 119
- fonts embedded: yes
- encrypted: no
- forms: none
- JavaScript: none
- XFA: none
- openable by PyMuPDF: yes
- likely scanned: no
- overfull boxes: 0
- underfull boxes: 0
- unresolved references: 0
- undefined control sequences: 0
- multiply defined labels: 0

## Visual review

All 141 pages were rendered with PDFium at 120 dpi. Twelve contact sheets were reviewed, along with full-size inspection of the new local-atlas, affine-channel, kernel-sparsity, precision-tree, two-Mahler-language, examples, and validation pages. No clipped text, broken glyphs, or overlapping blocks were found.

## Clean replay

- archive extraction: PASS
- all six verifier suites: PASS, 1,663,916 checks and 0 failures
- figure regeneration: PASS
- LaTeX rebuild: PASS, 141 pages and 0 warning lines
- rendered page comparison: 141 of 141 pages identical at 96 dpi
- source manifest: PASS, 151 entries

## Boundary

The validation certifies package integrity, exact bounded calculations, deterministic figure generation, and render reproducibility. It is not independent peer review and does not elevate the stated open local, mixed-radix, spectral-local, or global descent problems to theorem status.
