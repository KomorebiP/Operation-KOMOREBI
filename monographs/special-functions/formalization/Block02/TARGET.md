# SF-LEAN-B02: local analytic solution

Base: repository commit `cfff62cde8c8a5aac109fc84bf89c73b0e3daad1`,
Block01 `lean/CoupledFormal.lean`, Lean 4.34.0-rc2,
Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

The target is the local analytic part of Appendix F.1: the two sums of the
existing coefficient recurrence are complex differentiable on `norm(z)^2 < 2`,
can be differentiated term by term, have value zero at the origin, and satisfy
`U'(z) = 1 + U(q*z)*V(r*z)` and `V'(z) = 1 + U(a*z)*V(b*z)` there.
Parameters are labeled positive real numbers at most one. The coefficients
are ordinary Taylor coefficients of `z^(2*n+1)`, with initial pair `(1,1)`.
The target does not assert uniqueness among arbitrary analytic solutions,
entire continuation, the Perron growth law, or full monograph coverage.

Three candidate routes were considered:

1. Uniform convergence on smaller disks, then the complex Weierstrass theorem
   and its derivative-series theorem. The discriminating check is whether the
   existing geometric majorant supplies the exact local uniform hypothesis.
2. Repackage the odd sequence as a dense formal multilinear power series.
   This requires a sparse-to-dense correspondence before using the radius API.
3. Bound the derivative series directly by `(2*n+1)*rho^n` and use a real/complex
   smooth-series theorem. This requires a second summability estimate.

Route 1 is selected: it reuses the proved majorant and avoids an unnecessary
second coefficient representation. The product step will use the absolutely
convergent Cauchy product, with explicit exponent and recurrence identities.
The boundary case with all scales one is allowed for this local target;
it is a useful check against accidentally claiming entire continuation.

Completion requires successful warning-as-error compilation, exact theorem
axiom reports with no custom or placeholder axioms, and rejected negative
controls. Any compiler/environment change must be reported separately from
mathematical changes. Existing Block01 evidence is preserved.
