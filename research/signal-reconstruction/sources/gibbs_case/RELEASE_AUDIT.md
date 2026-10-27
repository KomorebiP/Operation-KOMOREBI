# Release audit

**Title:** Projector-Resolved Gibbs Reconstruction  
**Author:** Komorebi P.

## Mathematical scope

- One periodic signal is used throughout.
- Raw Fourier partial sums are derived exactly.
- The scaled Gibbs sine-integral profile is proved and checked numerically.
- Smooth and edge projectors are defined on a direct-sum model.
- The reconstruction operator is the identity on that model for `N >= 5`.
- The finite 96-sample interval search recovers the exact packet and amplitude.
- Perturbation, noise, off-grid, and runtime results remain labeled as computations.

## Computational results

- One Python file generates all figures, tables, numerical records, and tests.
- 26 of 26 checks pass.
- 60 vector-PDF figures and 60 matching PNG figures are generated.
- The recovered packet is `(start, length, amplitude) = (32, 32, 1)`.
- The objective gap is `0.7531607493634364`.
- The maximum reconstruction residual is `5.551115123125783e-16`.

## PDF and layout audit

- Final page count: 88.
- PDF opens successfully and is not encrypted.
- PDF preflight warnings: 0.
- LaTeX overfull boxes: 0.
- LaTeX underfull boxes: 0.
- Undefined references: 0.
- All fonts are embedded.
- All 88 pages were rendered at 180 DPI.
- A complete contact sheet and representative full-resolution pages were inspected.
- No clipped text, overlapping legends, misplaced colorbars, missing figures, or broken glyphs were found.
- No text block extends outside its page boundary.
- The visible PDF contains no semicolons.
- No page contains only one sentence or one isolated line.

## Editorial revision

- Figure pages and their explanatory notes were combined.
- Standalone part-title pages were replaced by compact part introductions.
- Chapter headings and the contents pages were tightened.
- Promotional and procedural wording was replaced by direct mathematical prose.
- The Python source was reformatted to one statement per line.

## Rebuild

A clean extraction regenerates the 60 figure pairs, all tables, all 26 checks, and the 88-page PDF with two `pdflatex` passes.
