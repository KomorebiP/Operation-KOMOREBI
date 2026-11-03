# SF-LEAN-B15 target contract

Base: `f5b2651f182244afd4d979d9aed386e45c898381` (published Block14).
Authority: Appendix J, `monograph/sections_v11/coupled_lab_full.tex`,
lines 44-87. All four real scales lie strictly between zero and one.

Prove the arbitrary-radius mathematical evaluation certificate for the
actual canonical entire functions: the positive-real max recurrence,
finite contraction ladder with terminal seed x/(1-x^2), actual complex
Taylor remainder bounded by B(S)*(R/S)^(2N+3) on |z|<=R for S>R>=0,
and real enclosure [F_N(x),F_N(x)+tail] for x>=0. F_N retains ordinary
odd coefficients with indices 0 through N. Include zero radius/input.

Add an exact rational fuel-indexed majorant and prove its real interpretation
sound when its terminal-radius condition holds, with existence of adequate
fuel for every nonnegative radius under strict contraction. Keep the numerical
certificate separate from the source's Python while loop, factorial-normalized
derivative generator, resource guards and returned dictionary. Mathematical
soundness is not by itself end-to-end Python refinement; retain that obligation.

Primary route: existing real_axis_full_upper + monotonicity -> scalar max
recurrence -> finite majorant induction; positive coefficient series at S
and finite-prefix/tail splitting -> outer-radius term comparison -> actual
remainder and enclosure. First discriminators: the zero-radius case, a radius
above the local disk and the inclusive-index exponent 2N+3.

Alternative outer-tail route: Cauchy estimates from an outer-disk supremum.
Defer if the positive-term route closes the contract; resume for signed or
complex coefficient regimes. Its ordinary Cauchy geometric denominator
would be weaker than the source's positive-series certificate. Alternative
majorant route: reuse the geometric ladder seeded at radius one from F.2.
Defer because its seed differs from the exact rational Python formula; resume
for bounds where matching that formula is unnecessary. Test invalid outer
radii and missing terminal conditions rather than silently weakening guards.

Preserve earlier blocks, source editions, PDFs and receipts. No unconditional
type convergence or whole-monograph completion is claimed. Review is self-review;
no delegation is authorized. Update exact I/O, status, GitHub and .io after replay.
