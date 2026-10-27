# Development and route record

Base: `Euler-coupled-stationarity-20261005`.

The route attempted to use exact resummation, a moment representation, and
Euler moment determinants to force nonzero stationary residual values.

* Exact resummation succeeded: the residual is the quotient in equation (7)
  of `STRUCTURAL_MOMENT_ROUTE.md`, with one universal Euler interpolation
  and a finite source prefix.
* The natural moment construction succeeded as an analytic Volkenborn
  distribution. A bounded-measure replacement is impossible for these
  moments, as proved by the interior poles of its forced Amice transform.
* Orthogonal-polynomial/Hankel structure succeeded, but the proposed
  proportional remainder identity failed at r=1, N=1 and N=2. The two
  exact ratios are -2/3 and 2/105. This falsifies that particular dictionary,
  not Euler residual simplicity or every possible distribution argument.
* No proof excluding the exact simultaneous two-moment equations (11)
  was obtained. The source prefix has the same leading derivative units
  as the full interpolation, so their subtraction prevents the direct
  curvature-unit argument from closing the gap.

Two runner setup invocations failed before any scientific command ran.
The first used a contract path relative to the wrong directory. The second
revealed that the draft contract lacked the runner's `claim_id` and
`mathematics` fields. Both were corrected. The final bounded scientific
run completed successfully and its manifest validates. No mathematical
failure was hidden by those setup corrections.

The general arguments use only the checkpoint's Euler/Bernoulli conventions,
its coefficient bounds, and explicit formal identities proved in the note.
A discovery-only search located literature on Euler interpolation, but no
external interpolation, logarithmic-form, or Skolem theorem is used here.
No novelty claim is made for the classical Volkenborn and orthogonality
identities. No Lean compilation was performed.

The distribution route remains open only for a genuinely new identity or
estimate that acts on the exact prefix S_r in (11). Further checking of the
already-proved full moment determinant would not address this missing step.

The weighted convolution supplied by the parallel unit-identity route was
then translated with the actual cutoff intact. The exact half-shift operator
produced equation (9) of `WEIGHTED_TAIL_TRANSLATION.md`, including its
nonzero commutator term. This goes beyond identifying a mismatch between
ordinary differentiation and the Bernoulli coefficient weights: it gives
the precise extra analytic series required by the true operator.

The weighted cutoff and half-shift checks passed in `weighted_run`. The
original structural proof received two reviewer-requested typing
clarifications, and `certified_run_final` records the same exact finite
checks against those final proof bytes. The older `certified_run` is
historical and pins the pre-clarification note. Use `certified_run_final`
for current-source manifest validation.

The weighted route did not eliminate the separate series u_r(s-1/2).
The explicit g-tail controls lambda*u_r-v_r, while its half-shift
commutator retains u_r itself. No proof that this remaining term cannot
match the finite expression and its derivative at a stationary point
was obtained. The finite cross-boundary polynomial was retained throughout.
