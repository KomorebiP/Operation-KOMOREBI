# Sequence interface and mathematical proofreading audit

Author: Komorebi P.
Date: 19 November 2026.

## Scope

This change continues the exact differential Hankel calculator and reviews
the Sequence Library calculator, the Closed Forms entry points, the full
differential proof reader, and the two polynomial/differential Hankel notes.
It does not represent a whole-site accessibility certification, a screen
reader compatibility study, or a new mathematical theorem.

## Correctness and usability findings

- Editing fields previously left old result rows and exports active while a
  copied link used the new field values. Results are now invalidated on edit,
  and all exports use the completed calculation's parameters.
- The moment and determinant views had separate coefficient inputs despite
  describing the same family. Their coefficients now stay synchronized.
- Errors were only reported in a general status line. Invalid fields now
  have associated explanations, and submission focuses the first invalid
  input. Hidden parameter groups are disabled.
- The direct browser determinant limit was 12. The exact Chebyshev–Schur
  implementation computes prefixes through size 64, with windows of up to
  32 values. Larger calculations run in a cancellable module worker.
- Method and formula details preceded or competed with the requested values.
  The table and exports now come first, with optional details below them.
- The mathematical reader left inline TeX unprocessed and escaped Bash code
  fences appeared as prose. Inline math now reaches the site's accessible
  MathJax runtime, and reproduction commands render as a focusable code block.
- A section outline, responsive formula containers, stable table headers,
  visible focus, and clearer table/status names improve navigation.
- The research card still described 24 records and six constructions. Counts
  now come from the same catalogue used by the collection page.
- The downloadable source bundle omitted JavaScript dependencies required by
  its cross-language test. Those modules are included and the production
  worker/import chain receives revision hashes.

## Mathematical proofreading

Reviewed `FINITE_DIFFERENTIAL_HANKEL.md`, `POLYNOMIAL_HANKEL_STRUCTURE.md`,
and the related passages in `SEQUENCE_LIBRARY.md`.

Routine edits repaired code fences, clarified prose, corrected construction
counts, distinguished formula copying from CSV contents, and updated the
documented implementation limits.

Meaning-sensitive notation and terminology changes were:

1. Defined the falling-factorial functional `F_d` explicitly in both notes.
2. Defined `D` and `r` as nonnegative degree/order bounds so zero inputs are
   meaningful. The positivity asymptotic explicitly takes `D = deg P`.
3. Restricted the coefficient identity for the iterated generating-function
   operator to `n >= k`, and stated that coefficients vanish for `n < k`.
   This avoids applying a polynomial functional to a negative monomial.
4. Corrected “separated block column” to “separated block row” in both rank
   proofs, matching the displayed span in the column coordinate.
5. Corrected “first nonzero Hankel matrix” to “first nonsingular leading Hankel
   matrix.” Earlier matrices can contain nonzero entries.
6. Renamed the unrelated auxiliary functional in the polynomial note's
   Theorem A proof from `F_s` to `mathcal F_s` to avoid colliding with `F_d`.

No determinant formula, coefficient, sign, recurrence formula, or proof route
was replaced. Independent source review of the new numerical implementation
found no numerical defect in the reviewed paths. It did find and correct an
overbroad verification message: the UI now states the actual direct-check
endpoint, the smaller of the last requested size and 12.

## Verification record

The mathematical regression checks include 546 direct comparisons through
size 12, 12 larger full-matrix comparisons at sizes 13, 24, 40, and 64, and
377 exact values compared between the independent Python and JavaScript
structured solvers. Zero weights/operators, empty coefficient arrays,
initial zero blocks, interior singular minors, repeated odd singular pivots,
and simultaneous reversal of odd derivative coefficients are included.

The proof reader regression checks preserve all 39 source display equations,
check inline mathematical markup, verify the seven outline targets, and
require the actual Bash block to render. Production builds preserve the
2,327 records and 7,108 formula representations.

The focused browser audit records its results and screenshots in the existing
Sequence Library checks artifact. It covers desktop and phone widths,
keyboard operation, error focus, stale-result handling, coefficient transfer,
large exact values, worker cancellation, clipboard fallback, mathematical
rendering, display preferences, and text contrast. See the workflow run for
the exact tested revision and pass/fail result.

Local Chromium could not launch because the execution workspace denied its
socket operation. Rendered checks therefore run in the repository's browser
CI; this limitation is not treated as a passing local browser test.
