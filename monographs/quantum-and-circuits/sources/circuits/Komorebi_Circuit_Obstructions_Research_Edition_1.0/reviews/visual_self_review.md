# Visual companion: final mathematical proofreading and PDF review

Date: 2026-10-07. Source baseline: immutable v1.2.0.

## Delivered scope

`manuscripts/visual.tex` builds the complete visual guide at
`output/Komorebi_Circuit_Obstructions_Visual_Guide.pdf`: 27 physical pages,
comprising an unnumbered cover and 26 numbered pages. Twelve precise figures
are supplied in PDF and PNG formats. `scripts/make_figures.py` reproduces
them and asserts the exact fixtures in `reviews/visual_examples.json`.

The guide covers the original eight claim groups through source definitions,
explicit hypotheses, computations and limits. It preserves the distinction
between written proof, archived formal result, fresh finite evidence,
counterexample, and conditional algorithmic implication.

## Conservative mathematical self-review

Mode: self-review of the newly authored guide only. The proofread-math skill
and its checklist were read. Source mathematical files were not edited.

- Routine edits: line-breakable source paths, clean evidence paragraphs,
  corrected an obsolete review-report path, and adjusted the guide's reading
  route to its actual numbered pages.
- Mathematical-token changes to pre-existing source: none.
- New-notation clarification: weighted own-block traces are explicitly
  defined as finite weighted sums and distinguished from top-coefficient
  extraction before the disjoint-factorization example.
- Domains reviewed: both initial target values; legal distinct-wire gates;
  finite Boolean quotient; positive v and d>=0 in the dual; nonzero monotone
  minterm statements; actual n in projection; fixed faithful linear
  multiplicative maps over a field; m=0 scalar boundary; efficient-field and
  exact-evaluator hypotheses in the randomized implication.
- Figure/prose alignment: AND compute/copy/uncompute is labeled a two-Toffoli
  restoration fixture, not the optimal AND2 oracle; the direct optimum is one.
  Full projection total-gate counts are construction upper bounds, while the
  Toffoli formulas have written optimality proofs. Trace coefficient-extraction
  finite scope is narrower than the complete GF16 evaluation scope at m=3.
- Unresolved mathematical/notation issues: none found in this authored guide.
- Review limitation: model-assisted self-review and another agent's source
  reading share possible errors and are not independent human refereeing.

## Exact fixture verification

All 12 figure pairs regenerated successfully after the final layout repairs.

- Unbalanced OR F3: all 32 assignments and all 64 affine masks checked;
  alpha=2, beta=3, alphaStar=3, betaStar=4, 11 positive points.
- AND2 evaluation dependence: positive degree-one row equals the XOR of the
  three negative rows, with constant coordinate included.
- Shared-degree fixture: actual coordinate maxima 1,2,2,4 across three legal
  Toffolis; product of two registers after two operations has exact degree 4.
- Small restored constructions: all 276 functions through three inputs,
  both target branches and 4,240 input/target cases checked. Distribution
  28 zero-Toffoli, 120 one-Toffoli, 128 three-Toffoli functions.
- Projection constructors m=2..10: exact gate counts asserted against the
  source. At m=10, n=1022, full T=17, CNOT=10220, total=10237; quadratic
  T=total=511. No large full truth-table search is implied.
- Unsafe projection m=3: all 64 inputs checked, 24 false positives; first
  assignment index13 is [1,0,1,1,0,0] in source label order1..6, L=[0,1,1],
  P=0, Q=1.
- Weighted fixture: accepted indices1,2,5,6 give four distinct monomials
  although ordinary parity is zero.
- GF16 overlap: z=theta encoded2, trace intersection0 versus product2;
  trace Boolean square2 versus square of trace4. Field arithmetic is exact.

The independent core dual check remains separately recorded: all 278 functions
on n=0..3, all positives and d=0..n, 4,201 primal/dual checks.

## Visual repairs and latest rendering

An independent agent inspected the figure previews and requested three fixes:
small-bar labels, idempotent label alignment, and an overlong unsafe-table
cell. Those repairs were applied in the generator and all figures regenerated.
A second inspection found the new small-count annotation colliding with its
legend; the annotation was moved to the empty middle-left chart region.
The final physical page15 was rendered at110dpi and directly inspected:
the legend, tiny segments, counts and caption are clear and separated.

All 27 final PDF pages were rendered at90dpi under
`build/visual/rendered/`; all page layouts were reviewed through contact
sheets, with full-page checks of the mathematical dual and GF16 pages and
full-resolution previews of the repaired figures. The final PDF is consistent
in margins, headers, footers, caption alignment and page numbering. There are
no clipped equations, overlapping table cells, unreadable figure labels,
missing glyphs or overflow into the margins in the inspected pages.

Two final pdflatex passes succeed. `build/visual/visual.log` contains no
overfull or underfull boxes, warnings, undefined references, or duplicate
page-anchor warnings. `pdffonts` lists every font as embedded. Exact text-bound
checks on every page stay inside the specified review margins. The final
digest and check results are in `reviews/visual_pdf_checks.json`.

## Reproduction

From the publication root:

```sh
python scripts/make_figures.py
python scripts/core_dual_checks.py --output reviews/core_dual_checks.json
```

Build `manuscripts/visual.tex` with pdflatex from the manuscripts directory,
using two passes and the shared `common.tex`. The publication build script
places the named output PDF and retains the build logs. Source checks and
PDF compilation are different validation layers; no fresh Lean rebuild is
claimed here.
