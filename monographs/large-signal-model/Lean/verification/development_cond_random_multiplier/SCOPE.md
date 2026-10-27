P81 predictable random multiplier helper

ConditionalSubgaussian hm X σ μ consists of ambient measurability of X,
integrability of exp(h X) for each fixed real h, and the actual conditional
expectation bound μ[exp(h X)|m] ≤ exp(h²σ²/2), almost surely for each h separately.
There is no uniform almost-sure event over all real h in its fields.

For every m-measurable real a, the literal normalized factor
exp(a X − a²σ²/2) is proved integrable and its actual conditional expectation is
at most one. The coefficient may be unbounded. The proof handles finite-valued
simple coefficients using conditional-expectation linearity and indicators,
then applies nonnegative Fatou limits on every m-measurable event. The sample
space is arbitrary; no Standard Borel or conditional-distribution kernel
assumption occurs.

For every nonnegative m-measurable integrable weight W, weighted integrability
and the integral budget ∫W exp(aX−a²σ²/2) ≤ ∫W are derived. The nonnegativity
premise is pointwise, as holds for the actual exponential wealth used by P81.
Bounded W uses conditional-expectation pullout. Truncations min(W,n) and Fatou
remove the boundedness condition. The same inequality is proved on every
m-measurable event by indicator weighting. Weighted integrability is not an
input assumption.

This is the one-step transfer needed to build the exponential process. Gaussian
integration, matrix determinants, ridge algebra, Ville crossing bounds and the
full P81 confidence theorem belong to the consuming modules and are not claimed
by this helper alone.

The semantic control constructs genuine deterministic conditional subGaussian
bounds for a centered two-point observation, but chooses a coefficient after
seeing that same noise. Its normalized expected factor is exactly exp(1/2)>1,
so the proposed bound without predictability rejects actual False.

The checks here are individual development checks, not a cumulative release run.
