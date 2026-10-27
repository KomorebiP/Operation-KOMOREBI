# Block 09 validation record

## Mathematical verifier

`verify_block09_holonomic.py` returned:

```text
BLOCK09_STATUS=PASS
BLOCK09_CHECKS=174940
BLOCK09_FAILURES=0
BLOCK03_TO_BLOCK09_CUMULATIVE=1838856
```

The verifier uses exact rational and integer arithmetic. It covers:

- root-of-unity multisection reconstruction for binomial source series
- exact coefficient formulas for the marked packet family
- hypergeometric ratio recurrences
- nonintegral packet-order instances
- positive-integral rational collapse
- nonpositive-integral finite-support aliasing and zero packets
- rotated-orbit ranks
- alias and cancellation defects
- local exponent packets and monodromy eigenvalue ledgers
- consistency of the printed worked examples

The four exact verifier categories are:

| Category | Checks |
|---|---:|
| Nonintegral binomial packets | 110,880 |
| Positive-integral collapse | 27,720 |
| Nonpositive-integral aliasing | 11,492 |
| Root-filter and order ledger | 24,848 |
| **Block 09 total** | **174,940** |

## Regression verifier totals

| Block | Result |
|---|---:|
| Block 03 | 39,805 checks, 0 failures |
| Block 04 | 11,391 checks, 0 failures |
| Block 05 | 89,055 checks, 0 failures |
| Block 06 | 697,958 checks, 0 failures |
| Block 07 | 595,964 checks, 0 failures |
| Block 08 | 229,743 checks, 0 failures |
| Block 09 | 174,940 checks, 0 failures |
| **Combined** | **1,838,856 checks, 0 failures** |

## PDF validation

- pages: 156
- page size: US letter, 612 by 792 points
- outline entries: 130
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
- source files including manifest: 171
- internal manifest entries: 170

## Visual review

All 156 pages were rendered with PDFium. Thirteen contact sheets were inspected, and the new Block 09 pages were also reviewed individually. The inspection covered:

- the ordinary holonomic atlas diagram
- the root-filter and state-jump multisection pipeline
- the order-phase diagram
- the local exponent packet diagram
- the marked atlas theorem and worked-example tables
- all boundary and result boxes in the new section

No clipped text, overlapping objects, black squares, broken glyphs, or unreadable tables were found.

## Clean replay

A clean copy of the source package was used to:

1. verify the internal SHA-256 manifest
2. replay all Block 03 through Block 09 exact verifiers
3. regenerate every common and block-specific figure
4. regenerate the concordance and proof-obligation tables
5. compile the LaTeX manuscript through three `pdflatex` passes
6. render the rebuilt PDF with PDFium at 96 dpi
7. compare every rebuilt page with the packaged final PDF

Result:

```text
CLEAN_REPLAY=PASS
REBUILT_PAGES=156
PIXEL_IDENTICAL_PAGES=156
CHANGED_PAGES=0
LATEX_WARNING_LINES=0
```

The source package contains the exact machine-readable Block 09 record in `generated/block09_holonomic_validation.json`.

## Status boundary

The verifier certifies the implemented exact identities and finite parameter ranges. It does not replace the symbolic proofs, prove historical novelty, establish external peer review, or extend the marked binomial-Fuchsian minimality theorem to arbitrary D-finite multisections.
