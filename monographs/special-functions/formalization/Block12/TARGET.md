# SF-LEAN-B12 target contract

Base: `c6c529a58b70ebdedac1d0a7dc232153688735b3`, the clean merge of
SF-LEAN-B11 with GitHub main `85cfa6f01fe7f820e7a957c9df0c5bed39efc7c7`.
Authority: Theorem F.3 in `monograph/sections_v11/coupled_growth_full.tex`,
lines 354-422. Preserve the actual real lower/upper type definitions and
the maximum-modulus identification from Block11.

For every positive strict contraction quadruple, prove that the lower and
upper type vectors are positive scalar multiples of the max-normalized
characteristic right eigenvector, with the lower scalar at most the upper.
Prove both explicit component-ratio identities and equivalence of existence
of the two ordinary type limits. If the limits exist, identify the vector.
No unconditional existence of ordinary type limits is claimed.

Primary route: transport eventual lower/upper envelopes through p(R-c),
prove the power factor tends to p^rho and logarithmic corrections vanish,
and take epsilon to zero. Obtain the two matrix inequalities from the
proved canonical real recurrences. Use the positive left eigenvector to
force equality coordinatewise, then explicit two-dimensional algebra to
classify the fixed space. The discriminator is transport without assuming
type convergence, while supplying real boundedness explicitly.

Alternative exact-transport route: prove equalities for the scaled real
liminf/limsup and invoke sum inequalities. First uncertainty: bounded
variable-factor transport in the cached library. Defer if envelope
comparisons suffice; resume for reusable exact transport identities.

Alternative cluster-point route: transport extremal cluster points through
the recurrence. First uncertainty: simultaneous two-component accumulation
points need not realize both individual extrema. Do not assume they do.
Defer unless an independent compactness argument is needed.

Controls must reject absent boundedness, a nonpositive left weight,
unconditional type convergence inferred from proportional extrema, and
placeholders. Positive interfaces must exercise the actual canonical pair.
Record inputs, outputs, rejected attempts, review provenance and remaining
work. Update the catalogue and GitHub/Pages publication from tested sources.
Review provenance is self-review; no delegation is authorized.
