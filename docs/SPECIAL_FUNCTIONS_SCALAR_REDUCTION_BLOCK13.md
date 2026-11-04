# Special Functions: scalar reductions and local certificates, Block13

SF-LEAN-B13 proves actual global U=V exactly when the unordered scale rows
coincide. At q=r=a=b=1/2 the canonical pair is exactly
sqrt(2) sinh(z/sqrt(2)), with growth order one. The unequal example
(1/5,2/5,3/5,7/10) has order one, explicit coefficients through degree seven,
type ratio two and explicit positive-real lower bounds. Characteristic order
is invariant under fixed q,b,ar; a strict-budget parameter construction realizes
each admissible prescribed positive order. Actual complex truncation error is
bounded for |z|^2<2. The example's printed degree-seven polynomials have error
at most |z|^9/8 on the closed unit disk.

There are **43 new theorem declarations**, for **342 registered names**.
All **54 fresh verification steps** pass across thirteen coupled modules:
303 theorem axiom audits, thirteen kernel replays, four expected rejections
and one positive fixture. The finite core's 39-name evidence is inherited;
pinned Mathlib is cached, not freshly rebuilt/replayed. Review is self-review.

The [report](../monographs/special-functions/formalization/Block13/REPORT.md),
[claim map](../monographs/special-functions/formalization/Block13/CLAIM_MAP.json),
[review](../monographs/special-functions/formalization/Block13/SELF_REVIEW.md),
[source](../monographs/special-functions/lean/CoupledScalarReduction.lean),
[I/O inventory](../monographs/special-functions/formalization/Block13/IO_MANIFEST.json)
and [receipt](../monographs/special-functions/formalization/Block13/evidence/receipt.json)
bind the exact proof and replay. Formal I/O has 47 inputs, 55 packaged outputs,
thirteen generated objects and 31 staging copies. The separate source-based
remaining-work assessment has 23 inputs and two outputs.

Replay `tools/verify_coupled_scalar_reduction.py` under Special Functions with
Lean 4.34.0-rc2, Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06 and
a new external work directory. The verifier installs nothing and makes no
network request. [Live continuation](../monographs/special-functions/CONTINUE_HERE.md)
and [remaining work](../monographs/special-functions/formalization/Block13/REMAINING_WORK.md)
retain exact next targets and boundaries.

Next major target: H.1 autonomous projections and operator decoupling.
Some ancillary explanatory F correspondence, I-J analytic resolution and
arbitrary-radius evaluator/Python refinement, and broad A-E analytic coverage
remain. Ordinary type convergence is conditional. No exhaustive whole-book
map or completion percentage is established. Earlier sources and evidence
retain their bytes.
