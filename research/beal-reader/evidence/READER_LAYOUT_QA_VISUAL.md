# Reader layout QA: visual reviewer

Result: **passed** for physical pages **13–24** of the 48-page reader.

PDF: `pdf/Komorebi_Beal_Conjecture_Piece_v1.0.pdf`  
PDF SHA256: `3b1911d594d7c68bdfccc5d4788d4a6a33df1ce968ea226ca053f020c0b03ebf`

All twelve supplied page PNGs were opened and inspected individually at full resolution. The review covered label readability, mathematical displays, equation numbering, wrapping, tables, margins, clipping, and page endings. No presentation correction is requested. This is a layout review; it does not replace the separate mathematical and literature audits. Reader sources and figures were not changed.

## Page observations

- Physical page 13: Discriminant proof, equations 5.1–5.3, and ending paragraph fit cleanly.
- Physical page 14: Cartier matrix and irreducibility prose are readable; final sentence continues naturally on page 15.
- Physical page 15: The continuation resolves before Chapter 6; polynomial formulas and ending paragraph fit.
- Physical page 16: Chapter 7 heading, coefficient-ring display, and exact sequence are contained; subsection ending is readable.
- Physical page 17: Final norm-four/place-two clarification and the residue set and projector/depth displays fit; the subsection ends with a complete sentence. Reinspected after the final rebuild.
- Physical page 18: Local-depth matrices and equations 7.2–7.3 fit; no equation-number collision or clipped proof text.
- Physical page 19: Cup-endpoint prose and Chapter 8 displays fit; Lemma 8.1 begins coherently and continues on page 20.
- Physical page 20: Lemma continuation and proof are readable; marked-period equations at the page ending fit.
- Physical page 21: Period matrix, torsion exact sequence, and criterion 9.2 are readable and contained.
- Physical page 22: Chapter 10 sums and Frobenius matrix fit; subsection heading has supporting text and display.
- Physical page 23: Trace and norm fractions and coefficient normalization fit; final paragraph completes cleanly.
- Physical page 24: Eight-pattern support/inertia table is readable and contained; primewise bound wording and subsection ending fit.

The reviewed range has mathematical displays and one support/inertia table, rather than an embedded standalone figure. Table entries, field symbols, primes, exponents, and equation numbers remain legible. No text intersects a footer or leaves the page. Normal continuations across pages 14–15 and 19–20 do not lose text.

## Render pins

Images are `tmp/pdfs/beal_qa/paper/page-XX.png`. These hashes pin the rendered pages actually inspected.

| Physical page | Pixels | SHA256 | Review |
| --- | --- | --- | --- |
| 13 | 849 × 1200 | `0876d67a6d2ae7c8be9b95fad5dce10bd14c0c5fc759ac36645faf64a501a6f4` | Passed |
| 14 | 849 × 1200 | `10a4a096c664e02b37b8c1324f1517b95ce7ade134b82cfca685b4412e554b7e` | Passed |
| 15 | 849 × 1200 | `4279d3494cdc09efb88ca2508fdd8803062b1e56366ad4ac86426873e7e9000b` | Passed |
| 16 | 849 × 1200 | `f1d512378b71b4f3ec1798f852a0a5d2fd1b14af6c03c991fe3b670aebc77a04` | Passed |
| 17 | 849 × 1200 | `cf80e411ceb3d7f5d499bbb70dd79787c7ce077b21de699c0fad863a6b642d3e` | Passed |
| 18 | 849 × 1200 | `a98d8da1bd3565ef8dd96656cf4b8bf9cb1bf5953a2d9e4cf78344a3d0818473` | Passed |
| 19 | 849 × 1200 | `1f54b73d74a03e71526719171771d22f36afd00b040e3d60b5923cbabcdffdd8` | Passed |
| 20 | 849 × 1200 | `88d2a53e5c5aa19d67a9ae0ea1611a4b202ea74979abac3fcb0ed8c4b5ab9ead` | Passed |
| 21 | 849 × 1200 | `7855f82b4557a308df9b0cd1b9b374a17aa66e215364418f3562c48c73d2a9f7` | Passed |
| 22 | 849 × 1200 | `c2df12ecec4c08114cf5a9084f9d7e69e5ce54cca59792bd820d0a8d636cc7fe` | Passed |
| 23 | 849 × 1200 | `12dc53885dd3a789fd08a3ed72ac2e6a1d4e690281a838d3aaf5e09f81f8487d` | Passed |
| 24 | 849 × 1200 | `590e555bbc1a517ffb697ebede59e63c1d48b040eb547a7d8ad379aaad7f3c87` | Passed |

## Final revision comparison

The original twelve-page inspection was against PDF SHA256 `ab301499c5ffaacfb65a8c5b53204a8f456491003df8b7e768cd7c6102b68bf4`. The final 48-page reader has the PDF hash pinned above. Its final page images were compared with every original render pin. Physical pages 13–16 and 18–24 have identical PNG hashes, so their full-resolution acceptance carries forward without a source-based assumption. Only physical page 17 changed; its final PNG was reopened and inspected at full resolution, and passed. Its displayed clarification mentions residue norms four, nine, and five and fits without reflow into other reviewed pages.

Previous physical page 17 PNG SHA256: `e3a6310199f77fd36b101336e2e92437a01b028c3a2efaa5059d4de258597862`  
Final physical page 17 PNG SHA256: `cf80e411ceb3d7f5d499bbb70dd79787c7ce077b21de699c0fad863a6b642d3e`

All twelve rows above now pin the final rendered images. This record accepts physical pages 13–24 of the final frozen reader for layout. No reader source or figure was changed by this review.
