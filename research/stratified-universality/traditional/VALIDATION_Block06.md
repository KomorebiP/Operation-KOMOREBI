# Block 06 validation record

## Mathematical verifier

Command:

```powershell
python .\verify_block06_integral_tower.py
```

Recorded result:

- Smith divisibility chains: 1,984
- chain-modulus cases: 45,632
- Fitting cases: 8,840
- prime-power profile cases: 39,680
- digit-equivariant Smith-square systems: 320
- bounded ghost-contraction samples: 1,681
- total exact checks: 697,958
- failures: 0
- status: PASS

The bounded verifier checks Smith kernels, cokernels, semantic image cardinalities, good-modulus criteria, Fitting generators, prime-power ghost and generator profiles, digit-equivariant inclusion squares, named sequence defects, digit-sum orbit-state formulas, and finite ghost-contraction behavior.

## Regression suites

- Block 03 periodic atlas: 39,805 checks, 0 failures
- Block 04 rational-mask atlas: 11,391 checks, 0 failures
- Block 05 regular atlas: 89,055 checks, 0 failures
- Block 06 integral and prime-power layer: 697,958 checks, 0 failures
- combined Block 03-06 record: 838,209 checks, 0 failures

All four verifier suites passed again after clean extraction of the source archive.

## LaTeX and PDF validation

Final manuscript:

- page count: 114
- page size: US letter, 612 by 792 points
- PDF outline entries: 100
- encryption: none
- forms, JavaScript, and XFA: none
- all listed fonts embedded
- unresolved references: 0
- undefined control sequences: 0
- multiply defined labels: 0
- overfull boxes: 0
- underfull boxes: 0
- PDF preflight: openable, non-scanned, non-encrypted, no XFA

The manuscript was rendered in full and visually inspected. The title pages, tables of contents, Block 06 theorem sequence, all three new figures, landscape tables, validation appendix, and closing concordance pages were inspected at page resolution.

## Clean source-package replay

The source tree was copied into a clean directory and validated independently.

1. The internal SHA-256 manifest passed for all 114 listed source files.
2. The Block 03, 04, 05, and 06 verifier suites all passed.
3. Common figures, Block 06 figures, generated tables, and proof-obligation components were regenerated.
4. `latexmk` rebuilt the 114-page manuscript successfully.
5. The rebuilt LaTeX log contained no warnings, unresolved references, overfull boxes, or underfull boxes.
6. Both PDFs were rendered with `pdftoppm` at 96 dpi.
7. All 114 corresponding rendered pages were pixel-identical.

The PDF byte streams are not claimed to be identical because TeX writes build-time metadata. The rendered mathematical and typographic output is identical page by page.

## Boundary

These results certify the declared finite computations, PDF build, source manifest, and clean package replay. They do not constitute external peer review and do not prove finite-data recognition, arbitrary-ring or semiring minimality, cross-radix compatibility, or an unrestricted equivalence between prime-power regular towers and local analytic Mahler interpolation.
