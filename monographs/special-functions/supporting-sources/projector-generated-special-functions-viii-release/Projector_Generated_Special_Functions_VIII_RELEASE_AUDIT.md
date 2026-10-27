# Release audit

## Build

- Paper title: Projector-Generated Special Functions VIII
- Author: Komorebi P.
- PDF pages: 62
- Page size: US Letter
- Vector figures: 32
- PNG figures: 32
- Built-in checks: 23 of 23 passed
- Independent tests: 20 of 20 passed

## LaTeX

The final three-pass build completed without:

- overfull boxes
- underfull boxes
- undefined references
- duplicate labels
- duplicate page anchors

## PDF

The final PDF is openable and unencrypted. It is not image-only. All listed fonts are embedded.

The preflight reported no structural warning. The page scan found:

- no blank content pages
- no one-line content pages
- no extracted text outside page bounds
- no clipped figures in the reviewed renders
- no overlapping legends or colorbars in the reviewed renders

Every page was rendered at 180 DPI. The complete contact sheet and selected full-resolution pages were inspected.

## Source consistency

All 32 generated PDF figures are referenced once by the manuscript. No manuscript figure reference is missing from the figure directory.

The complete Python program has no external network dependency. It writes figures, numerical tables, checks, and the machine-readable manifest before LaTeX compilation.

## Claim boundary

The release distinguishes the classical q-Racah and Askey-Wilson theory from the packet architecture developed in the paper. It does not claim invention of the classical polynomial families. It does not claim a proof of the Riemann hypothesis.

## Independent clean rebuild

The source ZIP was extracted into a separate directory. The generator reported 32 figure pairs and 23 of 23 built-in checks. The independent suite reported 20 passed tests. Three LaTeX passes produced a 62-page PDF.

A page-by-page render comparison at 120 DPI reported:

```text
changed_pages: 0
pages_a: 62
pages_b: 62
```
