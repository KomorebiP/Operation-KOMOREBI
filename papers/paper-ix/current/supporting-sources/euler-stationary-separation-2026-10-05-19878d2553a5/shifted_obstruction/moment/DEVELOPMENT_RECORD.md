# Shifted-moment route record

Base: `Euler-arithmetic-nonvanishing-20261005`, immutable archive SHA256
`15e1f9114380e180adcf4f7306d894100d6fd499929ee7a841d8629bd27e7464`.

The continuation attacked the actual shifted Bernoulli series and its
derivative. Reflection was derived with the finite cutoff intact. Unit-3
regularization supplies a bounded full Euler measure, so the first uncertain
implication tested was transfer of that measure norm to the actual residual.
That inequality failed at six exact rational examples retained in the run.

The pole proof then showed why the failure is structural for any finite odd
scalar dilation multiplier. This is a theorem about that filter class, not
about arbitrary analytic or differential methods.

The concrete polynomial D(s)=(s+1)(2s+1) was also tried because it preserves
multiplicity on the current chart and clears the source denominator. It
destroys boundedness on the full Euler side. The exact filtered Amice
coefficient valuation 3-2k at degree2^k, k>=2, was proved and checked through
degree256; an independent Euler-moment path checked degrees0..32.

No critical-value nonvanishing theorem was obtained. The surviving task is
a strict value/derivative estimate for the actual finite-prefix distribution,
or a new multiplicity-preserving operation outside the filter classes
examined here. No low-jet mismatch is asserted: the parent continuation
shows that the actual prefix inherits the full Euler derivative units through
the relevant finite range.

The authoritative computation record is `frozen_run/manifest.json`. It pins
the final proof and checker and passes current-source hash validation.
`certified_run` and `certified_run_final` are historical runs from before the
finite-dilation and polynomial-filter extension; their source hashes are
intentionally not the final source hashes.

One prose patch invocation failed before applying changes because its
unrelated trailing context contained a misspelling. The patch was corrected
and applied. No scientific computation failed, and no theorem was changed
to hide an inconsistent result. The failed strict inequality is preserved
as an explicit mathematical counterexample to the proposed estimate.

No external theorem is used beyond the standard analytic moment framework
already constructed in the base. No Lean compilation was performed.
