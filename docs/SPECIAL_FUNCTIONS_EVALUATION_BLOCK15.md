# Special Functions: exact evaluation certificates, Block15

SF-LEAN-B15 proves the registered Appendix J mathematical certificate for
strict positive contractions: a finite disk-majorant ladder bounds the actual
entire functions at any radius; adequate fuel always exists. For S>R>=0,
retaining odd indices 0 through N gives actual complex error at most
B(S)*(R/S)^(2N+3) throughout the closed disk of radius R. The real partial
polynomial and that error give an enclosure for every nonnegative real input.
For rational scales and rational target/outer radii, the Lean rational
coefficient, polynomial and majorant definitions cast to these canonical
quantities, so the enclosure has exact rational endpoints.

The unequal pair (1/5,2/5,3/5,7/10), R=1, S=2 and last index 30 has actual
complex error **below 1.6e-13** on the unit disk. Last index 30 retains
31 coefficients through degree 61, with first omitted degree 63.

There are **36 new theorem declarations**, for **405 registered names**.
All **60 fresh verification steps** pass across fifteen coupled modules:
366 theorem axiom audits, fifteen kernel replays, four expected rejections
and one positive fixture. The finite core's 39-name evidence is inherited;
Mathlib imports are cached. Review provenance is self-review.

The [report](../monographs/special-functions/formalization/Block15/REPORT.md),
[claim map](../monographs/special-functions/formalization/Block15/CLAIM_MAP.json),
[review](../monographs/special-functions/formalization/Block15/SELF_REVIEW.md),
[source](../monographs/special-functions/lean/CoupledEvaluation.lean),
[I/O inventory](../monographs/special-functions/formalization/Block15/IO_MANIFEST.json)
and [receipt](../monographs/special-functions/formalization/Block15/evidence/receipt.json)
bind the proof and replay. Formal I/O has 53 inputs, 61 packaged outputs,
fifteen generated objects and 35 staging copies. The separate remaining-work
assessment has 31 inputs and two outputs. Development diagnostics are labeled
separately from accepted proof evidence.

Replay `tools/verify_coupled_evaluation.py` with Lean 4.34.0-rc2,
Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06 and a new external work
directory. It installs nothing and makes no network request.
[Live continuation](../monographs/special-functions/CONTINUE_HERE.md) and
[remaining work](../monographs/special-functions/formalization/Block15/REMAINING_WORK.md)
give the exact next targets.

The existing Python program is **not yet proved to refine the Lean model**.
Next: factorial-normalized arrays and ordinary coefficient conversion, then
the guarded loop and exact returned endpoints. Other J normalization/degree
claims, ancillary F/H correspondence, I's resolution mechanisms and broad
A-E analytic development remain. Ordinary type convergence is conditional;
no whole-book coverage percentage is established. Earlier sources are preserved.
