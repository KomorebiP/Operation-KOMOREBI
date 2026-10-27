# Block 15 validation record

Date: 2026-08-31  
Release: v1.15.0

## Mathematical audit

- Two-pass independent proof audit completed.
- Final verdict: no mathematical or typing release blockers.
- Controlling theorem source SHA-256:
  `c1ae8aa2472eda9df467bbbf20b3c861f1261333364af06ffaf1cd455b5ab026`.

The audit specifically checked finite address typing, fold-map domains,
resolution-change functors, polynomial degree-zero data, characteristic-zero
requirements, the additive/multiplicative factorial distinction, exact tree
support, Mahler coefficient targets, Galois projectors, address holonomy, and
kernel descent.

## Exact implementation regression

- Seed: `20260831`
- Status: `PASS`
- Assertions: `197,099`
- Failures: `0`

Category totals:

| Family | Assertions |
|---|---:|
| Integer/unimodular lane transport | 28,490 |
| Dense rational three-level refinement | 16,674 |
| Abstract folds and strict selectors | 1,000 |
| Actual-support loss decomposition | 300 |
| Factorial and residue-lane realization | 150,630 |
| Deliberately invalid negative controls | 5 |

The category sum, expected-category sum, observed total, and expected total
are all independently reconciled by the publication audit.

## Publication-source audit

- Status: `PASS`
- Checks: `77`
- Failures: `0`
- Abstract: 316 words
- Source graph: 55 TeX files
- Labels: 519
- Cross-references: 131
- Citation keys: 14
- Graphics: 57
- Concordance: 56 rows, including Foundations row FND-16

## PDF build and visual inspection

- Final pages: 235
- Page size: US Letter
- Delivered release PDF SHA-256:
  `0889b03d18a5029cbdbdd2d9da5aec7cc76a54019caaaf95a05e926bddbc0d60`
- Final LaTeX log: zero overfull boxes, underfull boxes, undefined references,
  undefined citations, multiply defined labels, rerun warnings, or fatal
  errors.
- Embedded-font inspection completed.
- All 235 pages were rendered to contact sheets and inspected.
- High-resolution inspection covered the title page, theorem opening, main
  transport theorem, exact-loss sequence, factorial/residue realization,
  factorial genealogy, descent theorem and kernel clause, validation/result
  page, scope transition, and final references page.

The source gates ran in the recovered workspace. Because that mounted scratch
directory truncated the large LaTeX auxiliary file between passes, final TeX
compilation was performed from a byte-identical isolated copy of the audited
tree; the resulting PDF and final log were copied back unchanged.

These records are internal proof, implementation, source-integrity, and layout
checks. They are not independent peer review or a historical-priority study.

