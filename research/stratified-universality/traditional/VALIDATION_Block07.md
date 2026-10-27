# Block 07 validation record

## Mathematical verifier

Command:

```powershell
python .\verify_block07_product_multiplicative.py
```

Recorded result:

- Euler exponent prefixes: 15,625
- arbitrary integral unit-series prefixes: 3,125
- multiplicative local systems: 96
- Dirichlet-convolution pairs: 48
- multiplicative divisor-ghost systems: 128
- power families: 6
- named arithmetic families: 5
- geometric necklace modes: 6
- total exact checks: 595,964
- failures: 0
- status: PASS

The verifier checks Euler exponent/coefficient/ghost round trips, the product group law, ghost additivity, Mobius divisibility, prime-power reconstruction, local Euler inversion, valuation logarithmic derivatives, Dirichlet convolution, local Cauchy multiplication, beta and gamma additivity, multiplicative residue packets, divisor-ghost inversion, multiplicativity preservation, prime-power formulas, and named local families.

## Regression suites

- Block 03 periodic atlas: 39,805 checks, 0 failures
- Block 04 rational-mask atlas: 11,391 checks, 0 failures
- Block 05 regular atlas: 89,055 checks, 0 failures
- Block 06 integral and prime-power layer: 697,958 checks, 0 failures
- Block 07 product and multiplicative layer: 595,964 checks, 0 failures
- combined Block 03-07 record: 1,434,173 checks, 0 failures

## LaTeX and PDF validation

Final manuscript:

- page count: 127
- page size: US letter, 612 by 792 points
- PDF outline entries: 110
- encryption: none
- forms, JavaScript, and XFA: none
- all listed fonts embedded
- unresolved references: 0
- undefined control sequences: 0
- multiply defined labels: 0
- overfull boxes: 0
- underfull boxes: 0
- PDF preflight: openable, non-scanned, non-encrypted, no XFA

The manuscript was rendered in full with PDFium and visually inspected. The title page, abstract, table of contents, complete Block 07 theorem sequence, all four new figures, the named-family table, the exact-validation table, the proof-obligation ledger, conclusion, and appendices were inspected at page resolution.

## Clean source-package replay

The finalized source tree contains 132 files including `MANIFEST.sha256`, whose 131 recorded entries all passed `sha256sum -c` before replay. The package was copied to a clean working directory and rebuilt from its recorded source and generated-data inputs.

The replay completed the following operations successfully:

1. verified the complete internal SHA-256 manifest
2. replayed all five Block 03-07 verifier suites with the exact counts recorded above
3. regenerated the common figures and the Block 06 and Block 07 figure sets
4. regenerated the concordance and proof-obligation components
5. removed the packaged PDF and LaTeX auxiliaries and performed a clean `latexmk` compilation
6. produced a 127-page US-letter PDF with zero LaTeX warning, underfull, overfull, unresolved-reference, undefined-control-sequence, or multiply-defined-label lines
7. passed PDF inspection with 110 outline entries, zero forms, zero attachments, zero encryption, and all listed fonts embedded
8. rendered both the packaged and rebuilt PDFs at 96 dpi with PDFium and compared them page by page

The rendered comparison reported:

- packaged pages: 127
- rebuilt pages: 127
- changed pages: 0
- maximum changed-pixel fraction: 0

The rebuilt PDF is therefore visually identical to the packaged PDF. The PDF byte streams are not asserted to be identical because TeX compilation metadata can contain build timestamps.

## Boundary

These results certify the declared exact computations, document build, package integrity, and replay procedure. They do not constitute external peer review and do not prove finite structural complexity for arbitrary Euler exponent arrays, minimality across arbitrary product grammars, prime-power completeness without multiplicativity, or an unrestricted algebra equivalence between Cauchy and Dirichlet convolution.
