# Coupled-function browser laboratory

This record checks the bounded exact rational model used by
`special-functions-lab.html`. It adds no manuscript or Lean coverage.

## Mathematical contract

The two ordinary odd coefficient lists begin with `u[0] = v[0] = 1`.
For `n >= 1`, each new coefficient is the sum over `i+j=n-1` of the
shared earlier product `u[i]*v[j]`, multiplied by the appropriate odd
powers of the equation's two scales, divided by `2*n+1`.

The browser admits positive rational scales strictly below one, denominators
at most 100, one to sixteen retained coefficients, and rational disk radius
zero to 4/3. If `N` coefficients are retained, the first omitted index is `N`.
The exact local envelope is `R*(R*R/2)**N/(1-R*R/2)`. Decimal plots round the
finite polynomials and have additional floating-point error.

The source formulas are in the coupled-contractions chapter,
`monographs/special-functions/monograph/sections_v11/coupled_visual.tex`.
The coefficient bound and local tail statement are recorded in
`monographs/special-functions/lean/CoupledFormal.lean`, notably
`coefficients_le_geometric` and `odd_series_tail_bound`.

## Independent finite check

Run with Python and Node.js on PATH:

```text
python -B tools/audit_special_functions_lab.py
python -B -m unittest discover -s tools -p test_special_functions_lab.py -v
```

Use `--node /path/to/node` when Node.js is not on PATH. The audit extracts every
dense Taylor coefficient, including even degrees, using Python `Fraction`.
It compares the browser recurrence against this independent construction over
the complete 81-case three-value parameter grid and four explicit extra cases.
Additional controls check the all-half hyperbolic-sine identity, component
swap, exact evaluation, recurrence contribution sums, local envelope indexing,
malformed inputs, huge-fraction decimal conversion, CSV and shared-state round trips.

The bounded runner's `run-2026-11-10/manifest.json` binds the executed inputs,
environment, command and result. Read its status together with the finite
assertions in `result.json`; a valid manifest alone is not mathematical proof.

## Self-review

The new page's defining equations, ordinary-coefficient normalization,
retained-count convention, recurrence, geometric envelope, source links and
closed-form exercise were checked against the named sources. The finite code
audit is independent of the plot renderer. Browser accessibility and layout
checks are recorded separately by the publication task.

Historical comparison: the original research evaluator uses a *last index*,
so `last=N` retains `N+1` coefficients and has first omitted degree `2N+3`.
This page consistently uses retained count and first omitted degree `2N+1`.
