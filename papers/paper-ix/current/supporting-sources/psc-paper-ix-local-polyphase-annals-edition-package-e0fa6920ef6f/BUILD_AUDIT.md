# Build audit

## Final build

| Item | Result |
|---|---:|
| PDF pages | 52 |
| PDF openable | Yes |
| PDF encrypted | No |
| Searchable text | Yes |
| Fonts embedded | Yes |
| Type 3 fonts | None |
| Raster images in manuscript | None |
| Referenced vector figures | 14 |
| Overfull boxes | 0 |
| Underfull horizontal warnings | 8 |
| Undefined references | 0 |
| Undefined citations | 0 |
| Clean rebuild changed pages | 0 of 52 |

The eight underfull horizontal warnings arise from the strict suppression of word hyphenation and do not produce visible overlap or clipping. The installed `aomart` class emits one harmless warning through `cmtiup` and one notice concerning repeated bibliography authors.

## Visual review

All 52 pages were rendered at 150 dots per inch and inspected in six contact sheets. Pages containing the local comparison table, dyadic interpolation, the affine Mahler kernel, the final boundary table, and the bibliography were also inspected individually.

## Reproducibility

A clean directory containing only the LaTeX source, BibTeX database, and figure PDFs rebuilt to 52 pages. Pixel comparison at 120 dots per inch found zero changed pages.
